import json
from pathlib import Path

from app.services.skill_extractor import extract_skills


BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_FILE = (
    BASE_DIR
    / "backend"
    / "evaluation"
    / "skill_test_cases.json"
)


def calculate_metrics(expected, predicted):

    expected_set = set(expected)
    predicted_set = set(predicted)

    true_positive = len(
        expected_set.intersection(predicted_set)
    )

    false_positive = len(
        predicted_set - expected_set
    )

    false_negative = len(
        expected_set - predicted_set
    )

    if true_positive + false_positive == 0:
        precision = 0.0
    else:
        precision = (
            true_positive
            / (true_positive + false_positive)
        )

    if true_positive + false_negative == 0:
        recall = 0.0
    else:
        recall = (
            true_positive
            / (true_positive + false_negative)
        )

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = (
            2 * precision * recall
            / (precision + recall)
        )

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def evaluate():

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        test_cases = json.load(file)

    total_tp = 0
    total_fp = 0
    total_fn = 0

    for index, case in enumerate(test_cases, start=1):

        text = case["text"]
        expected = case["expected"]

        predicted = extract_skills(text)

        metrics = calculate_metrics(
            expected,
            predicted
        )

        total_tp += metrics["true_positive"]
        total_fp += metrics["false_positive"]
        total_fn += metrics["false_negative"]

        print()
        print("=" * 60)
        print(f"TEST CASE {index}")
        print("=" * 60)

        print("Text:")
        print(text)

        print()
        print("Expected:")
        print(expected)

        print()
        print("Predicted:")
        print(predicted)

        print()
        print("Precision:", round(metrics["precision"] * 100, 2))
        print("Recall:", round(metrics["recall"] * 100, 2))
        print("F1:", round(metrics["f1"] * 100, 2))

    # -----------------------------------------
    # OVERALL METRICS
    # -----------------------------------------

    if total_tp + total_fp == 0:
        overall_precision = 0.0
    else:
        overall_precision = (
            total_tp
            / (total_tp + total_fp)
        )

    if total_tp + total_fn == 0:
        overall_recall = 0.0
    else:
        overall_recall = (
            total_tp
            / (total_tp + total_fn)
        )

    if overall_precision + overall_recall == 0:
        overall_f1 = 0.0
    else:
        overall_f1 = (
            2
            * overall_precision
            * overall_recall
            / (overall_precision + overall_recall)
        )

    print()
    print()
    print("#" * 60)
    print("OVERALL SKILL EXTRACTION EVALUATION")
    print("#" * 60)

    print()
    print("True Positives:", total_tp)
    print("False Positives:", total_fp)
    print("False Negatives:", total_fn)

    print()
    print(
        "Precision:",
        round(overall_precision * 100, 2),
        "%"
    )

    print(
        "Recall:",
        round(overall_recall * 100, 2),
        "%"
    )

    print(
        "F1 Score:",
        round(overall_f1 * 100, 2),
        "%"
    )


if __name__ == "__main__":
    evaluate()