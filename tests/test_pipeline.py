"""Behavioral tests for coverage, provenance, status and reporting invariants."""

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "conference-paper-search" / "scripts" / "paper_pipeline.py"
SPEC = importlib.util.spec_from_file_location("paper_pipeline", SCRIPT)
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def paper(paper_id="p1", **updates):
    record = {
        "id": paper_id, "title": f"Paper {paper_id}", "authors": ["Author A"],
        "abstract": "We evaluate image language hallucinations.\nOur benchmark uses grounded questions.",
        "url": f"https://conference.example/paper/{paper_id}", "acceptance": "accepted",
    }
    record.update(updates)
    return record


def papers(*records, **updates):
    envelope = {
        "conference": "Test Conference", "year": 2026, "track": "main",
        "source_url": "https://conference.example/list", "retrieved_at": "2026-10-14",
        "scope_status": "partial", "scope_note": "Test sample; not a complete conference.",
        "papers": list(records) or [paper()],
    }
    envelope.update(updates)
    return pipeline.normalize_papers(envelope)


def profile():
    return {
        "owner": "personal", "topics": [{
            "id": "t1", "problem": "视觉语言模型幻觉评测", "focus": ["评测"],
            "constraints": [], "exclude": [], "relation_scope": ["direct", "method_transfer"],
            "priority": "primary", "provenance": [{"kind": "user", "reference": "用户本次描述"}],
        }], "representative_papers": [], "notes": "用户可修改",
    }


def assessment(paper_id="p1", **updates):
    value = {
        "paper_id": paper_id, "decision": "include", "relevance": "high",
        "relation": "direct", "topic_ids": ["t1"], "reason": "摘要研究幻觉评测。",
        "reading_focus": "评测任务与数据构建", "differences": ["需要核查任务范围"],
        "evidence": [{"source_id": "abstract", "quote": "We evaluate image language hallucinations."}],
        "uncertainties": ["正文实验未读取"], "evidence_status": "limited", "priority": 1,
    }
    value.update(updates)
    return value


def results(*records):
    return {"assessments": list(records) or [assessment()]}


