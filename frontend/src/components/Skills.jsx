function Skills({ skills }) {

    const matched = skills?.matched ?? [];
    const missing = skills?.missing_required ?? [];
    const preferredMatched = skills?.preferred_matched ?? [];
    const preferredMissing = skills?.preferred_missing ?? [];


    return (

        <div className="skills-intelligence">


            <SkillGroup
                number="01"
                title="Matched skills"
                description="Required skills detected in your resume."
                skills={matched}
                type="matched"
            />


            <SkillGroup
                number="02"
                title="Required gaps"
                description="Required skills not detected in your resume."
                skills={missing}
                type="missing"
            />


            <SkillGroup
                number="03"
                title="Preferred matches"
                description="Additional preferred skills already present."
                skills={preferredMatched}
                type="preferred"
            />


            <SkillGroup
                number="04"
                title="Preferred gaps"
                description="Preferred skills not detected."
                skills={preferredMissing}
                type="optional"
            />

        </div>
    );
}


function SkillGroup({
    number,
    title,
    description,
    skills,
    type
}) {

    return (

        <div className={`skill-group ${type}`}>

            <div className="skill-group-heading">

                <span className="skill-number">
                    {number}
                </span>

                <div>

                    <h3>
                        {title}
                    </h3>

                    <p>
                        {description}
                    </p>

                </div>

                <span className="skill-count">
                    {skills.length}
                </span>

            </div>


            <div className="skill-tags">

                {skills.length > 0 ? (

                    skills.map((skill) => (

                        <span
                            key={skill}
                            className="skill-tag"
                        >

                            <i></i>

                            {skill}

                        </span>

                    ))

                ) : (

                    <span className="skill-empty">
                        None detected
                    </span>

                )}

            </div>

        </div>
    );
}

export default Skills;