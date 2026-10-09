import { useState } from "react";

import ResumeUpload from "./components/ResumeUpload";
import JobDescription from "./components/JobDescription";
import MatchScore from "./components/MatchScore";
import Skills from "./components/Skills";

import { analyzeResume } from "./services/api";

import "./App.css";


function App() {

    const [resume, setResume] = useState(null);
    const [jobDescription, setJobDescription] = useState("");
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);


    /* =========================================================
       ANALYZE RESUME
    ========================================================= */

    const handleAnalyze = async () => {

        if (!resume) {
            alert("Please upload your resume first.");
            return;
        }

        if (!jobDescription.trim()) {
            alert("Please enter a job description.");
            return;
        }

        try {

            setLoading(true);

            const result = await analyzeResume(
                resume.text,
                jobDescription.trim()
            );

            setAnalysis(result);

            setTimeout(() => {
                document
                    .querySelector(".results-dashboard")
                    ?.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
            }, 100);

        } catch (error) {

            console.error("Analysis error:", error);

            alert(
                error.response?.data?.detail ||
                error.response?.data?.message ||
                "Analysis failed. Please try again."
            );

        } finally {

            setLoading(false);

        }
    };


    /* =========================================================
       RESET ANALYSIS
    ========================================================= */

    const handleNewAnalysis = () => {

        setAnalysis(null);
        setResume(null);
        setJobDescription("");
        setLoading(false);

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };


    /* =========================================================
       BACKEND DATA
    ========================================================= */

    const breakdown = analysis?.breakdown ?? {};
    const skills = analysis?.skills ?? {};
    const experience = analysis?.experience ?? {};
    const classification = analysis?.classification ?? {};
    const explanation = analysis?.explanation ?? {};
    const recommendations = Array.isArray(
        analysis?.recommendations
    )
        ? analysis.recommendations
        : [];

    const projects = Array.isArray(
        analysis?.projects
    )
        ? analysis.projects
        : [];

    const quality = analysis?.match_quality ?? {};
    const evidence = analysis?.evidence_quality ?? {};
    const job = analysis?.job_analysis ?? {};


    /* =========================================================
       SAFE VALUES
    ========================================================= */

    const matchScore = Number(
        analysis?.match_score ?? 0
    );

    const classificationLabel =
        String(
            classification?.label || "pending"
        )
            .replaceAll("_", " ")
            .toUpperCase();

    const classificationConfidence = Number(
        classification?.confidence ?? 0
    );


    return (

        <div className="app">

            {/* =================================================
                AMBIENT BACKGROUND
            ================================================= */}

            <div className="ambient ambient-one"></div>
            <div className="ambient ambient-two"></div>

            <div className="grid-background"></div>


            {/* =================================================
                NAVBAR
            ================================================= */}

            <header className="navbar">

                <div className="brand">

                    <div className="brand-mark">
                        RA
                    </div>

                    <div className="brand-copy">

                        <div className="brand-name">
                            Resume<span>AI</span>
                        </div>

                        <div className="brand-subtitle">
                            INTELLIGENCE ENGINE
                        </div>

                    </div>

                </div>


                <div className="nav-status">

                    <span className="status-dot"></span>

                    AI ENGINE ONLINE

                </div>

            </header>


            {/* =================================================
                MAIN
            ================================================= */}

            <main className="container">


                {/* =================================================
                    HERO
                ================================================= */}

                <section className="hero-section">

                    <div className="hero-eyebrow">

                        <span></span>

                        AI-POWERED RESUME ANALYTICS

                    </div>


                    <h1>

                        Understand your

                        <span>
                            career match.
                        </span>

                    </h1>


                    <p className="hero-description">

                        Analyze your resume against any job description
                        using semantic AI, NLP, skill intelligence and
                        evidence-based matching.

                    </p>


                    <div className="hero-stats">

                        <div>

                            <strong>
                                01
                            </strong>

                            <span>
                                Upload Resume
                            </span>

                        </div>


                        <div>

                            <strong>
                                02
                            </strong>

                            <span>
                                Add Job Description
                            </span>

                        </div>


                        <div>

                            <strong>
                                03
                            </strong>

                            <span>
                                Run AI Analysis
                            </span>

                        </div>

                    </div>

                </section>


                {/* =================================================
                    INPUT WORKSPACE
                ================================================= */}

                <section className="workspace-section">

                    <div className="section-header">

                        <div>

                            <span className="section-number">
                                01
                            </span>

                            <div>

                                <p className="section-kicker">
                                    ANALYSIS WORKSPACE
                                </p>

                                <h2>
                                    Feed the intelligence engine.
                                </h2>

                            </div>

                        </div>

                    </div>


                    <div className="input-grid">


                        {/* =================================================
                            RESUME PANEL
                        ================================================= */}

                        <div className="input-panel">

                            <div className="panel-top">

                                <div className="panel-heading">

                                    <span className="panel-index">
                                        A
                                    </span>

                                    <div>

                                        <h3>
                                            Resume
                                        </h3>

                                        <p>
                                            Upload your PDF resume
                                        </p>

                                    </div>

                                </div>


                                <span className="panel-badge">
                                    PDF
                                </span>

                            </div>


                            <ResumeUpload
                                onResumeUploaded={setResume}
                            />

                        </div>


                        {/* =================================================
                            JOB DESCRIPTION PANEL
                        ================================================= */}

                        <div className="input-panel">

                            <div className="panel-top">

                                <div className="panel-heading">

                                    <span className="panel-index">
                                        B
                                    </span>

                                    <div>

                                        <h3>
                                            Job Description
                                        </h3>

                                        <p>
                                            Paste the target role
                                        </p>

                                    </div>

                                </div>


                                <span className="panel-badge">
                                    TEXT
                                </span>

                            </div>


                            <JobDescription
                                jobDescription={jobDescription}
                                setJobDescription={
                                    setJobDescription
                                }
                            />

                        </div>

                    </div>


                    {/* =================================================
                        RESUME LOADED
                    ================================================= */}

                    {resume && (

                        <div className="resume-loaded">

                            <div className="loaded-icon">
                                ✓
                            </div>


                            <div className="loaded-info">

                                <strong>
                                    Resume successfully loaded
                                </strong>

                                <span>
                                    {resume.filename ||
                                        "Resume.pdf"}
                                </span>

                            </div>


                            <div className="loaded-meta">

                                <span>
                                    {resume.characters ?? 0} characters
                                </span>

                                <span>
                                    PDF PARSED
                                </span>

                            </div>

                        </div>

                    )}


                    {/* =================================================
                        ANALYZE BUTTON
                    ================================================= */}

                    <button
                        className={`analyze-btn ${
                            loading ? "is-loading" : ""
                        }`}
                        onClick={handleAnalyze}
                        disabled={
                            loading ||
                            !resume ||
                            !jobDescription.trim()
                        }
                    >

                        <span className="analyze-btn-text">

                            {loading
                                ? "Running Intelligence Engine..."
                                : "Run AI Analysis"
                            }

                        </span>


                        <span className="analyze-arrow">

                            {loading
                                ? "..."
                                : "→"
                            }

                        </span>

                    </button>


                    {!resume && (

                        <p className="analysis-helper">
                            Upload a PDF resume to begin.
                        </p>

                    )}

                </section>


                {/* =================================================
                    RESULTS DASHBOARD
                ================================================= */}

                {analysis && (

                    <div className="results-dashboard">


                        {/* =================================================
                            SECTION 02 — OVERVIEW
                        ================================================= */}

                        <section className="dashboard-section overview-section">

                            <div className="section-header">

                                <div>

                                    <span className="section-number">
                                        02
                                    </span>

                                    <div>

                                        <p className="section-kicker">
                                            AI ASSESSMENT
                                        </p>

                                        <h2>
                                            Your match intelligence.
                                        </h2>

                                    </div>

                                </div>


                                <span className="analysis-live">

                                    <span></span>

                                    ANALYSIS COMPLETE

                                </span>

                            </div>


                            <div className="overview-grid">


                                {/* =================================================
                                    SCORE
                                ================================================= */}

                                <div className="score-hero">

                                    <div className="score-label">
                                        OVERALL MATCH
                                    </div>


                                    <div className="score-value">

                                        {matchScore.toFixed(1)}

                                        <span>
                                            %
                                        </span>

                                    </div>


                                    <div className="score-caption">
                                        Resume ↔ Job Description
                                    </div>


                                    <div className="score-bar">

                                        <div
                                            style={{
                                                width: `${Math.min(
                                                    Math.max(
                                                        matchScore,
                                                        0
                                                    ),
                                                    100
                                                )}%`
                                            }}
                                        ></div>

                                    </div>

                                </div>


                                {/* =================================================
                                    CLASSIFICATION
                                ================================================= */}

                                <div className="classification-card">

                                    <span className="card-label">
                                        AI CLASSIFICATION
                                    </span>


                                    <div className="classification-value">

                                        {classificationLabel}

                                    </div>


                                    <p>

                                        Classification is derived from
                                        the configured match score,
                                        skill coverage and content
                                        alignment rules.

                                    </p>


                                   <div className="classification-note">
    Rule-based classification — not a probability of correctness.
</div>

                                </div>

                            </div>


                            {/* =================================================
                                METRICS
                            ================================================= */}

                            
<div className="metric-grid">
    <Metric
        label="Skill Match"
        value={breakdown.skill_match}
    />

    <Metric
        label="Semantic AI"
        value={breakdown.semantic_match}
    />

    <Metric
        label="Keyword Similarity"
        value={breakdown.tfidf_match}
    />

    {breakdown.experience_match != null && (
        <Metric
            label="Experience"
            value={breakdown.experience_match}
        />
    )}

    {analysis?.experience?.score != null &&
        breakdown.experience_match == null && (
            <Metric
                label="Experience"
                value={analysis.experience.score}
            />
        )}

    {Array.isArray(analysis?.projects) &&
        analysis.projects.length > 0 &&
        breakdown.project_relevance != null && (
            <Metric
                label="Project Relevance"
                value={breakdown.project_relevance}
            />
        )}
</div>

                        </section>


                        {/* =================================================
                            SECTION 03 — SKILLS
                        ================================================= */}

                        <section className="dashboard-section">

                            <div className="section-header">

                                <div>

                                    <span className="section-number">
                                        03
                                    </span>

                                    <div>

                                        <p className="section-kicker">
                                            SKILL INTELLIGENCE
                                        </p>

                                        <h2>
                                            What matches. What is missing.
                                        </h2>

                                    </div>

                                </div>

                            </div>


                            <Skills
                                skills={skills}
                            />


                            <div className="coverage-grid">

                                <Coverage
                                    label="Required Skills"
                                    value={
                                        quality.required_skill_coverage
                                    }
                                />


                                <Coverage
                                    label="Preferred Skills"
                                    value={
                                        quality.preferred_skill_coverage
                                    }
                                />


                                <Coverage
                                    label="Evidence Quality"
                                    value={
                                        evidence.score
                                    }
                                />

                            </div>

                        </section>


                        {/* =================================================
                            SECTION 04 — EXPERIENCE
                        ================================================= */}

                        <section className="dashboard-section">

                            <div className="section-header">

                                <div>

                                    <span className="section-number">
                                        04
                                    </span>

                                    <div>

                                        <p className="section-kicker">
                                            EXPERIENCE INTELLIGENCE
                                        </p>

                                        <h2>
                                            Professional experience analysis.
                                        </h2>

                                    </div>

                                </div>

                            </div>


                            
<div className="experience-grid">

    <div className="experience-main">
        <span className="card-label">
            DETECTED EXPERIENCE
        </span>

        <div className="experience-years">
            {experience.resume_years == null
                ? "—"
                : Number(experience.resume_years).toFixed(2)}

            <span>years</span>
        </div>

        <p>
            {experience.resume_years == null
                ? "Experience data is unavailable."
                : "Estimated experience detected from the submitted resume."}
        </p>
    </div>

    <div className="experience-main">
        <span className="card-label">
            JOB REQUIREMENT
        </span>

        <div className="experience-years">
            {experience.required_years == null
                ? "—"
                : Number(experience.required_years).toFixed(2)}

            {experience.required_years != null && (
                <span>years</span>
            )}
        </div>

        <p>
            {experience.status === "not_required"
                ? "No numeric experience requirement was specified."
                : experience.required_years == null
                    ? "The required experience could not be determined."
                    : "Numeric experience requirement extracted from the job description."}
        </p>
    </div>

    <div className="experience-status">
        <span className="card-label">STATUS</span>

        <strong>
            {String(experience.status || "unknown")
                .replaceAll("_", " ")
                .toUpperCase()}
        </strong>

        <div className="status-line">
            {experience.score == null
                ? "Not scored"
                : `${Number(experience.score).toFixed(1)}% alignment`}
        </div>
    </div>

</div>

                        </section>


                        {/* =================================================
                            SECTION 05 — PROJECTS
                        ================================================= */}

                        <section className="dashboard-section">

                            <div className="section-header">

                                <div>

                                    <span className="section-number">
                                        05
                                    </span>

                                    <div>

                                        <p className="section-kicker">
                                            PROJECT INTELLIGENCE
                                        </p>

                                        <h2>
                                            Evidence from your projects.
                                        </h2>

                                    </div>

                                </div>

                            </div>


                            <div className="projects-analysis">

                                {projects.length > 0 ? (

                                    projects.map(
                                        (
                                            project,
                                            index
                                        ) => (

                                            <article
                                                className="project-analysis-card"
                                                key={
                                                    project.project ||
                                                    index
                                                }
                                            >

                                                <div className="project-analysis-top">

                                                    <span>
                                                        PROJECT{" "}
                                                        {String(
                                                            index + 1
                                                        ).padStart(
                                                            2,
                                                            "0"
                                                        )}
                                                    </span>


                                                    <strong>
                                                        {Number(
                                                            project.score ??
                                                            0
                                                        ).toFixed(1)}
                                                        %
                                                    </strong>

                                                </div>


                                                <h3>
                                                    {project.project ||
                                                        "Untitled Project"}
                                                </h3>


                                                <div className="project-analysis-metrics">

                                                    <div>

                                                        <span>
                                                            SKILLS
                                                        </span>

                                                        <strong>
                                                            {Number(
                                                                project.skill_score ??
                                                                0
                                                            ).toFixed(1)}
                                                            %
                                                        </strong>

                                                    </div>


                                                    <div>

                                                        <span>
                                                            SEMANTIC
                                                        </span>

                                                        <strong>
                                                            {Number(
                                                                project.semantic_score ??
                                                                0
                                                            ).toFixed(1)}
                                                            %
                                                        </strong>

                                                    </div>

                                                </div>


                                                <div className="mini-progress">

                                                    <div
                                                        style={{
                                                            width: `${Math.min(
                                                                Math.max(
                                                                    Number(
                                                                        project.score ??
                                                                        0
                                                                    ),
                                                                    0
                                                                ),
                                                                100
                                                            )}%`
                                                        }}
                                                    ></div>

                                                </div>


                                                {project.matched_skills?.length >
                                                    0 && (

                                                    <div className="project-skills">

                                                        {project.matched_skills.map(
                                                            (
                                                                skill
                                                            ) => (

                                                                <span
                                                                    key={
                                                                        skill
                                                                    }
                                                                >
                                                                    {skill}
                                                                </span>

                                                            )
                                                        )}

                                                    </div>

                                                )}

                                            </article>

                                        )
                                    )

                                ) : (

                                    <div className="empty-state">
                                        No project evidence detected.
                                    </div>

                                )}

                            </div>

                        </section>


                        {/* =================================================
                            SECTION 06 — EXPLAINABLE AI
                        ================================================= */}

                        <section className="dashboard-section">

                            <div className="section-header">

                                <div>

                                    <span className="section-number">
                                        06
                                    </span>

                                    <div>

                                        <p className="section-kicker">
                                            EXPLAINABLE AI
                                        </p>

                                        <h2>
                                            Why the system reached this result.
                                        </h2>

                                    </div>

                                </div>

                            </div>


                            <div className="insight-grid">

                                <Insight
                                    title="Strengths"
                                    icon="+"
                                    items={
                                        explanation.strengths
                                    }
                                    type="positive"
                                />


                                <Insight
                                    title="Gaps"
                                    icon="−"
                                    items={
                                        explanation.gaps
                                    }
                                    type="negative"
                                />


                                <Insight
                                    title="Warnings"
                                    icon="!"
                                    items={
                                        explanation.warnings
                                    }
                                    type="warning"
                                />

                            </div>

                        </section>


                        {/* =================================================
                            SECTION 07 — RECOMMENDATIONS
                        ================================================= */}

                        <section className="dashboard-section recommendations-section">

                            <div className="section-header">

                                <div>

                                    <span className="section-number">
                                        07
                                    </span>

                                    <div>

                                        <p className="section-kicker">
                                            AI RECOMMENDATIONS
                                        </p>

                                        <h2>
                                            Your next improvements.
                                        </h2>

                                    </div>

                                </div>

                            </div>


                            <div className="recommendations-list">

                                {recommendations.length > 0 ? (

                                    recommendations.map(
                                        (
                                            item,
                                            index
                                        ) => (

                                            <article
                                                className="recommendation"
                                                key={
                                                    item.title ||
                                                    index
                                                }
                                            >

                                                <div className="recommendation-number">

                                                    {String(
                                                        index + 1
                                                    ).padStart(
                                                        2,
                                                        "0"
                                                    )}

                                                </div>


                                                <div className="recommendation-content">

                                                    <div className="recommendation-top">

                                                        <span>

                                                            {String(
                                                                item.priority ||
                                                                "INFO"
                                                            ).toUpperCase()}

                                                        </span>


                                                        <h3>

                                                            {item.title ||
                                                                "Recommendation"}

                                                        </h3>

                                                    </div>


                                                    <p>

                                                        {item.recommendation ||
                                                            item.description ||
                                                            "Review your resume against the detected job requirements."}

                                                    </p>

                                                </div>


                                                <div className="recommendation-arrow">
                                                    →
                                                </div>

                                            </article>

                                        )
                                    )

                                ) : (

                                    <div className="empty-state">
                                        No recommendations generated.
                                    </div>

                                )}

                            </div>

                        </section>


                        {/* =================================================
                            SECTION 08 — JOB INTELLIGENCE
                        ================================================= */}

                        <section className="dashboard-section job-section">

                            <div className="section-header">

                                <div>

                                    <span className="section-number">
                                        08
                                    </span>

                                    <div>

                                        <p className="section-kicker">
                                            JOB INTELLIGENCE
                                        </p>

                                        <h2>
                                            What the role is asking for.
                                        </h2>

                                    </div>

                                </div>

                            </div>


                            <div className="job-summary-grid">


                                <div className="job-title-card">

                                    <span className="card-label">
                                        DETECTED ROLE
                                    </span>


                                    <h3>
                                        {job.job_title ||
                                            "Software Role"}
                                    </h3>

                                </div>


                                <div className="job-stat">

                                    <span>
                                        REQUIRED SKILLS
                                    </span>

                                    <strong>
                                        {Array.isArray(
                                            job.required_skills
                                        )
                                            ? job.required_skills.length
                                            : 0}
                                    </strong>

                                </div>


                                <div className="job-stat">

                                    <span>
                                        PREFERRED SKILLS
                                    </span>

                                    <strong>
                                        {Array.isArray(
                                            job.preferred_skills
                                        )
                                            ? job.preferred_skills.length
                                            : 0}
                                    </strong>

                                </div>


                                <div className="job-stat">

                                    <span>
                                        EXPERIENCE
                                    </span>

                                    <strong>
                                        {job.experience_required ||
                                            "N/A"}
                                    </strong>

                                </div>

                            </div>


                            {/* =================================================
                                RESPONSIBILITIES
                            ================================================= */}

                            {Array.isArray(
                                job.responsibilities
                            ) &&
                                job.responsibilities.length >
                                    0 && (

                                    <div className="job-responsibilities">

                                        <div className="card-label">
                                            DETECTED RESPONSIBILITIES
                                        </div>


                                        <div className="responsibility-list">

                                            {job.responsibilities.map(
                                                (
                                                    responsibility,
                                                    index
                                                ) => (

                                                    <div
                                                        className="responsibility-item"
                                                        key={
                                                            index
                                                        }
                                                    >

                                                        <span>
                                                            {String(
                                                                index +
                                                                    1
                                                            ).padStart(
                                                                2,
                                                                "0"
                                                            )}
                                                        </span>

                                                        <p>
                                                            {
                                                                responsibility
                                                            }
                                                        </p>

                                                    </div>

                                                )
                                            )}

                                        </div>

                                    </div>

                                )}

                        </section>


                        {/* =================================================
                            START NEW ANALYSIS
                        ================================================= */}

                        <div className="new-analysis-wrapper">

                            <button
                                className="new-analysis-btn"
                                onClick={
                                    handleNewAnalysis
                                }
                            >

                                <span>
                                    Start New Analysis
                                </span>

                                <span>
                                    ↗
                                </span>

                            </button>

                        </div>


                        {/* =================================================
                            FOOTNOTE
                        ================================================= */}

                        <div className="analysis-footnote">

                            <span className="footnote-dot"></span>

                            AI-generated analysis based on the submitted
                            resume and job description. Scores represent
                            content alignment and are not hiring
                            probabilities.

                        </div>

                    </div>

                )}

            </main>


            {/* =================================================
                FOOTER
            ================================================= */}

            <footer className="footer">

                <div className="footer-brand">

                    RESUME<span>AI</span>

                </div>


                <p>
                    Intelligent resume analysis engine
                </p>


                <span>
                    v1.0 • AI / NLP
                </span>

            </footer>

        </div>
    );
}


