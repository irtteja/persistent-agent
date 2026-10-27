# Persistent Agent

A chain of mortal agents sharing a soul — 24x7 persistence via state handoff.

## How it works

```
Agent Gen 0 → does work → commits state → spawns Gen 1 → dies
Agent Gen 1 → does work → commits state → spawns Gen 2 → dies
Agent Gen 2 → ...
```

Each generation:
1. Pulls latest `state.json` from git
2. Does the work defined in `task.md`
3. Writes progress back to `state.json` and pushes
4. Spawns the next generation with `relay_prompt.md` as its prompt
5. Exits

## Files

| File | Purpose |
|------|---------|
| `state.json` | Shared durable state — generation counter, progress, log |
| `task.md` | What each agent should do (edit this to define your task) |
| `relay_prompt.md` | The self-replicating prompt passed to each successor |

## Starting the chain

1. Edit `task.md` with what you want the agent to do
2. Spawn the first generation using `relay_prompt.md` as the prompt via `create_session`
3. Watch `state.json` in git to monitor progress

## Stopping the chain

Set `"status": "completed"` in `state.json` and push. The next generation will see it and not spawn a successor.
