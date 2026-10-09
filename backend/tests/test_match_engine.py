
import pytest

from app.services import match_engine


def fake_skill_result(score=80):
    return {
        "score": score,
        "coverage": 80.0,
        "required_coverage": 80.0,
        "preferred_coverage": 50.0,
        "matched": ["python"],
        "missing": ["sql"],
        "preferred_matched": [],
        "preferred_missing": ["docker"],
    }


def setup_mocks(
    monkeypatch,
    *,
    skill_score=80,
    semantic_score=60,
    tfidf_score=40,
    experience_score=20,
    project_score=100,
):
    monkeypatch.setattr(
        match_engine,
        "calculate_skill_match",
        lambda **kwargs: fake_skill_result(skill_score),
    )
    monkeypatch.setattr(
        match_engine,
        "calculate_semantic_similarity",
        lambda *args: semantic_score,
    )
    monkeypatch.setattr(
        match_engine,
        "calculate_tfidf_similarity",
        lambda *args: tfidf_score,
    )
    monkeypatch.setattr(
        match_engine,
        "calculate_experience_match",
        lambda *args: {
            "score": experience_score,
            "status": "partially_meets",
        },
    )
    monkeypatch.setattr(
        match_engine,
        "calculate_project_relevance",
        lambda *args: {
            "score": project_score,
            "projects": [],
        },
    )
    monkeypatch.setattr(
        match_engine,
        "calculate_evidence_quality",
        lambda **kwargs: {},
    )
    monkeypatch.setattr(
        match_engine,
        "classify_match",
        lambda **kwargs: "test_classification",
    )


def calculate(**overrides):
    args = {
        "resume_text": "Python developer with project experience",
        "job_description": "Python developer required",
        "resume_skills": ["python"],
        "required_skills": ["python", "sql"],
        "preferred_skills": ["docker"],
        "resume_experience": [{"duration": "Jan 2025 - Mar 2025"}],
        "required_experience": "1 year",
        "resume_projects": [{"name": "Test Project"}],
        "responsibilities": ["Build APIs"],
    }
    args.update(overrides)
    return match_engine.calculate_final_match(**args)


def test_final_score_with_all_components(monkeypatch):
    setup_mocks(monkeypatch)

    result = calculate()

    # 80*0.25 + 60*0.25 + 40*0.10
    # + 20*0.15 + 100*0.25 = 67
    assert result["match_score"] == pytest.approx(67.0)



def test_score_normalizes_when_projects_are_missing(monkeypatch):
    setup_mocks(monkeypatch)

    result = calculate(resume_projects=[])

    # 80*0.25 + 60*0.25 + 40*0.10 + 20*0.15 = 42
    # Remaining weights: 0.25 + 0.25 + 0.10 + 0.15 = 0.75
    # 42 / 0.75 = 56
    assert result["match_score"] == pytest.approx(56.0)


def test_score_normalizes_when_experience_is_unavailable(monkeypatch):
    setup_mocks(monkeypatch, experience_score=None)

    result = calculate()

    # Remaining weights total 0.85.
    # Weighted score = 64 / 0.85 = 75.294...
    assert result["match_score"] == pytest.approx(75.29, abs=0.01)

    
def test_scoring_metadata_with_all_components(monkeypatch):
    setup_mocks(monkeypatch)

    result = calculate()
    metadata = result["scoring_metadata"]

    assert set(metadata["included_components"]) == {
        "skill_match",
        "semantic_match",
        "tfidf_match",
        "experience_match",
        "project_relevance",
    }

    assert metadata["total_weight_before_normalization"] == pytest.approx(1.0)
    assert metadata["weights_normalized"] is False


def test_scoring_metadata_without_projects(monkeypatch):
    setup_mocks(monkeypatch)

    result = calculate(resume_projects=[])
    metadata = result["scoring_metadata"]

    assert "project_relevance" not in metadata["included_components"]
    assert metadata["total_weight_before_normalization"] == pytest.approx(0.75)
    assert metadata["weights_normalized"] is True