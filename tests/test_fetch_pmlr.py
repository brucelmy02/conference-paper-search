"""Offline parser and provenance tests; no network access required."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "skills" / "conference-paper-search" / "scripts" / "fetch_pmlr.py"
SPEC = importlib.util.spec_from_file_location("fetch_pmlr", MODULE_PATH)
fetch_pmlr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch_pmlr)
BASE = "https://proceedings.mlr.press/v235/"
VOLUME_HTML = """<!doctype html><html><head>
<title>Proceedings of Machine Learning Research | ICML</title>
<link rel="canonical" href="https://proceedings.mlr.press/v235/">
</head><body><h2>Volume 235: International Conference on Machine Learning, 21-27 July 2024, Vienna, Austria</h2>
<div class="paper"><p class="title">A &amp; B: <i>A method</i></p>
<p class="details"><span class="authors">Ada Doe,&nbsp;Bob Doe</span></p>
<p class="links">[<a href="paper24a.html">abs</a>][<a href="https://example.org/paper.pdf">Download PDF</a>]</p></div>
<div class="paper"><p class="title">Missing detail</p><a href="paper24b.html">abs</a></div>
</body></html>"""
DETAIL_HTML = """<html><head>
<meta name="citation_title" content="A &amp; B: A method">
<meta name="citation_author" content="Ada Doe"><meta name="citation_author" content="Bob Doe">
<meta name="citation_abstract_html_url" content="https://proceedings.mlr.press/v235/paper24a.html">
<meta name="citation_pdf_url" content="https://example.org/final.pdf">
<meta name="twitter:description" content="truncated...">
</head><body><div id="abstract" class="abstract">A complete <em>abstract</em> &amp; evidence.<p>Second paragraph.</p></div></body></html>"""


class FetchPmlrTests(unittest.TestCase):
    def test_validate_rejects_other_domain_and_nonvolume(self):
        for url in ["https://proceedings.mlr.press.evil.org/v235/", "http://proceedings.mlr.press/v235/",
                    "https://proceedings.mlr.press/v235/paper24a.html", "https://proceedings.mlr.press/v235/?x=1",
                    "https://user@proceedings.mlr.press/v235/", "https://proceedings.mlr.press:443/v235/"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                fetch_pmlr.validate_volume_url(url)

    def test_volume_metadata_is_from_official_heading(self):
        result = fetch_pmlr.parse_volume(VOLUME_HTML, BASE)
        self.assertEqual((result["conference"], result["year"]), ("International Conference on Machine Learning", 2024))
        self.assertEqual(result["papers"][0]["id"], "pmlr:235:paper24a")
        self.assertEqual(result["papers"][0]["title"], "A & B: A method")
        self.assertEqual(result["papers"][0]["authors"], ["Ada Doe", "Bob Doe"])
        self.assertEqual(result["papers"][0]["acceptance"], "accepted")

    def test_wrong_volume_and_missing_identity_rejected(self):
        for html in [VOLUME_HTML.replace("Volume 235:", "Volume 999:"),
                     VOLUME_HTML.replace("Proceedings of Machine Learning Research", "Some submission list")]:
            with self.subTest(html=html), self.assertRaises(ValueError):
                fetch_pmlr.parse_volume(html, BASE)

    def test_abstract_uses_full_text_with_citation_source(self):
        paper = fetch_pmlr.parse_volume(VOLUME_HTML, BASE)["papers"][0]
        result = fetch_pmlr.parse_paper(DETAIL_HTML, paper, "235")
        self.assertIn("complete abstract & evidence.", result["abstract"])
        self.assertIn("evidence. Second paragraph.", result["abstract"])
        self.assertNotIn("truncated", result["abstract"])
        self.assertEqual(result["sources"][0]["text"], result["abstract"])
        self.assertEqual(result["sources"][0]["locator"], "Abstract")
        self.assertEqual(result["pdf_url"], "https://example.org/final.pdf")

    def test_failed_detail_preserves_accepted_list_record(self):
        def get(url):
            if url == BASE:
                return VOLUME_HTML
            if url.endswith("paper24a.html"):
                return DETAIL_HTML
            raise RuntimeError("offline simulated timeout")
        with patch("sys.stderr"):
            result = fetch_pmlr.fetch_volume(BASE, fetcher=get)
        self.assertEqual(len(result["papers"]), 2)
        failed = result["papers"][1]
        self.assertEqual(failed["title"], "Missing detail")
        self.assertIsNone(failed["abstract"])
        self.assertEqual(failed["sources"], [])
        self.assertIn("simulated timeout", failed["error"])
        self.assertIn("volume 235 only", result["scope_note"])

    def test_limit_is_explicit_and_positive(self):
        with patch("sys.stderr"):
            result = fetch_pmlr.fetch_volume(BASE, limit=1, fetcher=lambda url: VOLUME_HTML if url == BASE else DETAIL_HTML)
        self.assertEqual(len(result["papers"]), 1)
        self.assertIn("--limit 1", result["scope_note"])
        with self.assertRaises(ValueError):
            fetch_pmlr.fetch_volume(BASE, limit=0, fetcher=lambda url: VOLUME_HTML)

    def test_foreign_detail_is_not_imported_as_accepted(self):
        html = VOLUME_HTML.replace('href="paper24a.html"', 'href="https://example.org/paper24a.html"')
        result = fetch_pmlr.parse_volume(html, BASE)
        self.assertEqual(len(result["papers"]), 1)
        self.assertEqual(result["papers"][0]["title"], "Missing detail")
        self.assertTrue(result["warnings"])

    def test_mismatched_citation_and_missing_abstract(self):
        paper = fetch_pmlr.parse_volume(VOLUME_HTML, BASE)["papers"][0]
        with self.assertRaises(ValueError):
            fetch_pmlr.parse_paper(DETAIL_HTML.replace("v235/paper24a", "v999/paper24a"), paper, "235")
        result = fetch_pmlr.parse_paper(DETAIL_HTML.replace('id="abstract"', 'id="other"'), paper, "235")
        self.assertIsNone(result["abstract"])
        self.assertIn("missing", result["error"])

    def test_redirect_guard_rejects_external_host(self):
        guard = fetch_pmlr.OfficialRedirects()
        with self.assertRaises(ValueError):
            guard.redirect_request(None, None, 302, "Found", {}, "https://example.org/v235/")


if __name__ == "__main__":
    unittest.main()
