from app.services.evidence_quality import (
    calculate_evidence_quality
)


TEST_CASES = [

    {
        "name": "Strong evidence",

        "resume_experience": [
            {
                "job_title": "Software Developer",
                "company": "ABC Technologies",
                "duration": "Jan 2024 - Jan 2026"
            },
            {
                "job_title": "Backend Developer",
                "company": "XYZ Solutions",
                "duration": "Feb 2026 - Aug 2026"
            }
        ],

        "resume_projects": [
            {
                "name": "Expense Tracker",
                "description": "React and Node.js application"
            },
            {
                "name": "AI Resume Analyzer",
                "description": "Python NLP application"
            },
            {
                "name": "Portfolio",
                "description": "Next.js developer portfolio"
            }
        ],

        "resume_skills": [
            "python",
            "react",
            "node.js",
            "sql"
        ],

        "required_skills": [
            "python",
            "react",
            "node.js",
            "sql"
        ],

        "responsibilities": [
            "Build web applications",
            "Develop APIs",
            "Work with databases"
        ]
    },

    {
        "name": "Experience only",

        "resume_experience": [
            {
                "job_title": "Software Developer",
                "company": "ABC",
                "duration": "Jan 2025 - Jan 2026"
            }
        ],

        "resume_projects": [],

        "resume_skills": [
            "python",
            "react",
            "sql"
        ],

        "required_skills": [
            "python",
            "react",
            "sql"
        ],

        "responsibilities": [
            "Build web applications"
        ]
    },

    {
        "name": "Projects only",

        "resume_experience": [],

        "resume_projects": [
            {
                "name": "Expense Tracker",
                "description": "React and Node.js application"
            },
            {
                "name": "Portfolio",
                "description": "Next.js application"
            }
        ],

        "resume_skills": [
            "python",
            "react",
            "node.js",
            "sql"
        ],

        "required_skills": [
            "python",
            "react",
            "node.js",
            "sql"
        ],

        "responsibilities": [
            "Build web applications"
        ]
    },

    {
        "name": "Skills only",

        "resume_experience": [],

        "resume_projects": [],

        "resume_skills": [
            "python",
            "react",
            "node.js",
            "sql"
        ],

        "required_skills": [
            "python",
            "react",
            "node.js",
            "sql"
        ],

        "responsibilities": []
    },

    {
        "name": "Weak evidence",

        "resume_experience": [],

        "resume_projects": [],

        "resume_skills": [
            "python"
        ],

        "required_skills": [
            "python",
            "react",
            "node.js",
            "sql"
        ],

        "responsibilities": []
    }
]


def main():

    print()
    print("=" * 60)
    print("EVIDENCE QUALITY EVALUATION")
    print("=" * 60)

    scores = []

    for index, test_case in enumerate(
        TEST_CASES,
        start=1
    ):

        result = calculate_evidence_quality(
            resume_experience=test_case[
                "resume_experience"
            ],

            resume_projects=test_case[
                "resume_projects"
            ],

            resume_skills=test_case[
                "resume_skills"
            ],

            required_skills=test_case[
                "required_skills"
            ],

            responsibilities=test_case[
                "responsibilities"
            ]
        )

        score = result["score"]

        scores.append(score)

        print()
        print("=" * 60)
        print(f"TEST CASE {index}")
        print("=" * 60)

        print(
            f"Scenario: {test_case['name']}"
        )

        print(
            f"Evidence Quality: {score}%"
        )

        print(
            f"Skill Evidence: "
            f"{result['skill_evidence']}%"
        )

        print(
            f"Experience Count: "
            f"{result['experience_count']}"
        )

        print(
            f"Project Count: "
            f"{result['project_count']}"
        )

        print(
            f"Has Experience: "
            f"{result['has_experience']}"
        )

        print(
            f"Has Projects: "
            f"{result['has_projects']}"
        )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"Test Cases: {len(scores)}"
    )

    print(
        f"Average Evidence Quality: "
        f"{sum(scores) / len(scores):.2f}%"
    )

    print(
        f"Highest Evidence Quality: "
        f"{max(scores)}%"
    )

    print(
        f"Lowest Evidence Quality: "
        f"{min(scores)}%"
    )


if __name__ == "__main__":
    main()