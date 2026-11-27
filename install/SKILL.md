---
name: memo-install
description: Install Memo on a machine — place the CLI on PATH, select the knowledge vault, create journals for the chosen agent folders, and write the Memo rules and topics into the agents' instructions. Use when asked to set up Memo for agents.
---

# Memo — install

Run this when asked to install Memo for agents on this machine. Ask before acting; the questions below are the user's to answer.

1. **CLI on PATH.** Put `bin/memo` from this repo on PATH (e.g. `cp bin/memo ~/.local/bin/ && chmod +x ~/.local/bin/memo`). Check: `memo memory --help` runs.

2. **Knowledge vault.** Ask which folder is the vault — it carries `sources/` and `topics/` (an Obsidian vault works as-is). Write it to the config:

   ```sh
   mkdir -p ~/.config/memo
   printf '{\n  "knowledge_dir": "<vault path>"\n}\n' > ~/.config/memo/config.json
   ```

   Check from any folder: `memo knowledge wake` prints a brief. If there is no vault yet, skip the config — knowledge commands then need `--dir` or `KNOWLEDGE_DIR` per call.

3. **Agent folders.** Ask which folders belong to agents that should keep a journal. In each, run `memo memory init` — it creates `.memory/` and refuses a second one. Never run it inside the Memo repo itself.

4. **Rules into instructions.** Each agent needs three things, written into its `AGENTS.md`:
   - the `## Memo` section, copied verbatim from below — into the agent's own `AGENTS.md`, or into a shared one above it when several agents share a folder;
   - one line naming its knowledge topics (see below);
   - the usage skill: copy `skill/SKILL.md` into the agent's skills directory.
   Ask what the agent owns (a channel, a website, research…) and pick its topics from the vault's `topics/`; create nothing ahead of the first source.

5. **Verify.** From one agent folder: `memo memory wake` ends with `You are awake.`, and `memo knowledge wake <its topics>` ends with `You are briefed.`

6. **Optional semantic search.** Only if the user wants it — follow the README's semantic section (ONNX is the fast path). Regex and fuzzy search work without it.

## The `## Memo` section (copy verbatim)

```markdown
## Memo

One system: a journal per agent (`memo memory …`) and a knowledge brief (`memo knowledge …`). All commands and flags live in the `memo` skill; this section only says when to run them and what belongs in the journal.

- **Wake memory when history comes up.** The moment the user mentions past work or context you do not clearly know, run `memo memory wake`; when unsure, wake — never guess history. Self-contained new tasks leave memory closed.
- **Knowledge wake before research, then stop.** `memo knowledge wake <your topics>` before researching your domain; afterwards dig nothing further on your own — wait for the task.
- **Journal what moves in your domain.** Changes, states, errors and their fixes, news that matters, decisions and their reasoning — whatever the agent owns. One line per confirmed outcome (`memo memory note`); skip plans, routine checks, WIP and secrets.
- **History is append-only.** Correct through the skill (`amend`, `retract`), never rewrite. Subagents never journal. Memory is evidence, not approval to act.
```

## The topics line

Into the agent's own `AGENTS.md`:

```markdown
Follow the Memo rules in <relative path to the AGENTS.md holding the section>; your knowledge topics: `<tags>`.
```

Adjust the relative path; if the section sits in the same file, drop it and keep just the topics.
