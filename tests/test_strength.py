
from app.services.strength_service import analyze_password


def test_strength_result_contains_required_fields():
    result = analyze_password("MyPassword123!")

    expected_fields = [
        "length",
        "diversity",
        "score",
        "strength",
        "estimated_guesses",
        "feedback"
    ]

    for field in expected_fields:
        assert field in result


def test_strength_score_range():
    result = analyze_password("MyPassword123!")

    assert 0 <= result["score"] <= 4


def test_password_length():
    result = analyze_password("Hello123!")

    assert result["length"] == 9


def test_empty_password():
    result = analyze_password("")

    assert result["length"] == 0


def test_character_diversity():
    result = analyze_password("Abc123!")

    assert result["diversity"] == 4
