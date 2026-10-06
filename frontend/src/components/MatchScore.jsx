function MatchScore({ score }) {

    const value = Math.max(
        0,
        Math.min(
            100,
            Number(score) || 0
        )
    );

    const radius = 94;

    const circumference =
        2 * Math.PI * radius;

    const offset =
        circumference -
        (value / 100) * circumference;


    return (

        <div className="match-score-card">

            <div className="score-ring">

                <svg
                    viewBox="0 0 220 220"
                    aria-label={`Match score ${value}%`}
                >

                    <circle
                        className="score-track"
                        cx="110"
                        cy="110"
                        r={radius}
                    />

                    <circle
                        className="score-progress"
                        cx="110"
                        cy="110"
                        r={radius}
                        style={{
                            strokeDasharray: circumference,
                            strokeDashoffset: offset
                        }}
                    />

                </svg>


                <div className="score-center">

                    <span>
                        MATCH
                    </span>

                    <strong>
                        {value.toFixed(1)}
                    </strong>

                    <small>
                        %
                    </small>

                </div>

            </div>


            <div className="score-copy">

                <span className="eyebrow">
                    OVERALL ALIGNMENT
                </span>

                <h2>
                    Resume compatibility
                </h2>

                <p>
                    This score represents the detected alignment
                    between your resume and the submitted job
                    description.
                </p>

                <div className="score-note">

                    <span></span>

                    AI-generated alignment score

                </div>

            </div>

        </div>
    );
}

export default MatchScore;