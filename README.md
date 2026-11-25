<div align="center">

<img src="assets/logo.svg" width="118" height="118" alt="Memo logo">

# Memo

**Local memory for AI agents — built for PPC and marketing teams.**

A standalone CLI journal with a progressive-compression overview.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776ab?logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-555)](#)
[![Deps](https://img.shields.io/badge/deps-stdlib%20only-2f9e44)](#design-guarantees)
[![Tests](https://img.shields.io/badge/tests-6%2F6-brightgreen)](#development)

</div>

---

Your ads agents manage live campaigns across sessions: budget moves, bid-strategy reverts, creative approvals, sync tags, open QA items. Every new session starts from scratch — the transcript is too long to reread, and the last few messages lose everything older. Memo gives each agent a small journal in its own folder and one command — `memo wake` — that shows the whole history in a few lines: **old material compressed, recent material verbatim, nothing deleted.**

No daemon, no IDE plugin, no external service. One file of Python from the standard library.

## The one command that matters

`memo wake` on an ads agent's journal with 113 entries prints 32 lines and covers *all* of them:

```text
Today is 2026-11-25.
#0-15   Kickoff: deploy-only-after-review rule set; e-mail and 404 fixes live.
#16-23  Consent sync v2: cookieless GTM tag pair reviewed; checks green.
#24-31  GTM v3 live: init and consent in one tag; autocapture on; tests 7/7.
#32-39  GTM v4 in production; single PostHog tag on gtm.init.
#40-47  Quiet week: backups, reports and routine checks; nothing blocking.
#48-55  Partner logo prep; tools-page copy drafts; weekly checks.
#56-63  Mobile audit branch opened; contrast and skip-link fixes staged.
#64-67  Promo copy removed from all ad bodies per owner decision.
#68-71  Budget $100 → $200 after tCPA throttled delivery.
#72-75  Day-2 read: 25% of budget used; pacing is the constraint.
#76-79  View transitions and self-hosted fonts live; CDP verified.
#80-83  Lighthouse perf drop traced to GTM/PostHog, not the build.
#84-87  Six route ads rewritten to name the corridor in the title.
#88-89  Carousel wired; dead script fixed.
#90-91  Partner logo deployed to the partners strip.
#92-93  Purchase-pixel QA checklist drafted.
#94-95  Campaign window confirmed through Dec 3.
#96-97  Cookie dialog closedby=any verified in Chrome 390.
#98-99  23 tests OK on fix/mobile-a11y-clarity.
#100  2026-11-24 [jakubivanov] change: mobile audit fixes on fix/mobile-a11y-clarity; 23 tests OK.
#101  2026-11-24 [ads] decision: promo code removed from all ad bodies; titles unchanged.
#102  2026-11-24 [website] testing: Chrome 390 verified; dialog and skip link pass contrast.
#103  2026-11-25 [website] blocker: purchase-pixel QA still open before launch.
#104  2026-11-25 [ads] change: daily budget $100 -> $200 after tCPA throttled delivery.
#105  2026-11-25 [ads] reporting: day 2 used 25% of budget; pacing is the constraint.
#106  2026-11-25 [website] change: view transitions and self-hosted fonts live; CDP verified.
#107  2026-11-25 [ads] testing: 7/7 tag tests pass; autocapture on.
#108  2026-11-25 [jakubivanov] change: partner logo added to the partners strip; deployed.
#109  2026-11-25 [website] testing: Lighthouse perf drop traced to GTM/PostHog, not the build.
#110  2026-11-25 [ads] change: rewritten 6 route ads to name the corridor in the title.
#111  2026-11-25 [website] blocker: purchase-pixel QA still open before the launch.
#112  2026-11-25 [ads] decision: campaign stays live through the Dec 3 window.
You are awake.
```

Older stretches appear as one-line summaries of 2, 4, 8, 16… entries; the newest entries appear verbatim. Every entry is covered exactly once — no gaps, no overlaps — and nothing is ever deleted.

## For PPC teams running agents

One journal per agent, one folder per channel — Google Ads, Meta, ChatGPT Ads, Reddit Ads each keep their own, so spend, decisions and blockers never mix:

```text
team/
├── google-ads/   └── .memo/   budget & bidding decisions, QA evidence
├── meta-ads/     └── .memo/   creative approvals, catalog work
├── reddit-ads/   └── .memo/   campaign windows, caps, day-boundary reads
└── content/      └── .memo/   page fixes, deploy approvals
```

The loop that makes it work:

1. **`memo wake`** at session start — the agent sees what changed, what's binding (deploy-after-approval rules, owner decisions) and what's still open (pixel QA).
2. **`memo note`** after each confirmed change — budget moves, bid reverts, promo-code removals, with the numbers. One line, no session bloat.
3. **`memo recall`** when the question is "what did we decide about promo codes?" — regex, typo-tolerant and optional semantic search over the originals, with later corrections shown under the hits.

Because agents write plain, dated lines as they work, week-old context costs one summary line — and your team can audit exactly what the agent believed when it acted. It runs on the same box as your agents, next to your campaign data, with no service to operate.

## How it works

1. **`memo note`** appends one short line (≤ 280 bytes): a change, a decision, a blocker, a lesson. Duplicates are detected under the same lock as the write, so parallel sessions can't double-record.
2. **`memo compress`** stores one-line summaries for aligned blocks. Blocks up to 16 entries are summarized from the originals; larger blocks are built from two smaller summaries. Your agent writes the summary — Memo never calls a model behind your back.
3. **`memo wake`** selects whole blocks to fit ~32 lines and prints them. If a required summary is missing, it prints the next compression job with its inputs and asks for it, then you re-run `wake`.

```text
agent/
└── .memo/
    ├── entries.jsonl   the journal — append-only, never rewritten
    ├── summaries/      one JSON file per compressed block (2, 4, 8, …)
    └── index.json      optional semantic-search vectors
```

Corrections are appends too: `memo amend <id>` and `memo retract <id>` add entries that reference what they correct. The history is never edited. `memo recall` shows later corrections under the hits it returns.

## Quick start

Requires Python 3.9+ on macOS or Linux. Core commands use only the standard library.

```sh
git clone https://github.com/kubaivanov/memo.git && cd memo
export PATH="$PWD/bin:$PATH"

# Try it in a dedicated, empty agent folder:
mkdir -p ~/demo-agent && cd ~/demo-agent
memo init
memo note --subject "website" --tag "decision" "Deploy only after review."
memo wake
memo recall "review" -n 5
```

Runs from a subfolder resolve to the same journal. A minimal drop-in instruction for your agent lives in [`skill/SKILL.md`](skill/SKILL.md).

## Commands

| Command | Purpose |
| --- | --- |
| `memo init` | Create the journal (`.memo/`) for this folder. |
| `memo wake [part [snapshot]]` | The progressive-compression overview. |
| `memo note [--subject s] [--tag t] [--date d] "line"` | Append one memory; duplicate-checked. |
| `memo compress [<range> "<summary>"]` | Show the next compression job, or store a summary. |
| `memo recall "regex" [-n 20] [--since 7d] [--subject s]` | Search the originals; shows later corrections. |
| `memo recall --fuzzy "typo toleranr query"` | Typo-tolerant search. |
| `memo show <id \| lo-hi>` | One entry (or block) plus everything that later referenced it. |
| `memo amend <id> "correction"` | Append a correction. History is never rewritten. |
| `memo retract <id> "reason"` | Append a retraction. |
| `memo expand <lo-hi>` | Open a summary into its two halves. |
| `memo drop-summary <lo-hi>` | Discard a derived summary (originals stay untouched). |
| `memo index [--status \| --rebuild]` | Maintain the optional semantic index. |
| `memo status` / `memo tags [--add "name: what it means"]` | Journal stats / tag vocabulary. |

Default tags: `change`, `decision`, `blocker`, `testing`. Size limits (`280` bytes per line, `32` wake rows) are constants at the top of [`bin/memo`](bin/memo).

## Optional semantic search

```sh
python3 -m pip install sentence-transformers
memo index
memo recall --semantic "what did we decide about the launch?"
```

Encodes entries locally with `paraphrase-multilingual-MiniLM-L12-v2` (weights may download on first use). `recall` never builds the index as a side effect: if entries are newer than the index, it says so and you run `memo index`. Regex and fuzzy search work without the model — the core tool stays dependency-free.

## Design guarantees

- **Append-only.** Entries and corrections are appended, never edited. Summaries are derived data; dropping one never touches an entry.
- **Folder-scoped.** Each agent folder has one journal; subfolders resolve to the same one. No global state, no server, no background process.
- **Stdout contract.** Like `wake`'s pager footer, outputs are written for agent consumption: explicit next actions, machine-usable `#id` references, no noise.
- **Standard library only** for the core. One `fcntl` lock guards concurrent access to a journal; that pins the supported platforms to macOS and Linux.

## Development

```sh
python3 -m unittest discover -s tests -v
```

Six tests exercise the CLI end-to-end in temporary folders: nested scope resolution, concurrent dedup, full-history wake coverage with original entries intact, hierarchical (two-level) summaries for large blocks, byte limits including prefixes, and the optional-index contract. No network, no model weights, no real journals.

## Journals from other tools

Memo has its own on-disk format and does not convert journals written by other engines; `init` refuses the known legacy formats. Real journals belong in the agent's folder, **not** in Git (see `.gitignore`).

## Attribution

The journal-and-compression model is inspired by [OptMem by Victor Taelin](https://github.com/VictorTaelin/OptMem). Memo does not bundle, invoke, or require it.

## License

[MIT](LICENSE) — free to use, modify and redistribute.
