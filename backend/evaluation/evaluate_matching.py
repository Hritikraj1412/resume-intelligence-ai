import json
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from app.services.skill_extractor import extract_skills
from app.services.job_description_parser import parse_job_description
from app.services.match_engine import calculate_final_match
from app.services.resume_section_parser import extract_resume_sections
from app.services.experience_parser import extract_experience_entries
from app.services.project_parser import extract_project_entries


BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_FILE = (
    BASE_DIR
    / "backend"
    / "evaluation"
    / "match_test_cases.json"
)


LABELS = [
    "strong_match",
    "moderate_match",
    "weak_match"
]


def evaluate():

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        test_cases = json.load(file)

    results = []

    y_true = []
    y_pred = []

    for case in test_cases:

        resume_text = case["resume_text"]
        job_description = case["job_description"]

        # -----------------------------------------
        # RESUME
        # -----------------------------------------

        resume_sections = extract_resume_sections(
            resume_text
        )

        resume_skills = extract_skills(
            resume_text
        )

        resume_experience = extract_experience_entries(
            resume_sections["experience"]
        )

        resume_projects = extract_project_entries(
            resume_sections["projects"]
        )

        # -----------------------------------------
        # JOB DESCRIPTION
        # -----------------------------------------

        job_data = parse_job_description(
            job_description
        )

        # -----------------------------------------
        # MATCH
        # -----------------------------------------

        result = calculate_final_match(
            resume_text=resume_text,
            job_description=job_description,
            resume_skills=resume_skills,
            required_skills=job_data["required_skills"],
            preferred_skills=job_data["preferred_skills"],
            resume_experience=resume_experience,
            required_experience=job_data["experience_required"],
            resume_projects=resume_projects,
            responsibilities=job_data["responsibilities"]
        )

        score = result["match_score"]

        predicted_label = result[
            "classification"
        ]["label"]

        expected_label = case["label"]

        passed = (
            predicted_label == expected_label
        )

        y_true.append(expected_label)
        y_pred.append(predicted_label)

        results.append({
            "id": case["id"],
            "expected": expected_label,
            "predicted": predicted_label,
            "score": score,
            "passed": passed
        })

        # -----------------------------------------
        # CASE OUTPUT
        # -----------------------------------------

        print()
        print("=" * 60)
        print(f"TEST CASE {case['id']}")
        print("=" * 60)

        print(
            "Expected:",
            expected_label
        )

        print(
            "Score:",
            score
        )

        print(
            "Skill Coverage:",
            result["match_quality"]["skill_coverage"]
        )

        print(
            "Content Alignment:",
            result["match_quality"]["content_alignment"]
        )

        print(
            "Classification:",
            result["classification"]["label"]
        )

        print(
            "Classification Confidence:",
            result["classification"]["confidence"]
        )

        print("Breakdown:")

        print(
            "  Skill Match:",
            result["breakdown"]["skill_match"]
        )

        print(
            "  Semantic Match:",
            result["breakdown"]["semantic_match"]
        )

        print(
            "  TF-IDF Match:",
            result["breakdown"]["tfidf_match"]
        )

        print(
            "  Experience Match:",
            result["breakdown"]["experience_match"]
        )

        print(
            "  Project Relevance:",
            result["breakdown"]["project_relevance"]
        )

        print(
            "Predicted:",
            predicted_label
        )

        if passed:
            print("STATUS: PASSED")
        else:
            print("STATUS: FAILED")

    # -----------------------------------------
    # OVERALL RESULTS
    # -----------------------------------------

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed

    accuracy = (
        accuracy_score(
            y_true,
            y_pred
        ) * 100
        if total
        else 0
    )

    precision = (
        precision_score(
            y_true,
            y_pred,
            labels=LABELS,
            average="weighted",
            zero_division=0
        ) * 100
        if total
        else 0
    )

    recall = (
        recall_score(
            y_true,
            y_pred,
            labels=LABELS,
            average="weighted",
            zero_division=0
        ) * 100
        if total
        else 0
    )

    f1 = (
        f1_score(
            y_true,
            y_pred,
            labels=LABELS,
            average="weighted",
            zero_division=0
        ) * 100
        if total
        else 0
    )

    # -----------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS
    )

    # -----------------------------------------
    # EVALUATION REPORT
    # -----------------------------------------

    print()
    print()
    print("#" * 60)
    print("MATCHING EVALUATION")
    print("#" * 60)

    print()

    print(
        "Total test cases:",
        total
    )

    print(
        "Passed:",
        passed
    )

    print(
        "Failed:",
        failed
    )

    print()

    print(
        "Classification Accuracy:",
        round(accuracy, 2),
        "%"
    )

    print(
        "Weighted Precision:",
        round(precision, 2),
        "%"
    )

    print(
        "Weighted Recall:",
        round(recall, 2),
        "%"
    )

    print(
        "Weighted F1 Score:",
        round(f1, 2),
        "%"
    )

    # -----------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------

    print()
    print("#" * 60)
    print("CONFUSION MATRIX")
    print("#" * 60)

    print()

    print(
        "Rows = Actual"
    )

    print(
        "Columns = Predicted"
    )

    print()

    print(
        f"{'':20}"
        f"{'Strong':>12}"
        f"{'Moderate':>12}"
        f"{'Weak':>12}"
    )

    for index, label in enumerate(LABELS):

        short_label = label.replace(
            "_match",
            ""
        ).title()

        print(
            f"{short_label:20}"
            f"{matrix[index][0]:>12}"
            f"{matrix[index][1]:>12}"
            f"{matrix[index][2]:>12}"
        )

    # -----------------------------------------
    # CLASSIFICATION REPORT
    # -----------------------------------------

    print()
    print("#" * 60)
    print("PER-CLASS METRICS")
    print("#" * 60)

    print()

    print(
        classification_report(
            y_true,
            y_pred,
            labels=LABELS,
            target_names=[
                "Strong Match",
                "Moderate Match",
                "Weak Match"
            ],
            zero_division=0
        )
    )

    # -----------------------------------------
    # CASE SUMMARY
    # -----------------------------------------

    print("#" * 60)
    print("CASE SUMMARY")
    print("#" * 60)

    print()

    for result in results:

        print(
            f"Case {result['id']}: "
            f"{result['expected']} → "
            f"{result['predicted']} "
            f"({result['score']}%)"
        )


if __name__ == "__main__":
    evaluate()