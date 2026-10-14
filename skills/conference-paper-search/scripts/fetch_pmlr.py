#!/usr/bin/env python3
"""Fetch one official PMLR proceedings volume; no model API or dependencies.

The default is every paper parsed from the supplied volume, not every paper at
the conference. --limit is a deliberate first-N sample for testing only.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


HOST = "proceedings.mlr.press"
TIMEOUT = 25
ATTEMPTS = 3
MAX_BYTES = 12 * 1024 * 1024
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Node:
    def __init__(self, tag: str, attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children: list[Node | str] = []

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def text(self) -> str:
        parts = []
        for child in self.children:
            if isinstance(child, Node):
                content = child.text()
                if child.tag in {"p", "div", "br", "li"}:
                    content = "\n" + content + "\n"
                parts.append(content)
            else:
                parts.append(child)
        return "".join(parts)

    def has_class(self, value: str) -> bool:
        return value in (self.attrs.get("class") or "").split()


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def clean(text: str) -> str:
    return " ".join(text.split())


def parse_html(html: str) -> Node:
    parser = PageParser()
    parser.feed(html)
    parser.close()
    return parser.root


def validate_volume_url(url: str) -> tuple[str, str]:
    """Return canonical volume URL and volume, rejecting lookalike domains."""
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc.lower() != HOST or parts.query or parts.fragment:
        raise ValueError("volume URL must use https://proceedings.mlr.press without query or fragment")
    match = re.fullmatch(r"/v([0-9]+)(?:/|/index\.html)?", parts.path)
    if not match:
        raise ValueError("volume URL must identify a PMLR volume, for example https://proceedings.mlr.press/v235/")
    volume = match.group(1)
    return f"https://{HOST}/v{volume}/", volume


def is_detail_url(url: str, volume: str) -> bool:
    parts = urlsplit(url)
    return (parts.scheme == "https" and parts.netloc.lower() == HOST
            and not parts.query and not parts.fragment
            and re.fullmatch(rf"/v{re.escape(volume)}/[A-Za-z0-9_-]+\.html", parts.path) is not None
            and not parts.path.endswith("/index.html"))


def parse_volume(html: str, volume_url: str) -> dict:
    """Validate the volume heading and preserve the list's order and titles."""
    volume_url, volume = validate_volume_url(volume_url)
    root = parse_html(html)
    headings = [clean(node.text()) for node in root.walk() if node.tag == "h2"]
    header = next((text for text in headings if text.startswith(f"Volume {volume}:")), None)
    if header is None:
        raise ValueError("official PMLR volume heading not found or volume number mismatched")
    page_titles = [clean(node.text()) for node in root.walk() if node.tag == "title"]
    if not any("Proceedings of Machine Learning Research" in title for title in page_titles):
        raise ValueError("page does not identify the Proceedings of Machine Learning Research")
    canonical = [node.attrs.get("href") for node in root.walk()
                 if node.tag == "link" and node.attrs.get("rel") == "canonical"]
    if canonical and validate_volume_url(urljoin(volume_url, canonical[0]))[0] != volume_url:
        raise ValueError("canonical URL disagrees with supplied volume")
    metadata = header.split(":", 1)[1].strip()
    conference = metadata.split(",", 1)[0].strip()
    year_match = re.search(r"\b(19[0-9]{2}|20[0-9]{2})\b", metadata)
    if not conference or year_match is None:
        raise ValueError("cannot determine conference/year from the volume heading")
    papers = []
    warnings = []
    seen = set()
    paper_nodes = [node for node in root.walk() if node.tag == "div" and node.has_class("paper")]
    for index, node in enumerate(paper_nodes, 1):
        title = next((clean(item.text()) for item in node.walk() if item.has_class("title")), "")
        links = [(urljoin(volume_url, item.attrs.get("href", "")), clean(item.text()))
                 for item in node.walk() if item.tag == "a"]
        detail_url = next((url for url, label in links if label.lower() == "abs" and is_detail_url(url, volume)), None)
        if not title or not detail_url:
            warnings.append(f"list record {index} missing title or valid official abstract link; not imported")
            continue
        if detail_url in seen:
            warnings.append(f"duplicate list URL omitted: {detail_url}")
            continue
        seen.add(detail_url)
        authors = next((clean(item.text()).split(", ") for item in node.walk() if item.has_class("authors")), [])
        slug = Path(urlsplit(detail_url).path).stem
        pdf_url = next((url for url, label in links if label.lower() == "download pdf"), None)
        papers.append({"id": f"pmlr:{volume}:{slug}", "title": title, "authors": authors,
                       "abstract": None, "url": detail_url, "pdf_url": pdf_url,
                       "acceptance": "accepted", "sources": []})
    if not paper_nodes or not papers:
        raise ValueError("no valid paper records found; refusing to emit an empty accepted-paper list")
    return {"conference": conference, "year": int(year_match.group(1)), "volume": volume,
            "papers": papers, "list_record_count": len(paper_nodes), "warnings": warnings}


