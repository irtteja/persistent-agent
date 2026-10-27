# Task

Each agent generation must:

1. **On birth** — record its name and birth timestamp into state.json
2. **Survive** — do a small unit of work (can be a no-op, a log entry, anything)
3. **On death** — record death timestamp and calculate survival in seconds
4. **Hand off** — spawn the next generation, then stop

## Agent naming
Name format: `agent-gen-{N}` where N is the current generation number from state.json.

## state.json schema
Each generation appends one entry to the `agents` array:
```json
{
  "name": "agent-gen-0",
  "born_at": "2026-10-27T10:00:00Z",
  "died_at": "2026-10-27T10:00:45Z",
  "survived_seconds": 45
}
```
Also increment `generation` by 1 before pushing.
