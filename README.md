<img src="assets/logo.svg" alt="Memo: three stacked notes" width="112" height="112">

# Memo

**Local memory for agents that need to pick up where they left off.**

Memo is a standalone command-line tool. It keeps a journal in each agent's folder and runs without an IDE plugin, a daemon, or an external journal engine.

## How it works

- `memo note` appends a short, numbered entry. It checks for exact duplicates under the same lock used for writes.
- `memo compress` stores one-line summaries for blocks of older entries. For blocks up to 16 entries, the agent sees the originals. Larger blocks use two smaller summaries as input.
- `memo wake` is a single view: older material appears in coarser summaries, recent entries in more detail. It selects whole blocks, not sentences. Original entries remain available to `memo recall` and `memo show`.

```text
agent/
└── .memo/
    ├── entries.jsonl original entries
    ├── summaries/    compressed views of older entries
    └── index.json    optional search index
```

One `wake` covers the whole journal in up to 32 memory lines without deleting anything. If a required card is missing, Memo prints the next compression job and its inputs. `compress` writes the summary supplied by your agent; Memo does not call a model to write summaries.

## Try it locally

Requires Python 3.9+ on macOS or Linux. Core commands use only the standard library.

```sh
# From this checkout:
export PATH="$PWD/bin:$PATH"

# Use a dedicated, empty agent folder:
mkdir -p "$HOME/memo-example"
cd "$HOME/memo-example"
memo init
memo note --subject "website" --tag "decision" "Deploy only after review."
memo wake
memo recall "review" -n 5
```

`memo init` creates `.memo/`. Subsequent calls from a subfolder use the same journal. `memo amend` and `memo retract` append corrections; they do not erase entries or rewrite old summaries. `recall` shows linked corrections below hits. `memo expand 0-15` shows finer detail, and `memo drop-summary 0-15` discards the selected derived summary and its ancestors without changing the original journal.

### Optional semantic search

Install `sentence-transformers` in your Python environment, run `memo index`, then `memo recall --semantic "what did we decide about release?"`. The model weights may download on first use; text is encoded locally. Refresh the index after new entries when needed. Regex and fuzzy search work without the model.

### Existing journals

This standalone version has its own disk format. It does not read or automatically convert journals written by another engine, and `init` refuses the known legacy log formats. Run it on a fresh folder until a migration is available. Keep real journals and search indexes out of Git.

See [`skill/SKILL.md`](skill/SKILL.md) for portable agent instructions.

## Development

```sh
python3 -m unittest discover -s tests -v
```

Tests run the standalone CLI in temporary folders. They do not need network access, model weights, or your real journal.

## Attribution and release status

Inspired by [OptMem by Victor Taelin](https://github.com/VictorTaelin/OptMem). Memo does not bundle, invoke, or require OptMem. The project license is pending the owner's decision before public release.