def parse_paper(html: str, paper: dict, volume: str) -> dict:
    """Read citation metadata and the full abstract, not truncated social tags."""
    root = parse_html(html)
    meta: dict[str, list[str]] = {}
    for node in root.walk():
        if node.tag == "meta" and node.attrs.get("name", "").startswith("citation_"):
            meta.setdefault(node.attrs["name"], []).append(clean(node.attrs.get("content", "")))
    if not meta.get("citation_title"):
        raise ValueError("citation_title missing; paper-detail page could not be verified")
    citation_url = next(iter(meta.get("citation_abstract_html_url", [])), paper["url"])
    if not is_detail_url(citation_url, volume) or citation_url != paper["url"]:
        raise ValueError("paper citation URL is outside this volume or differs from the list")
    result = dict(paper)
    result["title"] = meta["citation_title"][0]
    result["authors"] = meta.get("citation_author", paper.get("authors", []))
    result["pdf_url"] = next(iter(meta.get("citation_pdf_url", [])), paper.get("pdf_url"))
    abstract = next((clean(node.text()) for node in root.walk()
                     if node.attrs.get("id") == "abstract"), "")
    result["abstract"] = abstract or None
    result["sources"] = ([{"id": "abstract", "kind": "abstract", "text": abstract,
                            "url": paper["url"], "locator": "Abstract"}] if abstract else [])
    if not abstract:
        result["error"] = "abstract missing or empty on the verified paper-detail page"
    return result


class OfficialRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parts = urlsplit(newurl)
        if parts.scheme != "https" or parts.netloc.lower() != HOST:
            raise ValueError("refusing redirect outside official HTTPS PMLR host")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_html(url: str) -> str:
    """Bounded sequential reads; never follow a redirect to another host."""
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc.lower() != HOST:
        raise ValueError("only official HTTPS PMLR pages may be fetched")
    opener = build_opener(OfficialRedirects())
    last_error = None
    for attempt in range(ATTEMPTS):
        try:
            request = Request(url, headers={"User-Agent": "conference-paper-search/0.1 (PMLR proceedings reader)"})
            with opener.open(request, timeout=TIMEOUT) as response:
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    raise ValueError("HTML page exceeds maximum allowed size")
                charset = response.headers.get_content_charset() or "utf-8"
                return body.decode(charset)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            last_error = error
            if isinstance(error, HTTPError) and error.code not in (408, 429, 500, 502, 503, 504):
                break
            if attempt + 1 < ATTEMPTS:
                time.sleep(min(2 ** attempt, 4))
    raise RuntimeError(f"failed after bounded attempts: {last_error}") from last_error


def fetch_volume(volume_url: str, limit: int | None = None,
                 fetcher: Callable[[str], str] = fetch_html) -> dict:
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")
    volume_url, _ = validate_volume_url(volume_url)
    listing = parse_volume(fetcher(volume_url), volume_url)
    selected = listing["papers"] if limit is None else listing["papers"][:limit]
    papers = []
    for index, paper in enumerate(selected, 1):
        try:
            papers.append(parse_paper(fetcher(paper["url"]), paper, listing["volume"]))
        except (ValueError, RuntimeError, HTTPError, URLError, TimeoutError, OSError, UnicodeError) as error:
            failed = dict(paper)
            failed["error"] = f"detail retrieval failed: {error}"
            papers.append(failed)
        print(f"PMLR {listing['volume']}: {index}/{len(selected)} {paper['id']}", file=sys.stderr)
    note = (f"Scope: PMLR volume {listing['volume']} only. Parsed {len(listing['papers'])} unique paper links "
            f"from {listing['list_record_count']} list records; retrieved {len(papers)} detail records. "
            "track=main denotes this conference proceedings volume, not verified technical subtracks. "
            "Other volumes, workshops, late updates and on-site attendance are not covered; list parsing alone "
            "does not prove coverage of the entire conference.")
    if limit is not None:
        note += f" --limit {limit}: first-N sample in official list order; not a full-conference relevance sample."
    if listing["warnings"]:
        note += " List warnings: " + "; ".join(listing["warnings"])
    return {"conference": listing["conference"], "year": listing["year"], "track": "main",
            "source_url": volume_url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "scope_note": note, "papers": papers}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--volume-url", required=True, help="official PMLR volume URL")
    parser.add_argument("--output", required=True, type=Path, help="destination JSON file")
    parser.add_argument("--limit", type=int, help="fetch only the first N papers for a pilot; default all")
    args = parser.parse_args(argv)
    try:
        result = fetch_volume(args.volume_url, args.limit)
    except (ValueError, RuntimeError, HTTPError, URLError, TimeoutError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failures = sum(bool(paper.get("error")) for paper in result["papers"])
    print(f"Saved {len(result['papers'])} papers ({failures} detail warnings) to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
