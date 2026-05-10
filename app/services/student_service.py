from typing import List, Optional
from app.models.student import Student
from app.repository.student_repository import StudentRepository


class StudentService:
    """Business logic layer — mirrors Spring StudentService."""

    def __init__(self, repository: StudentRepository = None):
        self._repo = repository or StudentRepository()

    def get_all_students(self) -> List[Student]:
        """Retrieve all students."""
        return self._repo.find_all()

    def create_student(self, student: Student) -> Student:
        """Create and persist a new student."""
        return self._repo.save(student)

    def get_grade_by_id(self, student_id: int) -> Optional[float]:
        """Get the grade for a student by ID. Returns None if not found."""
        student = self._repo.find_by_id(student_id)
        return student.grade if student is not None else None

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Return the full Student object by ID."""
        return self._repo.find_by_id(student_id)
