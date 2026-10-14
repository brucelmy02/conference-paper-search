#!/usr/bin/env python3
"""Prepare conference records and verify evidence-backed assessments.

Standard library only. This program never assigns relevance or generates claims.
Relevance assessments are supplied by the skill after reading source material.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


class DataError(ValueError):
    """An actionable input validation error."""


def require(condition, message):
    if not condition:
        raise DataError(message)


def string(value, field, nonempty=False):
    require(isinstance(value, str), f"{field}: expected a string")
    if nonempty:
        require(bool(value.strip()), f"{field}: must not be empty")
    return value


def strings(value, field):
    require(isinstance(value, list), f"{field}: expected a list of strings")
    for index, item in enumerate(value):
        string(item, f"{field}[{index}]", nonempty=True)
    return value


def choice(value, allowed, field):
    require(isinstance(value, str) and value in allowed,
            f"{field}: expected one of {', '.join(sorted(allowed))}")
    return value


def safe_url(value, field, optional=False):
    if optional and value in (None, ""):
        return value
    string(value, field, nonempty=True)
    require(not any(c.isspace() or ord(c) < 32 for c in value),
            f"{field}: URL must not contain whitespace or control characters")
    try:
        parsed = urlsplit(value)
        require(parsed.scheme.lower() in {"http", "https"} and bool(parsed.hostname),
                f"{field}: expected an absolute http(s) URL")
        require(parsed.username is None and parsed.password is None,
                f"{field}: URL credentials are not allowed")
        # Accessing port also rejects malformed port numbers.
        parsed.port
    except DataError:
        raise
    except ValueError as exc:
        raise DataError(f"{field}: malformed URL") from exc
    return value


def canonical_url(value):
    parsed = urlsplit(value)
    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    port = parsed.port
    netloc = host if port is None or (scheme, port) in {("https", 443), ("http", 80)} else f"{host}:{port}"
    return urlunsplit((scheme, netloc, parsed.path or "/", parsed.query, ""))


def whitespace(value):
    return " ".join(value.split())


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DataError(f"Cannot read JSON {path}: {exc}") from exc


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_papers(path):
    path = Path(path)
    if path.suffix.lower() != ".csv":
        return normalize_papers(read_json(path))
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            records = list(csv.DictReader(stream))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise DataError(f"Cannot read CSV {path}: {exc}") from exc
    for row in records:
        authors = row.get("authors", "") or ""
        if authors.strip().startswith("["):
            try:
                row["authors"] = json.loads(authors)
            except json.JSONDecodeError as exc:
                raise DataError("CSV authors: malformed JSON list") from exc
        else:
            row["authors"] = [a.strip() for a in re.split(r"[;|]", authors) if a.strip()]
        if not row.get("abstract"):
            row["abstract"] = None
    return normalize_papers(records)


def normalize_papers(data):
    """Normalize records, preserving envelope scope and explicit source text.

    Bare arrays/CSV have unknown conference scope. Explicit acceptance labels
    are preserved for caller verification; missing labels stay unknown.
    Titles never deduplicate.
    """
    imported = isinstance(data, list)
    if imported:
        envelope = {
            "conference": None, "year": None, "track": "unknown",
            "source_url": None, "retrieved_at": None,
            "scope_note": "Imported records: conference scope is unknown; explicit acceptance labels require source verification.",
            "scope_status": "unknown", "papers": copy.deepcopy(data),
        }
    else:
        require(isinstance(data, dict), "papers: expected an envelope object or a JSON array")
        envelope = copy.deepcopy(data)
    records = envelope.get("papers")
    require(isinstance(records, list), "papers: expected a list")
    for field in ("conference", "track", "retrieved_at", "scope_note"):
        value = envelope.get(field)
        require(value is None or isinstance(value, str), f"{field}: expected a string or null")
    year = envelope.get("year")
    require(year is None or (isinstance(year, int) and not isinstance(year, bool) and year > 0),
            "year: expected a positive integer or null")
    safe_url(envelope.get("source_url"), "source_url", optional=True)
    if "scope_status" in envelope:
        choice(envelope["scope_status"], {"complete", "partial", "unknown"}, "scope_status")
    else:
        # A scope claim must be supplied explicitly; never assume completeness.
        envelope["scope_status"] = "unknown"
    normalized = []
    by_id, by_url = {}, {}
    dedup = envelope.get("duplicates", [])
    require(isinstance(dedup, list) and all(isinstance(item, dict) for item in dedup),
            "duplicates: expected a list of objects")
    dedup = list(dedup)
    for index, raw in enumerate(records):
        prefix = f"papers[{index}]"
        require(isinstance(raw, dict), f"{prefix}: expected an object")
        paper = copy.deepcopy(raw)
        title = string(paper.get("title"), f"{prefix}.title", nonempty=True)
        url = safe_url(paper.get("url"), f"{prefix}.url", optional=True) or None
        paper["url"] = url
        identity = canonical_url(url) if url else None
        supplied_id = paper.get("id")
        if supplied_id in (None, ""):
            seed = identity if identity else f"{index}\n{title}"
            supplied_id = "paper-" + hashlib.sha256(seed.encode()).hexdigest()[:16]
        string(supplied_id, f"{prefix}.id", nonempty=True)
        paper["id"] = supplied_id
        authors = paper.setdefault("authors", [])
        strings(authors, f"{prefix}.authors")
        abstract = paper.setdefault("abstract", None)
        require(abstract is None or isinstance(abstract, str), f"{prefix}.abstract: expected a string or null")
        if abstract is not None and not abstract.strip():
            paper["abstract"] = abstract = None
        acceptance = paper.get("acceptance") or "unknown"
        paper["acceptance"] = choice(acceptance, {"accepted", "unknown", "rejected", "withdrawn"}, f"{prefix}.acceptance")
        safe_url(paper.get("pdf_url"), f"{prefix}.pdf_url", optional=True)
        source_records = paper.setdefault("sources", [])
        require(isinstance(source_records, list), f"{prefix}.sources: expected a list")
        source_ids = set()
        for source_index, source in enumerate(source_records):
            context = f"{prefix}.sources[{source_index}]"
            require(isinstance(source, dict), f"{context}: expected an object")
            source_id = string(source.get("id"), f"{context}.id", nonempty=True)
            require(source_id not in source_ids, f"{context}: duplicate source id {source_id}")
            source_ids.add(source_id)
            choice(source.get("kind"), {"title", "abstract", "full_text"}, f"{context}.kind")
            string(source.get("text"), f"{context}.text", nonempty=True)
            safe_url(source.get("url"), f"{context}.url", optional=True)
            if "locator" in source:
                string(source["locator"], f"{context}.locator")
            require(bool(source.get("url") or source.get("locator")),
                    f"{context}: source requires a URL or locator")
            if source_id == "title":
                require(source["kind"] == "title" and whitespace(source["text"]) == whitespace(title),
                        f"{context}: reserved title source must match the paper title")
            if source_id == "abstract":
                require(abstract is not None and source["kind"] == "abstract" and whitespace(source["text"]) == whitespace(abstract),
                        f"{context}: reserved abstract source must match the paper abstract")
        if "title" not in source_ids:
            source_records.append({"id": "title", "kind": "title", "text": title, "url": url, "locator": "title"})
        if abstract and "abstract" not in source_ids:
            source_records.append({"id": "abstract", "kind": "abstract", "text": abstract, "url": url, "locator": "abstract"})
        presentation = paper.get("presentation")
        if presentation is not None:
            require(isinstance(presentation, dict), f"{prefix}.presentation: expected an object")
            require(isinstance(presentation.get("confirmed"), bool), f"{prefix}.presentation.confirmed: expected a boolean")
            if presentation["confirmed"]:
                safe_url(presentation.get("source_url"), f"{prefix}.presentation.source_url")
            else:
                safe_url(presentation.get("source_url"), f"{prefix}.presentation.source_url", optional=True)
            for field in ("time", "timezone", "session", "location"):
                value = presentation.get(field)
                require(value is None or isinstance(value, str), f"{prefix}.presentation.{field}: expected a string or null")
        id_match = by_id.get(supplied_id)
        url_match = by_url.get(identity) if identity else None
        require(id_match is None or url_match is None or id_match is url_match,
                f"{prefix}: id and URL identify different existing records")
        existing = id_match or url_match
        if existing is not None:
            require(whitespace(existing["title"]) == whitespace(title),
                    f"{prefix}: duplicate id/URL has conflicting titles; reconcile records first")
            require(existing["acceptance"] == paper["acceptance"],
                    f"{prefix}: duplicate id/URL has conflicting acceptance; reconcile records first")
            require(not (existing["abstract"] and abstract and whitespace(existing["abstract"]) != whitespace(abstract)),
                    f"{prefix}: duplicate id/URL has conflicting abstracts; reconcile records first")
            if not existing["abstract"] and abstract:
                existing["abstract"] = abstract
            for field in ("pdf_url", "presentation"):
                if existing.get(field) and paper.get(field):
                    require(existing[field] == paper[field], f"{prefix}: conflicting {field}; reconcile records first")
                elif paper.get(field):
                    existing[field] = paper[field]
            existing["authors"] = list(dict.fromkeys(existing["authors"] + paper["authors"]))
            for source in source_records:
                old = next((s for s in existing["sources"] if s["id"] == source["id"]), None)
                if old is None:
                    existing["sources"].append(source)
                else:
                    require(old["kind"] == source["kind"] and whitespace(old["text"]) == whitespace(source["text"]),
                            f"{prefix}: duplicate id/URL has conflicting source {source['id']}")
            if supplied_id != existing["id"]:
                dedup.append({"discarded_id": supplied_id, "retained_id": existing["id"], "reason": "same URL"})
            else:
                dedup.append({"discarded_id": supplied_id, "retained_id": existing["id"], "reason": "same id"})
            by_id[supplied_id] = existing
            if identity:
                by_url[identity] = existing
            continue
        by_id[supplied_id] = paper
        if identity:
            by_url[identity] = paper
        normalized.append(paper)
    envelope["papers"] = normalized
    envelope["duplicates"] = dedup
    return envelope


def validate_profile(profile):
    require(isinstance(profile, dict), "profile: expected an object")
    choice(profile.get("owner"), {"personal", "lab"}, "profile.owner")
    topics = profile.get("topics")
    require(isinstance(topics, list) and bool(topics), "profile.topics: expected a nonempty list")
    by_id = {}
    for index, topic in enumerate(topics):
        prefix = f"profile.topics[{index}]"
        require(isinstance(topic, dict), f"{prefix}: expected an object")
        topic_id = string(topic.get("id"), f"{prefix}.id", nonempty=True)
        require(topic_id not in by_id, f"{prefix}: duplicate topic id {topic_id}")
        string(topic.get("problem"), f"{prefix}.problem", nonempty=True)
        for field in ("focus", "constraints", "exclude"):
            strings(topic.get(field, []), f"{prefix}.{field}")
        relations = strings(topic.get("relation_scope"), f"{prefix}.relation_scope")
        require(bool(relations), f"{prefix}.relation_scope: must not be empty")
        for relation in relations:
            choice(relation, {"direct", "method_transfer", "adjacent"}, f"{prefix}.relation_scope")
        choice(topic.get("priority"), {"primary", "secondary"}, f"{prefix}.priority")
        provenance = topic.get("provenance")
        require(isinstance(provenance, list) and bool(provenance), f"{prefix}.provenance: expected a nonempty list")
        for source in provenance:
            require(isinstance(source, dict), f"{prefix}.provenance: expected objects")
            choice(source.get("kind"), {"user", "publication_inference"}, f"{prefix}.provenance.kind")
            string(source.get("reference"), f"{prefix}.provenance.reference", nonempty=True)
        by_id[topic_id] = topic
    if "representative_papers" in profile:
        require(isinstance(profile["representative_papers"], list), "profile.representative_papers: expected a list")
        for index, paper in enumerate(profile["representative_papers"]):
            prefix = f"profile.representative_papers[{index}]"
            require(isinstance(paper, dict), f"{prefix}: expected an object")
            string(paper.get("title"), f"{prefix}.title", nonempty=True)
            safe_url(paper.get("url"), f"{prefix}.url", optional=True)
            require(paper.get("reason") is None or isinstance(paper["reason"], str), f"{prefix}.reason: expected a string or null")
    if "notes" in profile:
        string(profile["notes"], "profile.notes")
    return by_id


def assessment_records(data):
    require(isinstance(data, dict) and isinstance(data.get("assessments"), list),
            "assessments: expected an object with an assessments list")
    return data["assessments"]


def validate_assessments(papers, profile, data):
    topics = validate_profile(profile)
    paper_index = {paper["id"]: paper for paper in papers["papers"]}
    assessments = {}
    for index, assessment in enumerate(assessment_records(data)):
        prefix = f"assessments[{index}]"
        require(isinstance(assessment, dict), f"{prefix}: expected an object")
        paper_id = string(assessment.get("paper_id"), f"{prefix}.paper_id", nonempty=True)
        require(paper_id in paper_index, f"{prefix}: unknown paper id {paper_id}")
        require(paper_id not in assessments, f"{prefix}: duplicate assessment for {paper_id}")
        paper = paper_index[paper_id]
        decision = choice(assessment.get("decision"), {"include", "exclude", "pending"}, f"{prefix}.decision")
        choice(assessment.get("relevance"), {"high", "medium", "low", "unknown"}, f"{prefix}.relevance")
        relation = assessment.get("relation")
        if relation is not None:
            choice(relation, {"direct", "method_transfer", "adjacent"}, f"{prefix}.relation")
        topic_ids = strings(assessment.get("topic_ids"), f"{prefix}.topic_ids")
        require(len(topic_ids) == len(set(topic_ids)), f"{prefix}.topic_ids: duplicates are not allowed")
        for topic_id in topic_ids:
            require(topic_id in topics, f"{prefix}: unknown topic id {topic_id}")
        string(assessment.get("reason"), f"{prefix}.reason", nonempty=True)
        string(assessment.get("reading_focus"), f"{prefix}.reading_focus")
        for field in ("differences", "uncertainties"):
            strings(assessment.get(field), f"{prefix}.{field}")
        status = choice(assessment.get("evidence_status"), {"sufficient", "limited", "missing"}, f"{prefix}.evidence_status")
        priority = assessment.get("priority")
        require(type(priority) is int and priority in {1, 2, 3}, f"{prefix}.priority: expected integer 1, 2, or 3")
        evidence = assessment.get("evidence")
        require(isinstance(evidence, list), f"{prefix}.evidence: expected a list")
        source_index = {source["id"]: source for source in paper["sources"]}
        for item_index, item in enumerate(evidence):
            context = f"{prefix}.evidence[{item_index}]"
            require(isinstance(item, dict), f"{context}: expected an object")
            source_id = string(item.get("source_id"), f"{context}.source_id", nonempty=True)
            require(source_id in source_index, f"{context}: unknown source id {source_id}")
            quote = string(item.get("quote"), f"{context}.quote", nonempty=True)
            require(whitespace(quote) in whitespace(source_index[source_id]["text"]),
                    f"{context}: quote is absent from source {source_id}")
        if decision in {"include", "exclude"}:
            require(status != "missing", f"{prefix}: a final decision cannot have missing evidence")
            require(bool(evidence), f"{prefix}: include/exclude requires source evidence")
        if paper["acceptance"] == "unknown":
            require(decision == "pending", f"{prefix}: unknown acceptance requires pending")
        if decision == "include":
            require(paper["acceptance"] == "accepted", f"{prefix}: only accepted papers may be included")
            require(relation is not None, f"{prefix}: include requires a relation")
            require(bool(topic_ids), f"{prefix}: include requires matched topics")
            require(assessment["relevance"] != "unknown", f"{prefix}: include requires known relevance")
            string(assessment["reading_focus"], f"{prefix}.reading_focus", nonempty=True)
            for topic_id in topic_ids:
                require(relation in topics[topic_id]["relation_scope"],
                        f"{prefix}: relation {relation} is outside matched topic {topic_id} scope")
        assessments[paper_id] = assessment
    return assessments


def coverage(papers, assessments=None):
    records = papers["papers"]
    result = {
        "total_papers": len(records), "duplicates_removed": len(papers.get("duplicates", [])),
        "scope_status": papers.get("scope_status", "unknown"),
        "scope_note": papers.get("scope_note"),
        "missing_abstract": sum(not paper["abstract"] for paper in records),
        "title_only": sum(not any(source["kind"] in {"abstract", "full_text"} for source in paper["sources"]) for paper in records),
        "acceptance": dict(Counter(paper["acceptance"] for paper in records)),
    }
    if assessments is not None:
        decisions = Counter(item["decision"] for item in assessments.values())
        result.update({"processed": len(assessments), "unprocessed": len(records) - len(assessments),
                       "included": decisions["include"], "excluded": decisions["exclude"], "pending": decisions["pending"],
                       "limited_evidence": sum(item["evidence_status"] == "limited" for item in assessments.values())})
    return result


def prepare(papers_path, out_dir, batch_size=40):
    require(type(batch_size) is int and batch_size > 0, "batch-size: expected a positive integer")
    papers = read_papers(papers_path)
    destination = Path(out_dir)
    require(not destination.exists() or (destination.is_dir() and not any(destination.iterdir())),
            f"Output directory must be empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "papers.json", papers)
    for index, offset in enumerate(range(0, len(papers["papers"]), batch_size), 1):
        batch = {key: value for key, value in papers.items() if key not in {"papers", "duplicates"}}
        batch["papers"] = papers["papers"][offset:offset + batch_size]
        batch["batch_number"] = index
        batch["total_papers"] = len(papers["papers"])
        write_json(destination / f"batch-{index:03d}.json", batch)
    stats = coverage(papers)
    write_json(destination / "coverage.json", stats)
    return stats


def merge_assessments(inputs, output):
    merged, seen = [], set()
    for path in inputs:
        for index, assessment in enumerate(assessment_records(read_json(path))):
            require(isinstance(assessment, dict), f"{path}: assessments[{index}] must be an object")
            paper_id = string(assessment.get("paper_id"), f"{path}: paper_id", nonempty=True)
            require(paper_id not in seen, f"Duplicate assessment during merge: {paper_id}")
            seen.add(paper_id)
            merged.append(assessment)
    # Input ordering is retained; no model judgment or last-write-wins behavior.
    write_json(output, {"assessments": merged})
    return len(merged)


def markdown(value):
    value = str(value).replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    value = re.sub(r"([\\`*_{}\[\]()#+.!|~-])", r"\\\1", value)
    return value.replace("\n", " ")


def link(label, url):
    # Validation restricts protocols; encode markdown delimiter characters too.
    if not url:
        return markdown(label) + "（无公开链接）"
    safe_url(url, "report link")
    for character, encoded in (("<", "%3C"), (">", "%3E"), ("(", "%28"), (")", "%29"), ("\\", "%5C"), ('"', "%22")):
        url = url.replace(character, encoded)
    return f"[{markdown(label)}](<{url}>)"


RELATIONS = {"direct": "直接相关", "method_transfer": "方法可借鉴", "adjacent": "邻近方向", None: "待确定"}
RELEVANCE = {"high": "高", "medium": "中", "low": "低", "unknown": "待确定"}
EVIDENCE_STATUS = {"sufficient": "充分", "limited": "有限", "missing": "缺失"}


def ranked(papers, assessments, profile):
    topic_priority = {topic["id"]: topic["priority"] for topic in profile["topics"]}
    selected = [paper for paper in papers["papers"] if assessments.get(paper["id"], {}).get("decision") == "include"]
    return sorted(selected, key=lambda paper: (
        assessments[paper["id"]]["priority"],
        {"high": 0, "medium": 1, "low": 2, "unknown": 3}[assessments[paper["id"]]["relevance"]],
        0 if any(topic_priority[tid] == "primary" for tid in assessments[paper["id"]]["topic_ids"]) else 1,
        paper["id"],
    ))


def paper_details(paper, assessment, topics, show_schedule=False):
    lines = [f"### {markdown(paper['title'])}", "",
             f"{link('论文', paper['url'])} · ID：{markdown(paper['id'])}"]
    if paper.get("pdf_url"):
        lines[-1] += f" · {link('PDF', paper['pdf_url'])}"
    if paper["authors"]:
        lines += ["", "作者：" + "、".join(markdown(author) for author in paper["authors"])]
    lines += ["", f"优先级：{assessment['priority']}；相关性：{RELEVANCE[assessment['relevance']]}；关联：{RELATIONS[assessment['relation']]}；证据：{EVIDENCE_STATUS[assessment['evidence_status']]}。",
              "", "匹配方向：" + "；".join(markdown(topics[tid]["problem"]) for tid in assessment["topic_ids"]),
              "", "推荐理由：" + markdown(assessment["reason"]), "", "重点阅读：" + markdown(assessment["reading_focus"]), "", "来源证据：", ""]
    sources = {source["id"]: source for source in paper["sources"]}
    for evidence in assessment["evidence"]:
        source = sources[evidence["source_id"]]
        locator = source.get("locator") or source["kind"]
        lines.append(f"- “{markdown(evidence['quote'])}” — {link(locator, source.get('url'))}（{markdown(source['id'])}）")
    for field, label in (("differences", "关键差异"), ("uncertainties", "待核查项")):
        if assessment[field]:
            lines += ["", label + "：", ""] + ["- " + markdown(item) for item in assessment[field]]
    if show_schedule:
        schedule = paper.get("presentation")
        if schedule and schedule["confirmed"]:
            verified = []
            if schedule.get("time"):
                verified.append("时间：" + markdown(schedule["time"]))
            if schedule.get("timezone"):
                verified.append("时区：" + markdown(schedule["timezone"]))
            if schedule.get("session"):
                verified.append("场次：" + markdown(schedule["session"]))
            if schedule.get("location"):
                verified.append("地点：" + markdown(schedule["location"]))
            lines += ["", "已核实日程字段：" + ("；".join(verified) or "尚未公布详细字段") + "。" + link("官方日程", schedule["source_url"])]
            if not (schedule.get("time") and schedule.get("timezone")):
                lines += ["", "时间或时区尚未核实，暂不能据此排程。"]
        else:
            lines += ["", "现场展示安排：尚无已确认日程。"]
    return lines + [""]


def render_report(papers, profile, data, mode="recap", top_k=20, include_excluded=False):
    require(mode in {"attend", "recap"}, "mode: expected attend or recap")
    require(type(top_k) is int and top_k > 0, "top-k: expected a positive integer")
    assessments = validate_assessments(papers, profile, data)
    topics = {topic["id"]: topic for topic in profile["topics"]}
    stats = coverage(papers, assessments)
    selected = ranked(papers, assessments, profile)
    label = "参会阅读清单" if mode == "attend" else "会后方向论文清单"
    lines = [f"# {label}", "", f"会议：{markdown(papers.get('conference') or '未核实')}；年份：{markdown(papers.get('year') or '未核实')}；范围：{markdown(papers.get('track') or '未核实')}。"]
    if papers.get("source_url"):
        lines += ["", link("论文列表来源", papers["source_url"])]
    if papers.get("retrieved_at"):
        lines += ["", "获取日期：" + markdown(papers["retrieved_at"])]
    lines += ["", "## 覆盖情况", "",
              f"输入 {stats['total_papers']} 篇；已评估 {stats['processed']} 篇；推荐 {stats['included']} 篇；排除 {stats['excluded']} 篇；待核查 {stats['pending']} 篇；未处理 {stats['unprocessed']} 篇。",
              "", f"缺少摘要 {stats['missing_abstract']} 篇；仅有标题资料 {stats['title_only']} 篇；录用状态未知 {stats['acceptance'].get('unknown', 0)} 篇；合并重复记录 {stats['duplicates_removed']} 条。",
              "", f"范围状态：{markdown(stats['scope_status'])}。{markdown(stats['scope_note'] or '未提供范围说明。')}"]
    if stats["scope_status"] != "complete" or stats["unprocessed"]:
        lines += ["", "覆盖尚未确认完整；清单仅反映已处理且有证据的论文。"]
    lines += ["", "## 研究兴趣", ""]
    for topic in profile["topics"]:
        lines.append(f"- {markdown(topic['id'])}：{markdown(topic['problem'])}（{'主要' if topic['priority'] == 'primary' else '次要'}）")
        for provenance in topic["provenance"]:
            lines.append(f"  - {'用户输入' if provenance['kind'] == 'user' else '发表记录推断'}：{markdown(provenance['reference'])}")
    lines += ["", f"## 优先阅读（最多 {top_k} 篇）", ""]
    if not selected:
        lines.append("暂无通过事实校验的推荐论文。")
    for index, paper in enumerate(selected[:top_k], 1):
        assessment = assessments[paper["id"]]
        lines.append(f"{index}. {link(paper['title'], paper['url'])} — 优先级 {assessment['priority']}；{RELATIONS[assessment['relation']]}；{markdown(paper['id'])}")
    if mode == "recap":
        lines += ["", "## 各方向相关论文全表", ""]
        for topic in profile["topics"]:
            lines += ["### " + markdown(topic["problem"]), ""]
            members = [paper for paper in selected if topic["id"] in assessments[paper["id"]]["topic_ids"]]
            if not members:
                lines.append("暂无已确认相关论文。")
            for paper in members:
                lines.append(f"- {link(paper['title'], paper['url'])}（{markdown(paper['id'])}；{RELATIONS[assessments[paper['id']]['relation']]}）")
            lines.append("")
    lines += ["## 推荐依据", ""]
    detail_papers = selected[:top_k] if mode == "attend" else selected
    for paper in detail_papers:
        lines += paper_details(paper, assessments[paper["id"]], topics, show_schedule=mode == "attend")
    lines += ["## 待核查与未处理", ""]
    pending = [paper for paper in papers["papers"] if paper["id"] not in assessments or assessments[paper["id"]]["decision"] == "pending"]
    if not pending:
        lines.append("无。")
    for paper in pending:
        assessment = assessments.get(paper["id"])
        reason = assessment["reason"] if assessment else "尚未处理；未作相关性判断"
        lines.append(f"- {link(paper['title'], paper['url'])}（{markdown(paper['id'])}；录用：{markdown(paper['acceptance'])}）：{markdown(reason)}")
        if assessment:
            for uncertainty in assessment["uncertainties"]:
                lines.append("  - " + markdown(uncertainty))
    if not include_excluded:
        if stats["excluded"]:
            lines += ["", f"已排除 {stats['excluded']} 篇；逐篇理由与原文证据保存在本次 assessments 文件中。"]
        return "\n".join(lines).rstrip() + "\n"
    lines += ["", "## 已排除论文", ""]
    excluded = [paper for paper in papers["papers"] if assessments.get(paper["id"], {}).get("decision") == "exclude"]
    if not excluded:
        lines.append("无。")
    for paper in excluded:
        assessment = assessments[paper["id"]]
        lines.append(f"- {link(paper['title'], paper['url'])}（{markdown(paper['id'])}；录用：{markdown(paper['acceptance'])}）：{markdown(assessment['reason'])}")
        sources = {source["id"]: source for source in paper["sources"]}
        for evidence in assessment["evidence"]:
            source = sources[evidence["source_id"]]
            lines.append(f"  - “{markdown(evidence['quote'])}” — {link(source.get('locator') or source['kind'], source.get('url'))}")
    return "\n".join(lines).rstrip() + "\n"


def validate_overview(overview, papers, profile, assessments):
    require(isinstance(overview, dict), "overview: expected an object")
    string(overview.get("lead", ""), "overview.lead")
    topics = {topic["id"] for topic in profile["topics"]}
    known = {paper["id"] for paper in papers["papers"]}
    themes = overview.get("themes", [])
    questions = overview.get("attendance_questions", [])
    require(isinstance(themes, list), "overview.themes: expected a list")
    require(isinstance(questions, list), "overview.attendance_questions: expected a list")
    for index, theme in enumerate(themes):
        context = f"overview.themes[{index}]"
        require(isinstance(theme, dict), f"{context}: expected an object")
        topic_id = string(theme.get("topic_id"), f"{context}.topic_id", nonempty=True)
        require(topic_id in topics, f"{context}: unknown topic id")
        string(theme.get("text"), f"{context}.text", nonempty=True)
        refs = strings(theme.get("paper_ids"), f"{context}.paper_ids")
        require(bool(refs), f"{context}: a theme description needs supporting papers")
        for paper_id in refs:
            require(paper_id in known, f"{context}: unknown paper id {paper_id}")
            require(assessments.get(paper_id, {}).get("decision") == "include",
                    f"{context}: supporting paper must be included")
    for index, item in enumerate(questions):
        context = f"overview.attendance_questions[{index}]"
        require(isinstance(item, dict), f"{context}: expected an object")
        paper_id = string(item.get("paper_id"), f"{context}.paper_id", nonempty=True)
        require(paper_id in known and assessments.get(paper_id, {}).get("decision") == "include",
                f"{context}: questions require an included paper")
        strings(item.get("questions"), f"{context}.questions")
    return copy.deepcopy(overview)


def build_output_bundle(papers, profile, data, mode="recap", top_k=20, overview=None):
    require(mode in {"attend", "recap"}, "mode: expected attend or recap")
    require(type(top_k) is int and top_k > 0, "top-k: expected a positive integer")
    assessments = validate_assessments(papers, profile, data)
    overview = validate_overview({} if overview is None else overview, papers, profile, assessments)
    labels = {topic["id"]: topic["problem"] for topic in profile["topics"]}
    recommendations = ranked(papers, assessments, profile)
    records, identifiers = [], set()
    for paper in papers["papers"]:
        record = copy.deepcopy(paper)
        display_id = "P-" + hashlib.sha256(paper["id"].encode("utf-8")).hexdigest()[:12].upper()
        require(display_id not in identifiers, "display ID collision: reconcile paper identities before export")
        identifiers.add(display_id)
        record["display_id"] = display_id
        record["assessment"] = copy.deepcopy(assessments.get(paper["id"]))
        record["topic_labels"] = [labels[tid] for tid in assessments.get(paper["id"], {}).get("topic_ids", [])]
        record["reading_status"] = "unread"
        record["user_notes"] = ""
        records.append(record)
    metadata = {field: papers.get(field) for field in
                ("conference", "year", "track", "source_url", "retrieved_at", "scope_note", "scope_status")}
    metadata.update({"mode": mode, "top_k": top_k,
                     "conference_label": {"International Conference on Machine Learning": "ICML"}.get(papers.get("conference"), papers.get("conference")),
                     "duplicates": copy.deepcopy(papers.get("duplicates", [])),
                     "selected_ids": [paper["id"] for paper in recommendations[:top_k]],
                     "recommended_ids": [paper["id"] for paper in recommendations],
                     "csv_scope": "include_and_pending",
                     "reading_marks_note": "HTML 阅读标记保存在当前浏览器，不会自动更新其他三份文件。"})
    return {"schema_version": "1.0", "metadata": metadata, "coverage": coverage(papers, assessments),
            "profile": copy.deepcopy(profile), "overview": overview, "papers": records}


def short_reason(value):
    first = re.split(r"(?<=[。！？])", value, maxsplit=1)[0]
    return first if len(first) <= 130 else first[:127] + "…"


def render_export_markdown(bundle):
    metadata, stats = bundle["metadata"], bundle["coverage"]
    topics = {topic["id"]: topic for topic in bundle["profile"]["topics"]}
    records = {paper["id"]: paper for paper in bundle["papers"]}
    selected = [records[paper_id] for paper_id in metadata["selected_ids"]]
    all_related = [records[paper_id] for paper_id in metadata["recommended_ids"]]
    label = "参会论文导读" if metadata["mode"] == "attend" else "会后方向导读"
    lines = [f"# {label}", "",
             f"{markdown(metadata.get('conference_label') or metadata.get('conference') or '会议待核实')} · {markdown(metadata.get('year') or '年份待核实')}", "",
             bundle["overview"].get("lead") and markdown(bundle["overview"]["lead"]) or
             f"本次识别出 {stats['included']} 篇相关论文，可从优先阅读开始，再按研究方向查找。", "",
             f"已评估 {stats['processed']}/{stats['total_papers']} 篇 · 相关 {stats['included']} 篇 · 待核查 {stats['pending']} 篇 · 未处理 {stats['unprocessed']} 篇。", "",
             "[搜索与筛选](index.html) · [论文目录](papers.csv) · [完整记录](results.json)", ""]
    if stats["scope_status"] != "complete" or stats["unprocessed"]:
        lines += ["本次覆盖范围尚未确认完整；下方结果对应已取得的论文资料。", ""]
    lines += ["## 研究方向", ""]
    for topic in topics.values():
        lines.append("- " + markdown(topic["problem"]))
    if bundle["overview"].get("themes") and metadata["mode"] == "recap":
        lines += ["", "## 方向导读", ""]
        for theme in bundle["overview"]["themes"]:
            lines += ["### " + markdown(topics[theme["topic_id"]]["problem"]), "", markdown(theme["text"]), "",
                      "依据：" + "、".join(link(records[pid]["title"], records[pid]["url"]) for pid in theme["paper_ids"]), ""]
    lines += ["", f"## 优先阅读（{len(selected)} 篇）", "",
              "| ID | 论文 | 关联 | 推荐理由 |", "|---|---|---|---|"]
    for paper in selected:
        item = paper["assessment"]
        lines.append(f"| [{paper['display_id']}](index.html#{paper['display_id']}) | {link(paper['title'], paper['url'])} | {RELATIONS[item['relation']]} | {markdown(short_reason(item['reason']))} |")
    if not selected:
        lines += ["", "暂无已确认相关论文；请查看待核查记录。"]
    if metadata["mode"] == "recap":
        lines += ["", "## 完整相关目录", ""]
        for topic in topics.values():
            members = [paper for paper in all_related if topic["id"] in paper["assessment"]["topic_ids"]]
            lines += ["### " + markdown(topic["problem"]), ""]
            for paper in members:
                lines.append(f"- [{paper['display_id']}](index.html#{paper['display_id']}) · {link(paper['title'], paper['url'])}")
            if not members:
                lines.append("当前没有已确认相关论文。")
            lines.append("")
    lines += ["", "## 阅读建议与依据", ""]
    question_map = {item["paper_id"]: item["questions"] for item in bundle["overview"].get("attendance_questions", [])}
    for paper in (selected if metadata["mode"] == "attend" else all_related):
        detail = paper_details(paper, paper["assessment"], topics, show_schedule=metadata["mode"] == "attend")
        detail[0] = f"### {paper['display_id']} · {markdown(paper['title'])}"
        lines += detail
        if metadata["mode"] == "attend" and question_map.get(paper["id"]):
            lines += ["交流问题：", ""] + ["- " + markdown(question) for question in question_map[paper["id"]]] + [""]
    lines += ["## 范围与来源", "", markdown(metadata.get("scope_note") or "未提供范围说明。"), "",
              f"缺少摘要 {stats['missing_abstract']} 篇；已排除 {stats['excluded']} 篇。待核查、排除和未处理记录可在 HTML 按状态查看，完整判断保存在 JSON 中。", ""]
    if metadata.get("source_url"):
        lines += [link("官方论文列表", metadata["source_url"]), ""]
    if metadata.get("retrieved_at"):
        lines += ["资料获取时间：" + markdown(metadata["retrieved_at"]), ""]
    return "\n".join(lines).rstrip() + "\n"


def csv_text(value):
    value = str(value) if value is not None else ""
    # Spreadsheet readers must interpret source text as text, not formulas.
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def render_export_csv(bundle):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["ID", "原始论文ID", "论文标题", "作者", "研究方向", "筛选状态", "阅读优先级", "关联类型",
                     "相关性", "推荐理由", "重点阅读", "证据状态", "论文链接", "PDF链接", "展示时间", "时区", "场次", "地点", "日程来源", "阅读状态", "个人备注"])
    order = {paper_id: index for index, paper_id in enumerate(bundle["metadata"]["recommended_ids"])}
    records = [paper for paper in bundle["papers"] if paper["assessment"] and paper["assessment"]["decision"] in {"include", "pending"}]
    records.sort(key=lambda paper: (paper["assessment"]["decision"] != "include", order.get(paper["id"], len(order)), paper["id"]))
    for paper in records:
        item = paper["assessment"]
        schedule = paper.get("presentation") or {}
        if not schedule.get("confirmed"):
            schedule = {}
        row = [paper["display_id"], paper["id"], paper["title"], "；".join(paper["authors"]), "；".join(paper["topic_labels"]),
               "相关" if item["decision"] == "include" else "待核查", item["priority"], RELATIONS[item["relation"]],
               RELEVANCE[item["relevance"]], item["reason"], item["reading_focus"], EVIDENCE_STATUS[item["evidence_status"]],
               paper.get("url"), paper.get("pdf_url"), schedule.get("time"), schedule.get("timezone"), schedule.get("session"), schedule.get("location"), schedule.get("source_url"), "未读", ""]
        writer.writerow([csv_text(value) for value in row])
    return stream.getvalue()


def export_documents(papers, profile, data, out_dir, mode="recap", top_k=20, overview=None):
    bundle = build_output_bundle(papers, profile, data, mode, top_k, overview)
    module_path = Path(__file__).with_name("output_html.py")
    spec = importlib.util.spec_from_file_location("conference_output_html", module_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    contents = {"report.md": render_export_markdown(bundle), "papers.csv": render_export_csv(bundle),
                "results.json": json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", "index.html": renderer.render_html(bundle)}
    destination = Path(out_dir)
    require(not destination.exists() or (destination.is_dir() and not any(destination.iterdir())),
            f"Output directory must be empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in contents.items():
        (destination / name).write_text(content, encoding="utf-8-sig" if name.endswith(".csv") else "utf-8")
    return bundle["coverage"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="Normalize and batch every paper; output directory must be empty")
    prepare_parser.add_argument("--papers", required=True)
    prepare_parser.add_argument("--out-dir", required=True)
    prepare_parser.add_argument("--batch-size", type=int, default=40)
    merge_parser = commands.add_parser("merge", help="Merge assessment batches; duplicate paper IDs are errors")
    merge_parser.add_argument("--inputs", nargs="+", required=True)
    merge_parser.add_argument("--output", required=True)
    for name in ("validate", "report", "export"):
        command = commands.add_parser(name)
        command.add_argument("--papers", required=True)
        command.add_argument("--profile", required=True)
        command.add_argument("--assessments", required=True)
        if name == "report":
            command.add_argument("--mode", choices=("attend", "recap"), default="recap")
            command.add_argument("--top-k", type=int, default=20)
            command.add_argument("--include-excluded", action="store_true", help="Append every excluded paper and its evidence for audit")
            command.add_argument("--output", required=True)
        elif name == "export":
            command.add_argument("--mode", choices=("attend", "recap"), default="recap")
            command.add_argument("--top-k", type=int, default=20)
            command.add_argument("--out-dir", required=True, help="Fresh directory for exactly four output documents")
            command.add_argument("--overview", help="Optional evidence-backed guide, themes and discussion questions JSON")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            print(json.dumps(prepare(args.papers, args.out_dir, args.batch_size), ensure_ascii=False))
        elif args.command == "merge":
            print(f"Merged {merge_assessments(args.inputs, args.output)} assessments.")
        else:
            papers = read_papers(args.papers)
            profile = read_json(args.profile)
            data = read_json(args.assessments)
            if args.command == "validate":
                assessments = validate_assessments(papers, profile, data)
                print(json.dumps(coverage(papers, assessments), ensure_ascii=False))
            elif args.command == "export":
                stats = export_documents(papers, profile, data, args.out_dir, args.mode, args.top_k,
                                         read_json(args.overview) if args.overview else None)
                print(json.dumps(stats, ensure_ascii=False))
                print(f"Exported report.md, papers.csv, results.json and index.html to {args.out_dir}")
            else:
                Path(args.output).write_text(render_report(papers, profile, data, args.mode, args.top_k, args.include_excluded), encoding="utf-8")
                print(f"Report written: {args.output}")
    except (DataError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
