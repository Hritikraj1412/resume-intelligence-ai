
import pytest

from app.services.experience_matcher import (
    calculate_total_experience_years,
    calculate_experience_match,
)


@pytest.mark.parametrize(
    ("experience", "expected"),
    [
        ([{"duration": "Jan 2025 - Mar 2025"}], 0.17),
        (
            [
                {"duration": "Jan 2025 - Jun 2025"},
                {"duration": "Apr 2025 - Aug 2025"},
            ],
            0.58,
        ),
        ([{"duration": "Jan 2027 - Dec 2027"}], 0.0),
        ([{"job_title": "Web Developer Intern", "duration": ""}], 0.0),
        ([{"duration": "Jan 2025 - Dec 2027"}], None),
    ],
)
def test_total_experience(experience, expected):
    result = calculate_total_experience_years(experience)

    if expected is None:
        # The end date must be capped at the current month.
        from datetime import datetime

        current_month = datetime.now().year * 12 + datetime.now().month - 1
        start_month = 2025 * 12
        expected = round((current_month - start_month) / 12, 2)

    assert result == pytest.approx(expected, abs=0.01)


def test_experience_match_below_requirement():
    result = calculate_experience_match(
        [{"duration": "Jan 2025 - Mar 2025"}],
        "1 year",
    )

    assert result["score"] == pytest.approx(17.0)
    assert result["status"] == "partially_meets"