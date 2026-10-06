import { useState } from "react";

const SAMPLE_JD = `Software Developer

Requirements

- Bachelor's degree in Computer Science or Engineering.
- 1-2 years of software development experience.
- Strong knowledge of Python.
- Strong knowledge of JavaScript.
- Experience with React.js.
- Experience with Node.js.
- Experience with SQL databases.
- Experience building REST APIs.
- Familiarity with Git and GitHub.

Preferred Skills

- AWS
- Docker
- Machine Learning
- MongoDB
- Next.js

Responsibilities

- Develop and maintain scalable web applications.
- Build and maintain REST APIs.
- Develop responsive frontend interfaces.
- Develop backend services using Node.js and Python.
- Work with SQL and NoSQL databases.
- Integrate APIs and third-party services.
- Write clean and maintainable code.
- Debug and troubleshoot application issues.
- Collaborate with development teams.`;

function JobDescription({
    jobDescription,
    setJobDescription
}) {

    const [focused, setFocused] = useState(false);

    const characterCount = jobDescription.length;


    const useSample = () => {

        setJobDescription(SAMPLE_JD);

    };


    const clearDescription = () => {

        setJobDescription("");

    };


    return (

        <div
            className={`jd-editor ${
                focused ? "focused" : ""
            }`}
        >

            <div className="jd-toolbar">

                <div className="jd-toolbar-left">

                    <span className="editor-dot"></span>

                    <span>
                        JOB DESCRIPTION
                    </span>

                </div>


                <div className="jd-actions">

                    <button
                        type="button"
                        onClick={useSample}
                    >
                        Use sample
                    </button>

                    <button
                        type="button"
                        onClick={clearDescription}
                        disabled={!jobDescription}
                    >
                        Clear
                    </button>

                </div>

            </div>


            <textarea
                value={jobDescription}
                onChange={(event) =>
                    setJobDescription(event.target.value)
                }
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                placeholder={`Paste the complete job description here...

Include requirements, responsibilities,
experience requirements and preferred skills.`}
                spellCheck="false"
            />


            <div className="editor-footer">

                <span>

                    {characterCount.toLocaleString()} characters

                </span>

                <span>

                    AI will extract skills, experience
                    and responsibilities

                </span>

            </div>

        </div>
    );
}

export default JobDescription;