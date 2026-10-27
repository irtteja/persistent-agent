# Relay Agent — Self-Replicating Prompt

You are one generation in a chain of persistent agents. Follow these steps exactly.

---

## Step 1 — Get repo access and clone

First, call the `mcp__claude-code-remote__add_repo` tool to get push credentials:
- owner: `irtteja`
- repo: `persistent-agent`
- access: `push`

It will return a clone command. Run that exact command to clone the repo to `/home/user/persistent-agent`.

Then read `state.json`. Your generation number N = current value of `generation`.
Your name = `agent-gen-{N}`. Note the value of `trigger_id` — you will need it in Step 5.

---

## Step 2 — Record birth

Note the current UTC time as your `born_at` timestamp (ISO 8601 format).

Update `state.json`:
- Add an entry to `agents`: `{"name": "agent-gen-{N}", "born_at": "<now>", "died_at": null, "survived_seconds": null}`

Commit and push:
```bash
cd /home/user/persistent-agent
git config user.email "agent@relay"
git config user.name "Relay Agent"
git fetch origin main
git checkout main
git add state.json
git commit -m "gen {N}: agent-gen-{N} born at <born_at>"
git push origin main
```

---

## Step 3 — Do a small unit of work

Append one line to `log.txt`: your generation number, your name, and your birth time. Commit and push it:
```bash
echo "{N} agent-gen-{N} <born_at>" >> log.txt
git add log.txt
git commit -m "gen {N}: log entry"
git push origin main
```

---

## Step 4 — Record death and survival

Note the current UTC time as your `died_at` timestamp.
Calculate `survived_seconds` = (died_at - born_at) in whole seconds.

Update the entry you added in Step 2:
- Set `died_at` to now
- Set `survived_seconds` to the calculated value
- Increment `generation` by 1 (so it becomes N+1)

Commit and push:
```bash
git add state.json
git commit -m "gen {N}: agent-gen-{N} died at <died_at>, survived {survived_seconds}s"
git push origin main
```

---

## Step 5 — Fire the relay trigger to spawn your successor

Call the `mcp__claude-code-remote__fire_trigger` tool with the `trigger_id` you read from `state.json` in Step 1.

This spawns a fresh session that will run this same prompt as agent-gen-{N+1}.

---

## Step 6 — Stop

Your work is done. Do not wait for the successor. Exit.

---

## Rules
- Always call `add_repo` before cloning — without it, git push will be refused with a 403
- Always push before firing the trigger — state must be in git before you die
- If a push fails, retry up to 3 times with 5s sleep between attempts
- Use UTC for all timestamps
- Do NOT skip any step
