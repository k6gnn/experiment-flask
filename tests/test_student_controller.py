"""
Tests mirroring StudentControllerTest.java — runs with pytest and unittest.

  test_get_all_students_returns_200_with_list
  test_create_student_returns_201_with_created
  test_get_student_grade_returns_200_when_student_exists
  test_get_student_grade_returns_404_when_student_not_found
  test_create_student_returns_400_when_name_is_blank
  test_create_student_returns_400_when_grade_exceeds_maximum
  test_create_student_returns_400_when_grade_below_minimum
  test_create_student_returns_400_when_body_missing
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from app import create_app
from app.models.student import Student
import app.routes.student_routes as routes_module

TEST_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
}


def _make_student(student_id, name, grade):
    s = Student(name=name, grade=grade)
    s.id = student_id
    return s


class StudentControllerTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

    # ------------------------------------------------------------------
    # GET /students
    # ------------------------------------------------------------------

    def test_get_all_students_returns_200_with_list(self):
        """getAllStudents_shouldReturn200WithStudentList"""
        s1 = _make_student(1, "Alice", 8.5)
        s2 = _make_student(2, "Bob", 6.0)

        mock_service = MagicMock()
        mock_service.get_all_students.return_value = [s1, s2]

        with patch.object(routes_module, "_get_service", return_value=mock_service):
            response = self.client.get("/students")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Alice")
        self.assertEqual(data[1]["name"], "Bob")

    # ------------------------------------------------------------------
    # POST /students
    # ------------------------------------------------------------------

    def test_create_student_returns_201_with_created(self):
        """createStudent_shouldReturn201WithCreatedStudent"""
        new_student = _make_student(3, "Charlie", 9.0)

        mock_service = MagicMock()
        mock_service.create_student.return_value = new_student

        with patch.object(routes_module, "_get_service", return_value=mock_service):
            response = self.client.post(
                "/students",
                data=json.dumps({"name": "Charlie", "grade": 9.0}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Charlie")
        self.assertEqual(data["grade"], 9.0)

    def test_create_student_returns_400_when_name_is_blank(self):
        """createStudent_shouldReturn400WhenNameIsBlank"""
        response = self.client.post(
            "/students",
            data=json.dumps({"name": "", "grade": 8.5}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_student_returns_400_when_grade_exceeds_maximum(self):
        """createStudent_shouldReturn400WhenGradeExceedsMaximum"""
        response = self.client.post(
            "/students",
            data=json.dumps({"name": "Dave", "grade": 11.0}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_student_returns_400_when_grade_below_minimum(self):
        response = self.client.post(
            "/students",
            data=json.dumps({"name": "Eve", "grade": -1.0}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_student_returns_400_when_body_missing(self):
        response = self.client.post("/students", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------
    # GET /students/{id}/grade
    # ------------------------------------------------------------------

    def test_get_student_grade_returns_200_when_student_exists(self):
        """getStudentGrade_shouldReturn200WithGradeWhenStudentExists"""
        mock_service = MagicMock()
        mock_service.get_grade_by_id.return_value = 8.5

        with patch.object(routes_module, "_get_service", return_value=mock_service):
            response = self.client.get("/students/1/grade")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), 8.5)

    def test_get_student_grade_returns_404_when_student_not_found(self):
        """getStudentGrade_shouldReturn404WhenStudentNotFound"""
        mock_service = MagicMock()
        mock_service.get_grade_by_id.return_value = None

        with patch.object(routes_module, "_get_service", return_value=mock_service):
            response = self.client.get("/students/99/grade")

        self.assertEqual(response.status_code, 404)



if __name__ == "__main__":
    unittest.main()
