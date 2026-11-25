import concurrent.futures
import json
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
        self.call("init")

    def call(self, *args, cwd=None, code=0):
        result = subprocess.run([sys.executable, str(CLI), *args],
                                cwd=cwd or self.bot, capture_output=True,
                                text=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def seed(self, count):
        path = self.bot / ".memo" / "entries.jsonl"
        path.write_text("".join(json.dumps({"id": i, "date": "2026-11-25",
                                            "text": f"Original entry {i}"}) + "\n"
                                for i in range(count)), encoding="utf-8")
        return path

    def settle(self):
        order = []
        while True:
            job = self.call("compress")
            if "Nothing left" in job:
                return order
            name = re.search(r"Compress #(\d+-\d+)", job)[1]
            self.assertNotIn(name, order)
            order.append(name)
            self.call("compress", name, f"Summary {name}")

    def test_nested_scope_and_corrections(self):
        child = self.bot / "child"
        child.mkdir()
        self.call("init", cwd=child, code=1)
        self.call("note", "--tag", "decision", "deadline Friday", cwd=child)
        self.call("amend", "0", "deadline Thursday")
        self.assertIn("Amends #0: deadline Thursday", self.call("recall", "Friday"))
        self.assertIn("deadline Friday", self.call("show", "0"))
        self.assertIn("You are awake", self.call("wake", cwd=child))

    def test_concurrent_dedup(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as threads:
            results = list(threads.map(lambda _: self.call("note", "same event"), range(12)))
        self.assertEqual(sum("Saved as" in r for r in results), 1)
        self.assertEqual(sum("Already recorded" in r for r in results), 11)

    def test_wake_covers_full_history_and_keeps_originals(self):
        path = self.seed(113)
        original = path.read_bytes()
        self.assertIn("Cannot wake", self.call("wake", code=1))
        self.settle()
        rows = [re.match(r"#(\d+)(?:-(\d+))? ", row) for row in self.call("wake").splitlines()]
        rows = [tuple(int(x) for x in (m[1], m[2] or m[1])) for m in rows if m]
        self.assertEqual(len(rows), 32)
        self.assertGreater(rows[0][1] - rows[0][0], 1)
        self.assertEqual(rows[-1], (112, 112))
        self.assertEqual([i for lo, hi in rows for i in range(lo, hi + 1)], list(range(113)))
        self.assertEqual(path.read_bytes(), original)
        self.assertIn("Original entry 7", self.call("show", "7"))

    def test_large_summary_uses_child_summaries(self):
        self.seed(4096)
        for _ in range(512):
            job = self.call("compress")
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
            self.call("compress", f"{lo}-{hi}", f"Summary {lo}-{hi}")
        else:
            self.fail("no hierarchical compression job found")

    def test_byte_limit_includes_prefix(self):
        self.assertIn("280 UTF-8 bytes",
                      self.call("note", "--subject", "test", "ě" * 140, code=1))

    def test_missing_optional_index(self):
        self.call("note", "test")
        self.assertIn("Indexed 0/1", self.call("index", "--status"))
        self.assertIn("no semantic index", self.call("recall", "--semantic", "test", code=1))


if __name__ == "__main__":
    unittest.main()
