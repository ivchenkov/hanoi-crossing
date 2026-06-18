from dataclasses import dataclass
from typing import Literal


Turn = Literal["a", "b"]

Move = Literal[
    "lift_1",
    "lift_mid",
    "lift_3",
    "place_1",
    "place_mid",
    "place_3",
    "skip",
]


@dataclass(frozen=True)
class StepResult:
    legal: bool
    winner: Turn | None


class HanoiCrossingState:
    """
    Core game state for Hanoi Crossing.

    Stacks are stored bottom -> top.
    Example: [5, 3, 1] means 5 is bottom, 1 is top.
    """

    def __init__(self, n: int):
        if n <= 0:
            raise ValueError("n must be positive")

        self.n = n

        # Player A has odd disks: 1, 3, ..., 2n - 1
        # Player B has even disks: 2, 4, ..., 2n
        self.pole_1a = list(range(2 * n - 1, 0, -2))
        self.pole_3a = []

        self.pole_1b = list(range(2 * n, 0, -2))
        self.pole_3b = []

        self.pole_mid = []

        self.hand_a = None
        self.hand_b = None

        self.winner = None

    def get_legal_moves(self, turn: Turn) -> list[Move]:
        self._validate_turn(turn)

        if self.winner is not None:
            return []

        legal: list[Move] = ["skip"]

        hand = self._get_hand(turn)

        if hand is None:
            # Can lift from any non-empty visible pole.
            if self._pole_for(turn, "1"):
                legal.append("lift_1")
            if self.pole_mid:
                legal.append("lift_mid")
            if self._pole_for(turn, "3"):
                legal.append("lift_3")
        else:
            # Can place on any visible pole where Hanoi rule allows it.
            if self._can_place(hand, self._pole_for(turn, "1")):
                legal.append("place_1")
            if self._can_place(hand, self.pole_mid):
                legal.append("place_mid")
            if self._can_place(hand, self._pole_for(turn, "3")):
                legal.append("place_3")

        return legal

    def step(self, move: Move, turn: Turn) -> StepResult:
        self._validate_turn(turn)

        # After the game is over, the state is frozen.
        if self.winner is not None:
            return StepResult(legal=False, winner=self.winner)

        if move not in self._all_moves():
            raise ValueError(f"unknown move: {move}")

        # Illegal move wastes the turn and does not change the state.
        if move not in self.get_legal_moves(turn):
            return StepResult(legal=False, winner=self.winner)

        if move == "skip":
            return StepResult(
                legal=True,
                winner=self._update_winner(),
            )

        if move.startswith("lift_"):
            pole = self._move_to_pole(turn, move)
            disk = pole.pop()
            self._set_hand(turn, disk)

        elif move.startswith("place_"):
            pole = self._move_to_pole(turn, move)
            disk = self._get_hand(turn)

            # The move is already checked as legal, so disk is not None here.
            assert disk is not None

            pole.append(disk)
            self._set_hand(turn, None)

        return StepResult(
            legal=True,
            winner=self._update_winner(),
        )

    def to_dict(self) -> dict:
        return {
            "n": self.n,
            "winner": self.winner,
            "poles": {
                "1a": self.pole_1a.copy(),
                "2": self.pole_mid.copy(),
                "3a": self.pole_3a.copy(),
                "1b": self.pole_1b.copy(),
                "3b": self.pole_3b.copy(),
            },
            "hands": {
                "a": self.hand_a,
                "b": self.hand_b,
            },
        }

    def render(self) -> str:
        return (
            f"1a={self.pole_1a} | "
            f"2={self.pole_mid} | "
            f"3a={self.pole_3a} | "
            f"1b={self.pole_1b} | "
            f"3b={self.pole_3b} | "
            f"hand_a={self.hand_a} | "
            f"hand_b={self.hand_b} | "
            f"winner={self.winner}"
        )

    def __str__(self) -> str:
        return self.render()

    def _update_winner(self) -> Turn | None:
        if self._has_won("a"):
            self.winner = "a"
        elif self._has_won("b"):
            self.winner = "b"

        return self.winner

    def _has_won(self, turn: Turn) -> bool:
        if self._get_hand(turn) is not None:
            return False

        if self.pole_mid:
            return False

        if turn == "a":
            target_disks = list(range(2 * self.n - 1, 0, -2))
            return self.pole_1a == [] and self.pole_3a == target_disks

        target_disks = list(range(2 * self.n, 0, -2))
        return self.pole_1b == [] and self.pole_3b == target_disks

    def _move_to_pole(self, turn: Turn, move: Move) -> list[int]:
        if move.endswith("_1"):
            return self._pole_for(turn, "1")

        if move.endswith("_mid"):
            return self.pole_mid

        if move.endswith("_3"):
            return self._pole_for(turn, "3")

        raise ValueError(f"move does not refer to a pole: {move}")

    def _pole_for(self, turn: Turn, local_pole: Literal["1", "3"]) -> list[int]:
        if turn == "a":
            return self.pole_1a if local_pole == "1" else self.pole_3a

        return self.pole_1b if local_pole == "1" else self.pole_3b

    def _get_hand(self, turn: Turn) -> int | None:
        return self.hand_a if turn == "a" else self.hand_b

    def _set_hand(self, turn: Turn, disk: int | None) -> None:
        if turn == "a":
            self.hand_a = disk
        else:
            self.hand_b = disk

    @staticmethod
    def _can_place(disk: int, pole: list[int]) -> bool:
        return not pole or disk < pole[-1]

    @staticmethod
    def _validate_turn(turn: Turn) -> None:
        if turn not in ("a", "b"):
            raise ValueError(f"unknown turn: {turn}")

    @staticmethod
    def _all_moves() -> set[str]:
        return {
            "lift_1",
            "lift_mid",
            "lift_3",
            "place_1",
            "place_mid",
            "place_3",
            "skip",
        }
