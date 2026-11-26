import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "bin" / "memo"


class MemoTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.bot = Path(temp.name)
        self.call("memory", "init")

    def call(self, *args, cwd=None, code=0):
        result = subprocess.run([sys.executable, str(CLI), *args],
                                cwd=cwd or self.bot, capture_output=True,
                                text=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def seed(self, count):
        path = self.bot / ".memory" / "entries.jsonl"
        path.write_text("".join(json.dumps({"id": i, "date": "2026-11-25",
                                            "text": f"Original entry {i}"}) + "\n"
                                for i in range(count)), encoding="utf-8")
        return path

    def settle(self):
        order = []
        while True:
            job = self.call("memory", "compress")
            if "Nothing left" in job:
                return order
            name = re.search(r"Compress #(\d+-\d+)", job)[1]
            self.assertNotIn(name, order)
            order.append(name)
            self.call("memory", "compress", name, f"Summary {name}")

    def test_journal_nested_scope_and_corrections(self):
        child = self.bot / "child"
        child.mkdir()
        self.call("memory", "init", cwd=child, code=1)
        self.call("memory", "note", "--tag", "decision", "deadline Friday", cwd=child)
        self.call("memory", "amend", "0", "deadline Thursday")
        self.assertIn("Amends #0: deadline Thursday",
                      self.call("memory", "recall", "Friday"))
        self.assertIn("deadline Friday", self.call("memory", "show", "0"))
        self.assertIn("You are awake", self.call("memory", "wake", cwd=child))

    def test_journal_concurrent_dedup(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as threads:
            results = list(threads.map(
                lambda _: self.call("memory", "note", "same event"), range(12)))
        self.assertEqual(sum("Saved as" in r for r in results), 1)
        self.assertEqual(sum("Already recorded" in r for r in results), 11)

    def test_journal_wake_covers_full_history_and_keeps_originals(self):
        path = self.seed(113)
        original = path.read_bytes()
        self.assertIn("Cannot wake", self.call("memory", "wake", code=1))
        self.settle()
        rows = [re.match(r"#(\d+)(?:-(\d+))? ", row)
                for row in self.call("memory", "wake").splitlines()]
        rows = [tuple(int(x) for x in (m[1], m[2] or m[1])) for m in rows if m]
        self.assertEqual(len(rows), 32)
        self.assertGreater(rows[0][1] - rows[0][0], 1)
        self.assertEqual(rows[-1], (112, 112))
        self.assertEqual([i for lo, hi in rows for i in range(lo, hi + 1)], list(range(113)))
        self.assertEqual(path.read_bytes(), original)
        self.assertIn("Original entry 7", self.call("memory", "show", "7"))

    def test_journal_large_summary_uses_child_summaries(self):
        self.seed(4096)
        for _ in range(512):
            job = self.call("memory", "compress")
            match = re.search(r"Compress #(\d+)-(\d+)", job)
            self.assertIsNotNone(match)
            lo, hi = (int(n) for n in match.groups())
            if hi - lo + 1 > 16:
                mid = (lo + hi + 1) // 2
                self.assertIn(f"Summary {lo}-{mid - 1}", job)
                self.assertIn(f"Summary {mid}-{hi}", job)
                self.assertNotIn("Original entry", job)
                break
            self.assertIn("Original entry", job)
            self.call("memory", "compress", f"{lo}-{hi}", f"Summary {lo}-{hi}")
        else:
            self.fail("no hierarchical compression job found")

    def test_journal_byte_limit_includes_prefix(self):
        self.assertIn("280 UTF-8 bytes",
                      self.call("memory", "note", "--subject", "test", "ě" * 140, code=1))

    def test_journal_missing_optional_index(self):
        self.call("memory", "note", "test")
        self.assertIn("Indexed 0/1", self.call("memory", "index", "--status"))
        self.assertIn("no semantic index",
                      self.call("memory", "recall", "--semantic", "test", code=1))


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.bot = self.home / "bot"
        self.bot.mkdir()
        self.vault = self.make_vault()

    def call(self, *args, cwd=None, code=0, env=None):
        result = subprocess.run([sys.executable, str(CLI), *args],
                                cwd=cwd or self.bot, capture_output=True,
                                text=True, timeout=10,
                                env={**os.environ, **(env or {})})
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def make_vault(self):
        vault = self.home / "knowledge"
        for folder in ("sources", "topics", "inbox", "ideas"):
            (vault / folder).mkdir(parents=True)
        (vault / "inbox" / "draft.md").write_text("draft", encoding="utf-8")
        (vault / "ideas" / "idea.md").write_text("idea", encoding="utf-8")
        (vault / "topics" / "ppc.md").write_text("---\ntype: topic\n---\n# PPC\n",
                                                encoding="utf-8")
        cards = [
            ("openai--chatgpt-ads-44", "ChatGPT Ads in 44 countries", "new",
             "2026-11-12", ["chatgpt-ads", "ppc"],
             "Aleph is the exclusive reseller for 44 countries."),
            ("growth-memo--meta-analysis", "AI search meta analysis", "read",
             "2026-11-16", ["ai-search", "seo"],
             "CTR on position 1 with AI Overviews fell 58% relatively."),
            ("n8n--meet-nod", "Meet Nod, a standalone personal agent", "new",
             "2026-11-10", ["automation", "n8n"], "A local agent from n8n labs."),
        ]
        for name, title, status, captured, topics, body in cards:
            tags = ", ".join(f'"[[{t}]]"' for t in topics)
            (vault / "sources" / f"{name}.md").write_text(
                f"---\ntype: article\ntitle: \"{title}\"\nstatus: {status}\n"
                f"captured: {captured}\ntopics: [{tags}]\n---\n\n"
                f"# {title}\n\n{body}\n", encoding="utf-8")
        return vault

    def test_wake_field_brief_filters_the_chosen_vault(self):
        out = self.call("knowledge", "wake", "chatgpt-ads", "ppc",
                        "--dir", self.vault)
        self.assertIn("1 source(s) match", out)
        self.assertIn("openai--chatgpt-ads-44", out)
        self.assertNotIn("growth-memo--meta-analysis", out)
        self.assertIn("Routers: topics/ppc.md", out)
        self.assertIn("You are briefed.", out)
        every = self.call("knowledge", "wake", "--dir", self.vault)
        self.assertIn("3 sources, 1 ideas, 1 in inbox", every)
        self.assertIn("Field: whole vault — 3 source(s) match", every)

    def test_vault_selection_env_and_config(self):
        out = self.call("knowledge", "wake", "ppc",
                        env={"KNOWLEDGE_DIR": str(self.vault)})
        self.assertIn("You are briefed.", out)
        config = self.home / "memo-config.json"
        config.write_text(json.dumps(
            {"knowledge_dir": str(self.vault)}), encoding="utf-8")
        out = self.call("knowledge", "wake", "ppc",
                        env={"MEMO_CONFIG": str(config), "KNOWLEDGE_DIR": ""})
        self.assertIn("You are briefed.", out)
        # a bad selection is a clear error, never a guess
        self.assertIn("not a knowledge vault",
                      self.call("knowledge", "wake", "--dir", self.home, code=1))
        self.assertIn("no knowledge vault selected",
                      self.call("knowledge", "wake",
                                env={"KNOWLEDGE_DIR": "", "MEMO_CONFIG": "/nonexistent"},
                                code=1))

    def test_recall_regex_and_filters(self):
        env = {"KNOWLEDGE_DIR": str(self.vault)}
        out = self.call("knowledge", "recall", "reseller", env=env)
        self.assertIn("openai--chatgpt-ads-44", out)
        self.assertIn("1 card(s)", out)
        out = self.call("knowledge", "recall", "", "--topic", "ai-search", env=env)
        self.assertIn("growth-memo--meta-analysis", out)
        self.assertNotIn("n8n--meet-nod", out)
        out = self.call("knowledge", "recall", "", "--status", "read", "-n", "1", env=env)
        self.assertIn("(read", out)

    def test_recall_fuzzy_survives_mangled_words(self):
        out = self.call("knowledge", "recall", "--fuzzy", "meet nod stanalone agent",
                        env={"KNOWLEDGE_DIR": str(self.vault)})
        self.assertIn("n8n--meet-nod", out)

    def test_show_prints_card_not_frontmatter(self):
        out = self.call("knowledge", "show", "growth-memo--meta-analysis",
                        env={"KNOWLEDGE_DIR": str(self.vault)})
        self.assertIn("AI search meta analysis", out)
        self.assertIn("captured: 2026-11-16", out)
        self.assertIn("[ai-search, seo]", out)
        self.assertIn("position 1", out)
        self.assertFalse(out.lstrip().startswith("---"))

    def test_semantic_contract_without_index(self):
        env = {"KNOWLEDGE_DIR": str(self.vault)}
        self.assertIn("no semantic index",
                      self.call("knowledge", "recall", "--semantic", "resellers",
                                env=env, code=1))
        self.assertIn("No semantic index",
                      self.call("knowledge", "index", "--status", env=env))
        self.assertIn("not a knowledge vault",
                      self.call("knowledge", "wake", "--dir", self.bot / "nowhere",
                                code=1))


if __name__ == "__main__":
    unittest.main()