class PreparationTests(unittest.TestCase):
    def test_batches_cover_every_paper_and_preserve_scope(self):
        records = [paper(f"p{i}", abstract=None if i == 3 else "Abstract", acceptance="unknown" if i == 4 else "accepted") for i in range(5)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            pipeline.write_json(source, papers(*records))
            destination = root / "prepared"
            stats = pipeline.prepare(source, destination, 2)
            batches = [pipeline.read_json(path) for path in sorted(destination.glob("batch-*.json"))]
            self.assertEqual([p["id"] for batch in batches for p in batch["papers"]], [f"p{i}" for i in range(5)])
            self.assertEqual([len(batch["papers"]) for batch in batches], [2, 2, 1])
            self.assertEqual(stats["missing_abstract"], 1)
            self.assertEqual(stats["acceptance"]["unknown"], 1)
            self.assertTrue(all(batch["scope_note"] == "Test sample; not a complete conference." for batch in batches))
            with self.assertRaisesRegex(pipeline.DataError, "must be empty"):
                pipeline.prepare(source, destination, 2)

    def test_invalid_batch_size_does_not_create_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "output"
            with self.assertRaisesRegex(pipeline.DataError, "positive"):
                pipeline.prepare("unused.json", destination, 0)
            self.assertFalse(destination.exists())

    def test_same_title_does_not_merge_distinct_publications(self):
        data = papers(paper("p1", title="Shared title"), paper("p2", title="Shared title"))
        self.assertEqual(len(data["papers"]), 2)
        self.assertEqual(data["duplicates"], [])

    def test_canonical_url_dedup_enriches_missing_abstract(self):
        first = paper("p1", title="Shared", abstract=None, url="HTTPS://Conference.Example:443/paper/a#top")
        second = paper("p2", title="Shared", url="https://conference.example/paper/a")
        data = papers(first, second)
        self.assertEqual(len(data["papers"]), 1)
        retained = data["papers"][0]
        self.assertEqual(retained["id"], "p1")
        self.assertTrue(retained["abstract"])
        self.assertIn("abstract", {source["id"] for source in retained["sources"]})
        self.assertEqual(data["duplicates"][0]["retained_id"], "p1")
        self.assertEqual(pipeline.normalize_papers(data), data)

    def test_conflicting_duplicates_fail_instead_of_overwriting(self):
        with self.assertRaisesRegex(pipeline.DataError, "conflicting acceptance"):
            papers(paper(), paper(acceptance="withdrawn"))
        with self.assertRaisesRegex(pipeline.DataError, "conflicting abstracts"):
            papers(paper(), paper(abstract="Different abstract"))
        with self.assertRaisesRegex(pipeline.DataError, "different existing records"):
            papers(paper("p1", title="Shared"), paper("p2", title="Shared"),
                   paper("p1", title="Shared", url="https://conference.example/paper/p2"))

    def test_raw_import_defaults_unknown_without_fabricated_urls(self):
        data = pipeline.normalize_papers([{"title": "Shared"}, {"title": "Shared"}, {"title": "Accepted", "acceptance": "accepted"}])
        self.assertEqual(data["scope_status"], "unknown")
        self.assertEqual(len(data["papers"]), 3)
        self.assertEqual([item["acceptance"] for item in data["papers"]], ["unknown", "unknown", "accepted"])
        self.assertTrue(all(item["url"] is None for item in data["papers"]))
        self.assertEqual(pipeline.coverage(data)["title_only"], 3)

    def test_csv_supports_bom_and_author_lists(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "papers.csv"
            source.write_text('id,title,authors,abstract,url,acceptance\np1,Title,Alice;Bob,Abstract,https://conference.example/p1,accepted\np2,Other,,,,\n', encoding="utf-8-sig")
            data = pipeline.read_papers(source)
            self.assertEqual(data["papers"][0]["authors"], ["Alice", "Bob"])
            self.assertEqual(data["papers"][0]["acceptance"], "accepted")
            self.assertEqual(data["papers"][1]["acceptance"], "unknown")
            self.assertIsNone(data["papers"][1]["abstract"])


class EvidenceTests(unittest.TestCase):
    def assert_invalid(self, data, expression, paper_data=None, interest=None):
        with self.assertRaisesRegex(pipeline.DataError, expression):
            pipeline.validate_assessments(paper_data or papers(), interest or profile(), data)

    def test_quote_whitespace_normalization_preserves_exact_words(self):
        quote = "hallucinations.  Our\tbenchmark uses grounded questions."
        validated = pipeline.validate_assessments(papers(), profile(), results(assessment(evidence=[{"source_id": "abstract", "quote": quote}])))
        self.assertIn("p1", validated)
        self.assert_invalid(results(assessment(evidence=[{"source_id": "abstract", "quote": "Our benchmark outperforms all previous methods."}])), "absent from source")

    def test_unknown_source_and_paper_ids_fail(self):
        self.assert_invalid(results(assessment(evidence=[{"source_id": "body", "quote": "Example"}])), "unknown source id")
        self.assert_invalid(results(assessment("not-p1")), "unknown paper id")
        self.assert_invalid(results(assessment(topic_ids=["not-t1"])), "unknown topic id")

    def test_duplicate_assessments_and_source_ids_fail(self):
        self.assert_invalid(results(assessment(), assessment()), "duplicate assessment")
        source = {"id": "body", "kind": "full_text", "text": "Text", "url": "https://conference.example/p1"}
        with self.assertRaisesRegex(pipeline.DataError, "duplicate source id"):
            papers(paper(sources=[source, source]))

    def test_nonaccepted_papers_cannot_enter_recommendations(self):
        for acceptance in ("unknown", "withdrawn", "rejected"):
            with self.subTest(acceptance=acceptance):
                self.assert_invalid(results(), "pending|only accepted", papers(paper(acceptance=acceptance)))
        pending = assessment(decision="pending", evidence=[], evidence_status="missing")
        validated = pipeline.validate_assessments(papers(paper(acceptance="unknown")), profile(), results(pending))
        self.assertEqual(validated["p1"]["relevance"], "high")

    def test_final_decisions_need_real_evidence(self):
        for decision in ("include", "exclude"):
            with self.subTest(decision=decision):
                self.assert_invalid(results(assessment(decision=decision, evidence=[])), "requires source evidence")
                self.assert_invalid(results(assessment(decision=decision, evidence_status="missing")), "cannot have missing evidence")
        title_only = papers(paper(abstract=None))
        boundary_exclusion = assessment(decision="exclude", topic_ids=[], relation=None,
                                        reason="用户明确排除这个任务。", reading_focus="",
                                        evidence=[{"source_id": "title", "quote": "Paper p1"}])
        self.assertIn("p1", pipeline.validate_assessments(title_only, profile(), results(boundary_exclusion)))

    def test_relation_must_be_allowed_by_a_matched_topic(self):
        self.assert_invalid(results(assessment(relation="adjacent")), "outside matched topic")
        interest = profile()
        second = copy.deepcopy(interest["topics"][0])
        second.update(id="t2", relation_scope=["adjacent"])
        interest["topics"].append(second)
        self.assert_invalid(results(assessment(relation="adjacent", topic_ids=["t1", "t2"])),
                            "outside matched topic t1", interest=interest)
        self.assertIn("p1", pipeline.validate_assessments(papers(), interest,
                      results(assessment(relation="adjacent", topic_ids=["t2"]))))

    def test_malformed_types_fail_with_field_context(self):
        self.assert_invalid(results(assessment(priority=True)), "priority")
        self.assert_invalid(results(assessment(differences="none")), "differences")
        self.assert_invalid(results(assessment(evidence=[{"source_id": "abstract", "quote": 1}])), "quote")
        with self.assertRaisesRegex(pipeline.DataError, "text"):
            papers(paper(sources=[{"id": "body", "kind": "full_text", "text": 17, "url": "https://conference.example/p1"}]))
        self.assert_invalid(results(assessment(reason=" ")), "reason")
        self.assert_invalid(results(assessment(reading_focus=" ")), "reading_focus")

    def test_missing_assessments_remain_unprocessed(self):
        data = papers(paper(), paper("p2", abstract=None))
        validated = pipeline.validate_assessments(data, profile(), results())
        stats = pipeline.coverage(data, validated)
        self.assertEqual(stats["unprocessed"], 1)
        self.assertEqual(stats["excluded"], 0)
        self.assertEqual(stats["pending"], 0)
        self.assertEqual(stats["title_only"], 1)


class ReportTests(unittest.TestCase):
    def test_recap_keeps_all_recommendations_beyond_top_k(self):
        data = papers(paper(), paper("p2"))
        report = pipeline.render_report(data, profile(), results(assessment(), assessment("p2", priority=2)), top_k=1)
        self.assertIn("### Paper p1", report)
        self.assertIn("### Paper p2", report)
        self.assertIn("覆盖尚未确认完整", report)
        self.assertIn("摘要研究幻觉评测", report)
        self.assertIn("正文实验未读取", report)
        self.assertIn("We evaluate image language hallucinations", report)

    def test_attend_uses_only_confirmed_schedule_and_limits_selected_papers(self):
        confirmed = {"confirmed": True, "source_url": "https://conference.example/schedule", "time": "2026-12-01 10:00", "timezone": "Asia/Shanghai", "session": "Poster 1", "location": "Hall A"}
        unconfirmed = {"confirmed": False, "time": "Imagined time", "session": "Hidden Fake Session", "location": "Hidden Room"}
        data = papers(paper(presentation=confirmed), paper("p2", presentation=unconfirmed))
        report = pipeline.render_report(data, profile(), results(assessment(), assessment("p2", priority=2)), mode="attend", top_k=1)
        self.assertIn("Asia/Shanghai", report)
        self.assertIn("https://conference.example/schedule", report)
        self.assertIn("Hall A", report)
        self.assertNotIn("### Paper p2", report)
        self.assertNotIn("https://conference.example/paper/p2", report)
        self.assertNotIn("Hidden Fake Session", report)
        self.assertNotIn("Hidden Room", report)

    def test_exclusion_audit_is_optional_and_assessments_keep_evidence(self):
        data = papers(paper(), paper("p2"))
        decisions = results(assessment(), assessment("p2", decision="exclude", topic_ids=[], relation=None))
        normal = pipeline.render_report(data, profile(), decisions)
        self.assertNotIn("https://conference.example/paper/p2", normal)
        self.assertEqual(pipeline.coverage(data, pipeline.validate_assessments(data, profile(), decisions))["excluded"], 1)
        audit = pipeline.render_report(data, profile(), decisions, include_excluded=True)
        self.assertIn("https://conference.example/paper/p2", audit)
        self.assertEqual(decisions["assessments"][1]["evidence"][0]["source_id"], "abstract")

    def test_partial_confirmed_schedule_does_not_invent_missing_details(self):
        partial = {"confirmed": True, "source_url": "https://conference.example/schedule", "time": "10:00", "timezone": None, "session": "Poster 1", "location": ""}
        report = pipeline.render_report(papers(paper(presentation=partial)), profile(), results(), mode="attend")
        self.assertIn("Poster 1", report)
        self.assertIn("暂不能据此排程", report)
        self.assertNotIn("地点：", report)
        with self.assertRaisesRegex(pipeline.DataError, "source_url"):
            papers(paper(presentation={"confirmed": True, "session": "Unverified"}))

    def test_pending_unknown_and_unprocessed_are_visible(self):
        data = papers(paper(), paper("p2", abstract=None, acceptance="unknown"), paper("p3"))
        pending = assessment("p2", decision="pending", evidence_status="missing", evidence=[], reason="录用未核实")
        report = pipeline.render_report(data, profile(), results(assessment(), pending))
        self.assertIn("录用未核实", report)
        self.assertIn("尚未处理", report)
        self.assertIn("待核查 1 篇；未处理 1 篇", report)

    def test_unsafe_urls_rejected_and_markdown_injection_escaped(self):
        with self.assertRaisesRegex(pipeline.DataError, "http"):
            papers(paper(url="javascript:alert(1)"))
        with self.assertRaisesRegex(pipeline.DataError, "credentials"):
            papers(paper(url="https://user:pass@conference.example/p1"))
        title = "[Click](javascript:alert(1)) | <script>danger</script>\n# injected"
        report = pipeline.render_report(papers(paper(title=title)), profile(), results())
        self.assertIn("\\|", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertNotIn("\n# injected", report)
        self.assertNotIn("<script>", report)


class MergeAndCliTests(unittest.TestCase):
    def test_merge_is_ordered_and_duplicate_failure_preserves_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second, destination = root / "one.json", root / "two.json", root / "merged.json"
            pipeline.write_json(first, results(assessment("p2")))
            pipeline.write_json(second, results(assessment("p1")))
            self.assertEqual(pipeline.merge_assessments([first, second], destination), 2)
            self.assertEqual([a["paper_id"] for a in pipeline.read_json(destination)["assessments"]], ["p2", "p1"])
            before = destination.read_bytes()
            with self.assertRaisesRegex(pipeline.DataError, "Duplicate"):
                pipeline.merge_assessments([first, first], destination)
            self.assertEqual(destination.read_bytes(), before)

    def test_cli_prepare_merge_validate_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, interest, judgments = root / "source.json", root / "profile.json", root / "part.json"
            pipeline.write_json(source, papers())
            pipeline.write_json(interest, profile())
            pipeline.write_json(judgments, results())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(pipeline.main(["prepare", "--papers", str(source), "--out-dir", str(root / "prepared")]), 0)
                self.assertEqual(pipeline.main(["merge", "--inputs", str(judgments), "--output", str(root / "merged.json")]), 0)
                args = ["--papers", str(root / "prepared" / "papers.json"), "--profile", str(interest), "--assessments", str(root / "merged.json")]
                self.assertEqual(pipeline.main(["validate"] + args), 0)
                self.assertEqual(pipeline.main(["report"] + args + ["--mode", "attend", "--output", str(root / "report.md")]), 0)
            self.assertTrue((root / "report.md").exists())
            errors = io.StringIO()
            pipeline.write_json(root / "bad.json", results(assessment("invalid")))
            with contextlib.redirect_stderr(errors):
                self.assertEqual(pipeline.main(["validate", "--papers", str(source), "--profile", str(interest), "--assessments", str(root / "bad.json")]), 2)
            self.assertIn("unknown paper id", errors.getvalue())
            self.assertNotIn("Traceback", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
