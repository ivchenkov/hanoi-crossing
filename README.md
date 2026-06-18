# Hanoi Crossing

Hanoi Crossing is a small reusable Python engine for the two-player Tower of
Hanoi variant described in the assignment. The repository also includes two
frontends:

- `replay`: runs a pre-recorded move sequence.
- `random`: lets both players choose random valid moves from the engine API.

The core engine is intentionally independent from the CLI. It can be reused as
the state core for a training loop, simulation service, or another frontend.

## Setup

This project uses a standard `src/` package layout. `uv sync` creates the
virtual environment, installs development dependencies, and installs the local
`hanoi_crossing` package into that environment.

```bash
uv sync
```

After syncing, the package can be imported from Python:

```bash
uv run python -c "from hanoi_crossing import HanoiCrossingState; print(HanoiCrossingState(1))"
```

Run tests:

```bash
uv run pytest
```

## CLI

The primary CLI entry point is `python -m hanoi_crossing`.

Run the built-in replay example, without creating an input file:

```bash
uv run python -m hanoi_crossing replay --example n1
```

Run a replay from a JSON file:

```bash
uv run python -m hanoi_crossing replay path/to/replay.json
```

Run a replay from stdin:

```bash
uv run python -m hanoi_crossing replay < path/to/replay.json
```

Run random play:

```bash
uv run python -m hanoi_crossing random --n 3 --seed 42 --max-steps 200
```

Use random player selection instead of alternating player selection:

```bash
uv run python -m hanoi_crossing random --n 3 --seed 42 --max-steps 200 --turn-order random
```

The package also exposes an equivalent console script:

```bash
uv run hanoi-crossing replay --example n1
```

## Replay Input Format

Replay input is JSON:

```json
{
  "n": 1,
  "steps": [
    {"turn": "a", "move": "lift_1"},
    {"turn": "b", "move": "lift_1"},
    {"turn": "a", "move": "place_3"}
  ]
}
```

Turns are lowercase `"a"` and `"b"`.

Moves are:

- `"lift_1"`
- `"lift_mid"`
- `"lift_3"`
- `"place_1"`
- `"place_mid"`
- `"place_3"`
- `"skip"`

The numbers `1` and `3` are local to the acting player. For player A,
`lift_1` means pole `1a`; for player B, it means pole `1b`. The shared pole is
always `mid`.

## Output Format

Both CLI modes write JSON to stdout. The output includes:

- `mode`
- `winner`
- final `state`
- per-step `history`

Example shape:

```json
{
  "mode": "replay",
  "winner": "a",
  "state": {
    "n": 1,
    "winner": "a",
    "poles": {
      "1a": [],
      "2": [],
      "3a": [1],
      "1b": [],
      "3b": []
    },
    "hands": {
      "a": null,
      "b": 2
    }
  },
  "history": [
    {
      "index": 1,
      "turn": "a",
      "move": "lift_1",
      "legal": true,
      "winner": null,
      "state": {
        "...": "same shape as final state"
      }
    }
  ]
}
```

The `state` inside each history item has the same shape as the final state.
Illegal moves are recorded with `"legal": false`; they do not mutate the game
state.

## Engine API

The main reusable object is `HanoiCrossingState`. Its API is deliberately close
to the `Board` object style from the Python `chess` package: a single mutable
state object exposes legal move generation and move application.

```python
from hanoi_crossing import HanoiCrossingState

state = HanoiCrossingState(n=1)
legal_moves = state.get_legal_moves("a")
result = state.step("lift_1", "a")
snapshot = state.to_dict()
```

Public methods:

- `get_legal_moves(turn)`: returns legal moves for the acting player.
- `step(move, turn)`: applies one action and returns `StepResult`.
- `to_dict()`: returns a JSON-friendly snapshot.
- `render()`: returns a compact human-readable state string.

The random player uses only this public API, which is the same boundary an RL
agent or online simulation service would use.

## Design Decisions

- Stacks are stored bottom-to-top. For example, `[5, 3, 1]` means `5` is on the
  bottom and `1` is on top.
- Player A owns odd disks: `1, 3, 5, ...`.
- Player B owns even disks: `2, 4, 6, ...`.
- `n` means each player starts with `n` disks, so the largest disk is `2n`.
- The shared pole is named `2` in snapshots and `mid` in moves.
- A player may lift any top disk from the shared pole, including the other
  player's disk.
- Illegal actions waste the turn and leave the state unchanged.
- Unknown moves or unknown players raise `ValueError`; malformed replay JSON is
  treated as caller/input error.
- Once a player wins, the state is frozen. Later `step` calls return
  `legal=False` and keep the winner.
- A win requires an empty hand, an empty shared pole, an empty own pole 1, and
  all of that player's own disks on own pole 3.
- The engine does not own turn scheduling. Replay mode receives turns from the
  input. Random mode offers `alternating` and `random` turn-order policies as
  frontend choices.

## AI Disclosure

AI assistance was used to help structure the package, CLI, tests, and
documentation around an existing hand-prepared engine implementation. The game
rules, engine behavior, and final review remain the submitter's responsibility.
