from app.services.job_description_parser import parse_job_description
from app.services.match_engine import calculate_final_match
from app.services.resume_section_parser import extract_resume_sections
from app.services.experience_parser import extract_experience_entries
from app.services.project_parser import extract_project_entries
from app.services.skill_extractor import extract_skills


TEST_CASES = [
    {
        "name": "Strong technical match",
        "resume": """
        Software Developer with Python, JavaScript, React, Node.js,
        SQL, Git and REST API experience.
        Built scalable web applications and REST APIs.
        """,
        "job": """
        Software Developer
        Requirements
        Python, JavaScript, React, Node.js, SQL, Git, REST APIs

        Responsibilities
        Develop scalable web applications.
        Build and maintain REST APIs.
        """
    },
    {
        "name": "Same skills, different wording",
        "resume": """
        Full stack engineer experienced in Python and JS.
        Built frontend interfaces using React and backend services
        using Node. Developed API-based web applications.
        """,
        "job": """
        Web Developer
        Requirements
        Python, JavaScript, React, Node.js, REST API

        Responsibilities
        Create modern web applications and backend API services.
        """
    },
    {
        "name": "Unrelated candidate",
        "resume": """
        Mechanical engineering student experienced in CAD,
        manufacturing, AutoCAD and mechanical design.
        """,
        "job": """
        Software Developer
        Requirements
        Python, React, Node.js, SQL, Git

        Responsibilities
        Develop web applications and REST APIs.
        """
    },
    {
        "name": "Partial skill match",
        "resume": """
        Python developer with experience in Flask and SQL.
        Built backend applications and database systems.
        """,
        "job": """
        Full Stack Developer
        Requirements
        Python, React, Node.js, SQL, REST API

        Responsibilities
        Build frontend and backend web applications.
        """
    },
    {
        "name": "Relevant project evidence",
        "resume": """
        Computer Science student.

        Projects
        Expense Tracker: Built using React.js, Node.js and SQL.
        Portfolio: Built using Next.js and HTML CSS.
        """,
        "job": """
        Frontend Developer
        Requirements
        React, JavaScript, HTML, CSS, Node.js

        Responsibilities
        Build responsive web applications and frontend interfaces.
        """
    }
]


def run_test(case):

    resume_text = case["resume"]
    job_description = case["job"]

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

    job_data = parse_job_description(
        job_description
    )

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

    return result


def main():

    print()
    print("=" * 60)
    print("MATCHING EDGE-CASE SANITY TEST")
    print("=" * 60)

    for index, case in enumerate(
        TEST_CASES,
        start=1
    ):

        result = run_test(case)

        print()
        print("-" * 60)
        print(f"CASE {index}: {case['name']}")
        print("-" * 60)

        print(
            "Match Score:",
            result["match_score"]
        )

        print(
            "Classification:",
            result["classification"]["label"]
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
            "Matched Skills:",
            result["skills"]["matched"]
        )

        print(
            "Missing Skills:",
            result["skills"]["missing_required"]
        )


if __name__ == "__main__":
    main()