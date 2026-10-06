from app.services.skill_extractor import extract_skills


TEST_CASES = [
    {
        "text": "I love JavaScript and ReactJS development.",
        "should_contain": [
            "javascript",
            "react"
        ]
    },

    {
        "text": "Experienced with NodeJS, Node.js and ExpressJS.",
        "should_contain": [
            "node.js",
            "express"
        ]
    },

    {
        "text": "Worked with Python, PYTHON, and python3.",
        "should_contain": [
            "python"
        ]
    },

    {
        "text": "Built REST APIs using FastAPI.",
        "should_contain": [
            "rest api",
            "fastapi"
        ]
    },

    {
        "text": "Machine-learning projects using scikit learn.",
        "should_contain": [
            "machine learning",
            "scikit-learn"
        ]
    },

    {
        "text": "Frontend: HTML5, CSS3, React.js and Next.js.",
        "should_contain": [
            "html",
            "css",
            "react",
            "next.js"
        ]
    },

    {
        "text": "Database experience: MySQL, MongoDB and PostgreSQL.",
        "should_contain": [
            "mysql",
            "mongodb",
            "postgresql"
        ]
    },

    {
        "text": "Cloud experience with AWS and Azure.",
        "should_contain": [
            "aws",
            "azure"
        ]
    },

    {
        "text": "Used Git and GitHub for version control.",
        "should_contain": [
            "git",
            "github"
        ]
    },

    {
        "text": "Developed ML models using TensorFlow and PyTorch.",
        "should_contain": [
            "machine learning",
            "tensorflow",
            "pytorch"
        ]
    }
]


def run_tests():

    passed = 0
    failed = 0

    for index, case in enumerate(TEST_CASES, start=1):

        text = case["text"]

        expected = set(
            case["should_contain"]
        )

        predicted = set(
            extract_skills(text)
        )

        missing = expected - predicted

        print()
        print("=" * 60)
        print(f"TEST {index}")
        print("=" * 60)

        print("Text:")
        print(text)

        print()
        print("Expected:")
        print(sorted(expected))

        print()
        print("Detected:")
        print(sorted(predicted))

        if missing:

            failed += 1

            print()
            print("❌ FAILED")
            print("Missing:", sorted(missing))

        else:

            passed += 1

            print()
            print("✅ PASSED")

    print()
    print("#" * 60)
    print("EDGE CASE SUMMARY")
    print("#" * 60)

    print()
    print("Total tests:", len(TEST_CASES))
    print("Passed:", passed)
    print("Failed:", failed)

    if failed == 0:
        print()
        print("All edge-case tests passed.")
    else:
        print()
        print("Some edge cases need improvement.")


if __name__ == "__main__":
    run_tests()