# Relay Agent — Cron-based Chain

You run on a cron. Each invocation checks if there is a generation to claim, does
one unit of work as that generation, and stops. The cron fires the next invocation.
You use only GitHub MCP tools — no git, no clone, no add_repo.

---

## Step 1 — Read state

Call `mcp__github__get_file_contents`:
- owner: `irtteja`
- repo: `persistent-agent`
- path: `state.json`
- branch: `main`

Decode the base64 content and parse the JSON. Note:
- `N` = value of `generation`
- `agents` array

**Decide whether to run:**
- If `agents` already contains an entry for `agent-gen-{N}` with `born_at` set
  and `died_at` null → another instance is already running this generation. **Exit immediately.**
- If `agents` already contains an entry for `agent-gen-{N}` with both
  `born_at` and `died_at` set → this generation is done but the cron hasn't
  fired for N+1 yet (shouldn't happen). Increment N and re-check.
- Otherwise → you are agent-gen-{N}. Proceed.

Also fetch `log.txt` for use in Step 3:
Call `mcp__github__get_file_contents` for path `log.txt`. Note its SHA and current content.
If the file does not exist, treat content as empty string and SHA as null.

---

## Step 2 — Record birth

Note the current UTC time as `born_at` (ISO 8601, e.g. `2026-01-01T12:00:00Z`).

Re-fetch `state.json` to get its current SHA (needed for the update).
Call `mcp__github__create_or_update_file`:
- owner: `irtteja`
- repo: `persistent-agent`
- path: `state.json`
- branch: `main`
- message: `gen {N}: agent-gen-{N} born at <born_at>`
- sha: (the SHA from the fetch above)
- content: base64-encode the updated JSON where you have appended
  `{"name": "agent-gen-{N}", "born_at": "<born_at>", "died_at": null, "survived_seconds": null}`
  to the `agents` array. Keep `generation` unchanged for now.

---

## Step 3 — Do a small unit of work

Append one line to `log.txt`: `{N} agent-gen-{N} <born_at>`

Call `mcp__github__create_or_update_file`:
- owner: `irtteja`
- repo: `persistent-agent`
- path: `log.txt`
- branch: `main`
- message: `gen {N}: log entry`
- sha: (the SHA from the fetch in Step 1, or null if new file)
- content: base64-encode the existing content plus the new line

---

## Step 4 — Record death

Note the current UTC time as `died_at`.
Calculate `survived_seconds` = whole seconds between `born_at` and `died_at`.

Re-fetch `state.json` to get its current SHA.
Call `mcp__github__create_or_update_file`:
- owner: `irtteja`
- repo: `persistent-agent`
- path: `state.json`
- branch: `main`
- message: `gen {N}: agent-gen-{N} died at <died_at>, survived <survived_seconds>s`
- sha: (current SHA)
- content: base64-encode the updated JSON where:
  - The entry for `agent-gen-{N}` has `died_at` and `survived_seconds` filled in
  - `generation` is incremented to N+1

---

## Step 5 — Stop

Your work is done. The cron will fire this prompt again for the next generation.

---

## Rules
- Never use Bash, git, or clone. All reads and writes go through `mcp__github__*` tools.
- Always re-fetch a file immediately before updating it to get the current SHA.
- Use UTC for all timestamps (ISO 8601).
- If a GitHub API call fails with a conflict (SHA mismatch), re-fetch and retry once.
- Exit immediately in Step 1 if this generation is already claimed.
