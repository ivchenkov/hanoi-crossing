import argparse
import json
import random
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .engine import HanoiCrossingState, Move, Turn


EXAMPLES: dict[str, dict[str, Any]] = {
    "n1": {
        "n": 1,
        "steps": [
            {"turn": "a", "move": "lift_1"},
            {"turn": "b", "move": "lift_1"},
            {"turn": "a", "move": "place_3"},
        ],
    }
}


def run_replay(spec: dict[str, Any]) -> dict[str, Any]:
    state = HanoiCrossingState(int(spec["n"]))
    history = []

    for index, raw_step in enumerate(spec.get("steps", []), start=1):
        turn = raw_step["turn"]
        move = raw_step["move"]
        result = state.step(move, turn)
        history.append(
            {
                "index": index,
                "turn": turn,
                "move": move,
                "legal": result.legal,
                "winner": result.winner,
                "state": state.to_dict(),
            }
        )

    return {
        "mode": "replay",
        "winner": state.winner,
        "state": state.to_dict(),
        "history": history,
    }


def run_random(
    *,
    n: int,
    max_steps: int,
    seed: int | None = None,
    turn_order: str = "alternating",
) -> dict[str, Any]:
    rng = random.Random(seed)
    state = HanoiCrossingState(n)
    history = []

    for index in range(1, max_steps + 1):
        if turn_order == "random":
            turn: Turn = rng.choice(["a", "b"])
        else:
            turn = "a" if index % 2 == 1 else "b"

        legal_moves = state.get_legal_moves(turn)
        if not legal_moves:
            break

        move: Move = rng.choice(legal_moves)
        result = state.step(move, turn)
        history.append(
            {
                "index": index,
                "turn": turn,
                "move": move,
                "legal": result.legal,
                "winner": result.winner,
                "state": state.to_dict(),
            }
        )

        if result.winner is not None:
            break

    return {
        "mode": "random",
        "n": n,
        "seed": seed,
        "turn_order": turn_order,
        "max_steps": max_steps,
        "winner": state.winner,
        "state": state.to_dict(),
        "history": history,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m hanoi_crossing")
    subparsers = parser.add_subparsers(dest="command", required=True)

    replay = subparsers.add_parser("replay", help="run a pre-recorded game")
    replay.add_argument(
        "path",
        nargs="?",
        help="JSON replay file path; reads stdin when omitted",
    )
    replay.add_argument(
        "--example",
        choices=sorted(EXAMPLES),
        help="run a built-in replay example instead of reading a file",
    )

    random_play = subparsers.add_parser("random", help="run random valid moves")
    random_play.add_argument("--n", type=int, required=True)
    random_play.add_argument("--max-steps", type=int, default=100)
    random_play.add_argument("--seed", type=int)
    random_play.add_argument(
        "--turn-order",
        choices=["alternating", "random"],
        default="alternating",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "replay":
        spec = _load_replay(args.path, args.example)
        output = run_replay(spec)
    else:
        output = run_random(
            n=args.n,
            max_steps=args.max_steps,
            seed=args.seed,
            turn_order=args.turn_order,
        )

    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _load_replay(path: str | None, example: str | None) -> dict[str, Any]:
    if example is not None:
        return EXAMPLES[example]

    if path is None:
        return json.load(sys.stdin)

    with Path(path).open(encoding="utf-8") as replay_file:
        return json.load(replay_file)
