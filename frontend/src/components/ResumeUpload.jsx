import { useRef, useState } from "react";
import { uploadResume } from "../services/api";

function ResumeUpload({ onResumeUploaded }) {

    const inputRef = useRef(null);

    const [dragging, setDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState("");

    const processFile = async (file) => {

        setError("");

        if (!file) return;

        if (file.type !== "application/pdf") {
            setError("Please select a PDF resume.");
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            setError("Resume must be smaller than 5 MB.");
            return;
        }

        try {

            setUploading(true);

            const result = await uploadResume(file);

            onResumeUploaded(result);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.message ||
                err.response?.data?.detail ||
                "Unable to process this resume."
            );

        } finally {

            setUploading(false);

        }
    };


    const handleFileChange = (event) => {

        const file = event.target.files?.[0];

        processFile(file);

        event.target.value = "";

    };


    const handleDrop = (event) => {

        event.preventDefault();

        setDragging(false);

        const file = event.dataTransfer.files?.[0];

        processFile(file);

    };


    return (

        <div className="resume-uploader">

            <input
                ref={inputRef}
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                hidden
            />


            <div
                className={`upload-zone ${
                    dragging ? "dragging" : ""
                } ${uploading ? "uploading" : ""}`}
                onDragOver={(event) => {
                    event.preventDefault();
                    setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
            >

                <div className="upload-orbit">

                    <div className="upload-icon">

                        {uploading ? (
                            <span className="loader-ring"></span>
                        ) : (
                            "↑"
                        )}

                    </div>

                </div>


                <div className="upload-copy">

                    <h3>

                        {uploading
                            ? "Processing your resume..."
                            : "Drop your resume here"
                        }

                    </h3>

                    <p>

                        {uploading
                            ? "Extracting structured information and preparing AI analysis."
                            : "PDF format only · Maximum file size 5 MB"
                        }

                    </p>

                </div>


                {!uploading && (

                    <button
                        type="button"
                        className="upload-button"
                        onClick={() => inputRef.current?.click()}
                    >

                        <span>
                            Choose PDF
                        </span>

                        <span className="button-arrow">
                            →
                        </span>

                    </button>

                )}


                {!uploading && (

                    <div className="upload-support">

                        <span>PDF</span>
                        <span>5 MB MAX</span>
                        <span>AI PARSING</span>

                    </div>

                )}

            </div>


            {error && (

                <div className="upload-error">

                    <span>!</span>

                    {error}

                </div>

            )}

        </div>
    );
}

export default ResumeUpload;