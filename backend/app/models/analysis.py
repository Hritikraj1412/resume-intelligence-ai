from pydantic import BaseModel, Field, field_validator


class ResumeAnalysisRequest(BaseModel):

    resume_text: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Extracted resume text"
    )

    job_description: str = Field(
        ...,
        min_length=30,
        max_length=30000,
        description="Job description text"
    )

    @field_validator(
        "resume_text",
        "job_description"
    )
    @classmethod
    def validate_text(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Text cannot be empty."
            )

        return value