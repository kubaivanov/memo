<div align="center">

<img src="assets/logo.svg" width="118" height="118" alt="Memo logo">

# Memo

**Local memory for AI agents — built for PPC and marketing teams.**

A journal that compresses itself, and a brief over what your field knows.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776ab?logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-555)](#)
[![Deps](https://img.shields.io/badge/deps-stdlib%20only-2f9e44)](#design-guarantees)
[![Tests](https://img.shields.io/badge/tests-11%2F11-brightgreen)](#development)

</div>

---

Your ads agents manage live campaigns across sessions: budget moves, bid-strategy reverts, creative approvals, sync tags, open QA items. Every new session starts from scratch — the transcript is too long to reread, and the last few messages lose everything older.

Memo gives each agent two stores, next to its work:

- **`memo memory …`** — a journal that compresses itself. `memo memory wake` shows the whole history in a few lines: old material compressed, recent material verbatim, nothing deleted.
- **`memo knowledge …`** — a brief over a vault of note cards. `memo knowledge wake ppc chatgpt-ads` answers "what does my field know?", from your own curated sources.

No daemon, no IDE plugin, no external service. One file of Python from the standard library.

## Memory: a journal that compresses itself

`memo memory wake` on an ads agent's journal with 113 entries prints 32 lines and covers *all* of them:

```text
Today is 2026-11-25.
#0-15   Kickoff: deploy-only-after-review rule set; e-mail and 404 fixes live.
#16-23  Consent sync v2: cookieless GTM tag pair reviewed; checks green.
#24-31  GTM v3 live: init and consent in one tag; autocapture on; tests 7/7.
#32-39  GTM v4 in production; single PostHog tag on gtm.init.
#40-47  Quiet week: backups, reports and routine checks; nothing blocking.
#48-55  Partner logo prep; tools copy drafts; weekly checks.
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

How the three commands fit together:

1. **`memo memory note`** appends one short line (≤ 280 bytes): a change, a decision, a blocker, a lesson. Duplicates are detected under the same lock as the write, so parallel sessions can't double-record.
2. **`memo memory compress`** stores one-line summaries for aligned blocks. Blocks up to 16 entries are summarized from the originals; larger blocks are built from two smaller summaries. Your agent writes the summary — Memo never calls a model behind your back.
3. **`memo memory wake`** selects whole blocks to fit ~32 lines and prints them. If a required summary is missing, it prints the next compression job with its inputs and asks for it, then you re-run `wake`.

Corrections are appends too: `memo memory amend <id>` and `memo memory retract <id>` add entries that reference what they correct. The history is never edited, and `memo memory recall` shows later corrections under the hits it returns.

## Knowledge: a brief of the field

A knowledge vault is any folder of note cards with `sources/` and `topics/` — an Obsidian vault works as-is. Cards carry YAML frontmatter (`title`, `status: new|read|used`, `captured`, `topics`); topics are quoted wikilinks (`"[[ppc]]"`) pointing at router notes.

```text
$ memo knowledge wake chatgpt-ads ppc
Knowledge: ~/0-KNOWLEDGE
22 sources, 0 ideas, 1 in inbox. Field: chatgpt-ads, ppc — 5 source(s) match.
Fresh (new): 0
Ready to use (read): 5
- openai--chatgpt-ads-increases-its-market-presence...--2026-11-12 (2026-11-18) [chatgpt-ads, ppc, cz, adtech]
- adexchanger--google-s-ai-ad-losses-are-meta-s-gain...--2026-11-11 (2026-11-11) [ppc, ai-search, chatgpt-ads, adtech, meta-ads]
Routers: topics/chatgpt-ads.md, topics/ppc.md
You are briefed.
```

With no topics, the brief covers the whole vault. **The vault is chosen, never guessed**, in this order: the `--dir` argument, the `KNOWLEDGE_DIR` environment variable, or `knowledge_dir` in `~/.config/memo/config.json` (`MEMO_CONFIG` to relocate the config). Without a selection Memo tells you how to make one.

Search the cards by exact words, filters, or meaning:

```sh
memo knowledge recall "CTR pozice 1" --topic ai-search --status read
memo knowledge recall --fuzzy "meta analisis"     # typo-tolerant
memo knowledge index                              # optional, once
memo knowledge recall --semantic "what fell after AI Overviews?"
```

For semantic search the index is built **per chunk**: each title-prefixed paragraph of a card gets its own vector, so a hit points at the paragraph that matched — and bodies longer than the model window still work:

```text
growth-memo--meta-analysis--2026-11-16 (read, 2026-11-18) [ai-search, seo, …] -- 0.54
  CTR on position 1 with AI Overviews fell 58% relatively…
```

## Where the data lives

```text
agent-folder/
└── .memory/        the journal: entries.jsonl (append-only),
                    summaries/ (derived, rebuildable), index.json (optional)
vault/
└── .knowledge/     the chunked semantic index — the only thing Memo
                    ever writes into your vault; everything else is yours
```

Both stores are folder-scoped: runs from a subfolder resolve to the same journal. The knowledge vault is whatever you selected — one machine, one vault, or a different `--dir` per call.

## For PPC teams running agents

One journal per agent, one folder per channel — and one shared vault of what the field knows:

```text
team/
├── google-ads/  └── .memory/   journal: budget & bidding decisions, QA evidence
├── meta-ads/    └── .memory/   journal: creative approvals, catalog work
├── reddit-ads/  └── .memory/   journal: campaign windows, caps, day-boundary reads
└── 0-KNOWLEDGE/               vault: source cards, topic routers per channel
```

The loop that makes it work:

1. **`memo memory wake`** at session start — the agent sees what changed, what's binding and what's still open.
2. **`memo memory note`** after each confirmed change; **`memo knowledge wake <topics>`** before research, so the agent starts from what the team already collected instead of re-reading the internet.
3. **`memo knowledge recall`** when the question is "what do we know about promo codes?" — over your own curated cards, with filters and their exact citations.

Because agents write plain, dated lines as they work, week-old context costs one summary line — and your team can audit exactly what the agent believed when it acted.

## Quick start

Requires Python 3.9+ on macOS or Linux. Core commands use only the standard library.

```sh
git clone https://github.com/kubaivanov/memo.git && cd memo
export PATH="$PWD/bin:$PATH"

# Memory: try it in a dedicated, empty agent folder.
mkdir -p ~/demo-agent && cd ~/demo-agent
memo memory init
memo memory note --subject "website" --tag "decision" "Deploy only after review."
memo memory wake
memo memory recall "review" -n 5

# Knowledge: point it at any folder of cards with sources/ and topics/.
mkdir -p demo-vault/sources demo-vault/topics
printf -- '---\ntitle: "Demo"\nstatus: new\ntopics: ["[[ppc]]"]\n---\n\n# Demo\n\nReseller expanded to 44 countries.\n' > demo-vault/sources/demo.md
printf -- '# PPC\n' > demo-vault/topics/ppc.md
memo knowledge wake ppc --dir demo-vault
```

A minimal drop-in instruction for your agent lives in [`skill/SKILL.md`](skill/SKILL.md).

## Commands

### `memo memory` — the journal

| Command | Purpose |
| --- | --- |
| `memo memory init` | Create the journal (`.memory/`) for this folder. |
| `memo memory wake [part [snapshot]]` | The progressive-compression overview. |
| `memo memory note [--subject s] [--tag t] [--date d] "line"` | Append one memory; duplicate-checked. |
| `memo memory compress [<range> "<summary>"]` | Show the next compression job, or store a summary. |
| `memo memory recall "regex" [-n 20] [--since 7d] [--subject s]` | Search the journal; shows later corrections. |
| `memo memory recall --fuzzy "…" / --semantic "…"` | Typo-tolerant / meaning-based search; `--semantic` builds the index as needed. |
| `memo memory show <id \| lo-hi>` | One entry (or block) plus later references. |
| `memo memory amend <id> "correction"` / `retract <id> "reason"` | Append corrections; history is never rewritten. |
| `memo memory expand <lo-hi>` / `drop-summary <lo-hi>` | Open a summary into its halves / discard a derived summary. |
| `memo memory index [-status \| --rebuild]` / `status` / `tags` | Optional index, journal stats, tag vocabulary. |

### `memo knowledge` — the vault

| Command | Purpose |
| --- | --- |
| `memo knowledge wake [topics…] [--dir v]` | One field brief, assembled from vault frontmatter. |
| `memo knowledge recall "regex" [--topic t] [--status s] [-n]` | Search cards by words and filters. |
| `memo knowledge recall --fuzzy "…" / --semantic "…"` | Typo-tolerant / meaning-based card search; `--semantic` builds the index as needed. |
| `memo knowledge show <name> [--dir v]` | Print one card: metadata plus body, without the YAML. |
| `memo knowledge index [-status \| --rebuild] [--dir v]` | Build the chunked semantic index (`.knowledge/`). |

Default journal tags: `change`, `decision`, `blocker`, `testing`. Size limits (`280` bytes per line, `32` wake rows) are constants at the top of [`bin/memo`](bin/memo).

## Optional semantic search

```sh
python3 -m pip install sentence-transformers
```

After that, **the index takes care of itself**: `memo memory note` returns immediately — a short-lived background run embeds the new entry, so writes never wait for a model. Any `recall --semantic` completes the index synchronously before searching; only the first search after the install pays the full build. The explicit `index` commands remain for pre-building and `--status` / `--rebuild`.

Without the library, journals simply skip indexing and nothing fails; regex and fuzzy search need no model. Encodes text locally with `paraphrase-multilingual-MiniLM-L12-v2` (weights may download on first use). The knowledge index is built **per chunk**: each title-prefixed paragraph of a card gets its own vector, so a hit points at the paragraph that matched — and bodies longer than the model window still work.

## Design guarantees

- **Append-only journals.** Entries and corrections are appended, never edited. Summaries are derived data; dropping one never touches an entry.
- **Read-only towards the vault.** Knowledge commands never modify a card; the only write is the rebuildable `.knowledge/index.json`.
- **Folder-scoped.** Each agent folder has one journal; subfolders resolve to the same one. No global state, no server, no resident process — a note's indexing is a short-lived detached child that exits when done.
- **Stdout contract.** Outputs are written for agent consumption: explicit next actions, stable `#id` / card-name references, no noise.
- **Standard library only** for the core. One `fcntl` lock guards concurrent access to a journal; that pins the supported platforms to macOS and Linux.

## Development

```sh
python3 -m unittest discover -s tests -v
```

Eleven tests exercise the CLI end-to-end in temporary folders: journal scope resolution, concurrent dedup, full-history wake coverage with originals intact, hierarchical summaries, byte limits, the optional-index contract — and knowledge discovery, field-filtered briefs, filtered and fuzzy card search, card printing and the semantic-index contract. No network, no model weights, no real journals.

## Journals from other tools

Memo has its own on-disk format and does not convert journals written by other engines; `init` refuses the known legacy formats. Real journals and vaults belong in the agent's folder, **not** in Git (see `.gitignore`).

## Attribution

The journal-and-compression model is inspired by [OptMem by Victor Taelin](https://github.com/VictorTaelin/OptMem). Memo does not bundle, invoke, or require it.

## License

[MIT](LICENSE) — free to use, modify and redistribute.
