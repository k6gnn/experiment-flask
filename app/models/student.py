from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    """
    Domain model mirroring the Java Student @Entity.
    Validated on construction; id is None until persisted.
    """
    name: str
    grade: float
    id: Optional[int] = None

    def __post_init__(self):
        if not self.name or not str(self.name).strip():
            raise ValueError("Student name must not be blank")
        if self.grade < 0:
            raise ValueError("Grade must be at least 0")
        if self.grade > 10:
            raise ValueError("Grade must be at most 10")

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "grade": self.grade}

    @classmethod
    def from_row(cls, row) -> "Student":
        """Build a Student from a sqlite3.Row (or dict-like object)."""
        return cls(id=row["id"], name=row["name"], grade=row["grade"])

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """Build and validate a Student from a JSON-parsed dict."""
        name = data.get("name")
        grade = data.get("grade")
        if grade is None:
            raise ValueError("grade is required")
        return cls(name=name, grade=float(grade))
