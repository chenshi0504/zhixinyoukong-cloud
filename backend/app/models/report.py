from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tasks.id"), index=True)
    student_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    file_path: Mapped[str | None] = mapped_column(String(500))
    original_filename: Mapped[str | None] = mapped_column(String(255))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    score: Mapped[int | None] = mapped_column(Integer)          # 0-100
    feedback: Mapped[str | None] = mapped_column(Text)
    grader_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="submitted")  # submitted/graded
    submitted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    graded_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    task: Mapped["Task"] = relationship("Task", back_populates="reports")
    student: Mapped["User"] = relationship("User", back_populates="reports_submitted", foreign_keys=[student_id])
    grader: Mapped["User"] = relationship("User", back_populates="reports_graded", foreign_keys=[grader_id])