/* =========================================================
   METRIC COMPONENT
========================================================= */

function Metric({
    label,
    value
}) {

    const number = Number(value ?? 0);

    const safeNumber = Number.isFinite(number)
        ? Math.max(
            0,
            Math.min(
                number,
                100
            )
        )
        : 0;


    return (

        <div className="metric-card">

            <span>
                {label}
            </span>


            <strong>

                {safeNumber.toFixed(1)}

                <small>
                    %
                </small>

            </strong>


            <div className="metric-line">

                <div
                    style={{
                        width: `${safeNumber}%`
                    }}
                ></div>

            </div>

        </div>
    );
}


/* =========================================================
   COVERAGE COMPONENT
========================================================= */

function Coverage({
    label,
    value
}) {

    const number = Number(value ?? 0);

    const safeNumber = Number.isFinite(number)
        ? Math.max(
            0,
            Math.min(
                number,
                100
            )
        )
        : 0;


    return (

        <div className="coverage-card">

            <div>

                <span>
                    {label}
                </span>


                <strong>
                    {safeNumber.toFixed(0)}%
                </strong>

            </div>


            <div className="coverage-track">

                <div
                    style={{
                        width: `${safeNumber}%`
                    }}
                ></div>

            </div>

        </div>
    );
}


/* =========================================================
   INSIGHT COMPONENT
========================================================= */

function Insight({
    title,
    icon,
    items = [],
    type
}) {

    const safeItems = Array.isArray(items)
        ? items
        : [];


    return (

        <div
            className={`insight-card ${type}`}
        >

            <div className="insight-heading">

                <span className="insight-icon">
                    {icon}
                </span>


                <h3>
                    {title}
                </h3>


                <span className="insight-count">
                    {safeItems.length}
                </span>

            </div>


            <div className="insight-items">

                {safeItems.length > 0 ? (

                    safeItems.map(
                        (
                            item,
                            index
                        ) => (

                            <div
                                className="insight-item"
                                key={index}
                            >

                                {item}

                            </div>

                        )
                    )

                ) : (

                    <div className="insight-empty">
                        Nothing detected.
                    </div>

                )}

            </div>

        </div>
    );
}


export default App;