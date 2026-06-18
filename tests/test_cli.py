from hanoi_crossing.cli import EXAMPLES, run_random, run_replay


def test_builtin_replay_example_wins_for_a():
    output = run_replay(EXAMPLES["n1"])

    assert output["mode"] == "replay"
    assert output["winner"] == "a"
    assert len(output["history"]) == 3
    assert all(step["legal"] for step in output["history"])


def test_replay_records_illegal_steps():
    output = run_replay(
        {
            "n": 1,
            "steps": [
                {"turn": "a", "move": "place_3"},
                {"turn": "a", "move": "lift_1"},
            ],
        }
    )

    assert output["history"][0]["legal"] is False
    assert output["history"][1]["legal"] is True
    assert output["winner"] is None


def test_random_play_is_deterministic_with_seed():
    first = run_random(n=2, max_steps=20, seed=7)
    second = run_random(n=2, max_steps=20, seed=7)

    assert first == second


def test_random_play_uses_requested_step_limit():
    output = run_random(n=2, max_steps=5, seed=1)

    assert len(output["history"]) <= 5
