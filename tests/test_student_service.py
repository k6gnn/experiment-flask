"""
Tests mirroring StudentServiceTest.java — runs with pytest OR unittest.

  - getAllStudents_shouldReturnAllStudents
  - createStudent_shouldSaveAndReturnStudent
  - getGradeById_shouldReturnGradeWhenStudentExists
  - getGradeById_shouldReturnEmptyWhenStudentNotFound
  - getStudentById_shouldReturnStudentWhenExists
"""
import unittest
from unittest.mock import MagicMock

from app.models.student import Student
from app.services.student_service import StudentService


def _make_student(student_id, name, grade):
    s = Student(name=name, grade=grade)
    s.id = student_id
    return s


class StudentServiceTest(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = StudentService(repository=self.mock_repo)
        self.student1 = _make_student(1, "Alice", 8.5)
        self.student2 = _make_student(2, "Bob", 6.0)

    # ------------------------------------------------------------------
    # get_all_students
    # ------------------------------------------------------------------

    def test_get_all_students_returns_all(self):
        """getAllStudents_shouldReturnAllStudents"""
        self.mock_repo.find_all.return_value = [self.student1, self.student2]

        result = self.service.get_all_students()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Alice")
        self.assertEqual(result[1].name, "Bob")
        self.mock_repo.find_all.assert_called_once()

    # ------------------------------------------------------------------
    # create_student
    # ------------------------------------------------------------------

    def test_create_student_saves_and_returns(self):
        """createStudent_shouldSaveAndReturnStudent"""
        new_student = Student(name="Charlie", grade=9.0)
        self.mock_repo.save.return_value = new_student

        result = self.service.create_student(new_student)

        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Charlie")
        self.assertEqual(result.grade, 9.0)
        self.mock_repo.save.assert_called_once_with(new_student)

    # ------------------------------------------------------------------
    # get_grade_by_id
    # ------------------------------------------------------------------

    def test_get_grade_by_id_returns_grade_when_exists(self):
        """getGradeById_shouldReturnGradeWhenStudentExists"""
        self.mock_repo.find_by_id.return_value = self.student1

        result = self.service.get_grade_by_id(1)

        self.assertIsNotNone(result)
        self.assertEqual(result, 8.5)

    def test_get_grade_by_id_returns_none_when_not_found(self):
        """getGradeById_shouldReturnEmptyWhenStudentNotFound"""
        self.mock_repo.find_by_id.return_value = None

        result = self.service.get_grade_by_id(99)

        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # get_student_by_id
    # ------------------------------------------------------------------

    def test_get_student_by_id_returns_student_when_exists(self):
        """getStudentById_shouldReturnStudentWhenExists"""
        self.mock_repo.find_by_id.return_value = self.student1

        result = self.service.get_student_by_id(1)

        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Alice")

    def test_get_student_by_id_returns_none_when_not_found(self):
        self.mock_repo.find_by_id.return_value = None

        result = self.service.get_student_by_id(42)

        self.assertIsNone(result)




if __name__ == "__main__":
    unittest.main()
