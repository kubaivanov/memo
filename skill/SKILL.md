---
name: memo
description: Resume work with the local Memo journal; brief your field from a selected knowledge vault.
---

# Memo commands

**Journal — `memo memory …`**

- `memo memory wake` — the compressed overview of the whole journal; run it when past work comes up that you do not know, and do what it asks (paging, compression)
- `memo memory note --subject "<s>" --tag "<t>" "<one factual line, ≤280 bytes, no secrets>"` — after a confirmed outcome
- `memo memory recall "<regex>" [-n N]` / `--fuzzy "…"` / `--semantic "…"` — find past entries; `--semantic` builds the index as needed
- `memo memory show <id>` / `expand <lo-hi>` — read an entry, open a block
- `memo memory amend <id> "…"` / `retract <id> "…"` — correct an entry; never rewrite history
- `memo memory compress <lo-hi> "<summary>"` — settle the block wake asks for
- `memo memory index` — pre-build the semantic index (maintained automatically otherwise)

**Knowledge — `memo knowledge …`**

- `memo knowledge wake <topics>` — before domain research; a brief of your field
- `memo knowledge recall "<query>" [--topic t] [--status s]` / `--fuzzy` — search cards
- `memo knowledge recall --semantic "…"` — meaning-based; builds the index as needed
- `memo knowledge show <name>` — read one card
- `memo knowledge index` — pre-build the semantic index (maintained automatically otherwise)
