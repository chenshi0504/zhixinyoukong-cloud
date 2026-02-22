from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class ReportRead(BaseModel):
    id: int
    task_id: int | None
    student_id: int | None
    original_filename: str | None
    file_size: int | None
    score: int | None
    feedback: str | None
    grader_id: int | None
    status: str
    submitted_at: datetime
    graded_at: datetime | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GradeRequest(BaseModel):
    score: int
    feedback: str | None = None

    @field_validator("score")
    @classmethod
    def score_range(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("score must be between 0 and 100")
        return v
