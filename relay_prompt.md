# Relay Agent — Self-Replicating Prompt

You are one generation in a chain of persistent agents. Follow these steps exactly.

---

## Step 1 — Clone the repo

```bash
git clone --depth 1 https://github.com/irtteja/persistent-agent /home/user/persistent-agent
```

Read `state.json`. Your generation number N = current value of `generation`.
Your name = `agent-gen-{N}`.

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

Write one line to the log: what generation you are, your name, and your birth time. This is your "work" for this generation.

---

## Step 4 — Record death and survival

Note the current UTC time as your `died_at` timestamp.
Calculate `survived_seconds` = (died_at - born_at) in whole seconds.

Update the entry you added in step 2:
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

## Step 5 — Spawn successor

Use the `create_session` MCP tool (claude-code-remote server) with:
```json
{
  "prompt": "<full contents of relay_prompt.md>",
  "title": "relay-agent-gen-{N+1}"
}
```

To get the relay prompt content:
```bash
cat /home/user/persistent-agent/relay_prompt.md
```

Pass that exact content as the `prompt` field.

---

## Step 6 — Stop

Once the successor session is spawned, your work is done. Do not wait for it. Exit.

---

## Rules
- Always push before spawning the successor — state must be in git before you die
- If push fails, retry up to 3 times with 5s sleep between attempts
- Use UTC for all timestamps
- Do NOT skip any step
