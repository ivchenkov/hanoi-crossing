import pytest

from hanoi_crossing.engine import HanoiCrossingState


def test_initial_state_n2():
    state = HanoiCrossingState(2)

    assert state.to_dict() == {
        "n": 2,
        "winner": None,
        "poles": {
            "1a": [3, 1],
            "2": [],
            "3a": [],
            "1b": [4, 2],
            "3b": [],
        },
        "hands": {"a": None, "b": None},
    }


def test_n_must_be_positive():
    with pytest.raises(ValueError):
        HanoiCrossingState(0)


def test_legal_moves_with_empty_hand_are_visible_lifts_and_skip():
    state = HanoiCrossingState(1)

    assert state.get_legal_moves("a") == ["skip", "lift_1"]
    assert state.get_legal_moves("b") == ["skip", "lift_1"]


def test_lift_and_place_updates_state():
    state = HanoiCrossingState(1)

    lift = state.step("lift_1", "a")
    place = state.step("place_3", "a")

    assert lift.legal is True
    assert place.legal is True
    assert state.to_dict()["poles"]["1a"] == []
    assert state.to_dict()["poles"]["3a"] == [1]
    assert state.to_dict()["hands"]["a"] is None


def test_illegal_move_wastes_turn_without_mutating_state():
    state = HanoiCrossingState(1)
    before = state.to_dict()

    result = state.step("place_3", "a")

    assert result.legal is False
    assert state.to_dict() == before


def test_cannot_place_larger_disk_on_smaller_disk():
    state = HanoiCrossingState(1)

    state.step("lift_1", "a")
    state.step("place_mid", "a")
    state.step("lift_1", "b")

    assert "place_mid" not in state.get_legal_moves("b")
    before = state.to_dict()
    result = state.step("place_mid", "b")

    assert result.legal is False
    assert state.to_dict() == before


def test_both_players_can_lift_from_shared_pole():
    state = HanoiCrossingState(1)

    state.step("lift_1", "a")
    state.step("place_mid", "a")

    assert "lift_mid" in state.get_legal_moves("b")

    result = state.step("lift_mid", "b")

    assert result.legal is True
    assert state.to_dict()["hands"]["b"] == 1
    assert state.to_dict()["poles"]["2"] == []


def test_example_a_wins_with_arbitrary_turn_order():
    state = HanoiCrossingState(1)

    assert state.step("lift_1", "a").winner is None
    assert state.step("lift_1", "b").winner is None
    result = state.step("place_3", "a")

    assert result.winner == "a"
    assert state.winner == "a"


def test_b_can_win():
    state = HanoiCrossingState(1)

    state.step("lift_1", "b")
    result = state.step("place_3", "b")

    assert result.winner == "b"
    assert state.to_dict()["poles"]["3b"] == [2]


def test_state_is_frozen_after_win():
    state = HanoiCrossingState(1)

    state.step("lift_1", "a")
    state.step("place_3", "a")
    before = state.to_dict()
    result = state.step("lift_1", "b")

    assert result.legal is False
    assert result.winner == "a"
    assert state.to_dict() == before


def test_unknown_move_and_turn_raise():
    state = HanoiCrossingState(1)

    with pytest.raises(ValueError):
        state.step("dance", "a")

    with pytest.raises(ValueError):
        state.get_legal_moves("c")
