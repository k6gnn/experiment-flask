from flask import Blueprint, request, jsonify
from app.models.student import Student
from app.services.student_service import StudentService

student_bp = Blueprint("students", __name__, url_prefix="/students")

# Module-level service; tests can replace _service via patch or direct assignment
_service = StudentService()


def _get_service() -> StudentService:
    """Indirection point for test injection via unittest.mock.patch."""
    return _service


# GET /students — returns all students
@student_bp.route("", methods=["GET"])
def get_all_students():
    students = _get_service().get_all_students()
    return jsonify([s.to_dict() for s in students]), 200


# POST /students — creates a new student
@student_bp.route("", methods=["POST"])
def create_student():
    json_data = request.get_json(silent=True)
    if json_data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        student = Student.from_dict(json_data)
    except (ValueError, TypeError) as err:
        return jsonify({"errors": str(err)}), 400

    created = _get_service().create_student(student)
    return jsonify(created.to_dict()), 201


# GET /students/{id}/grade — returns the grade of a specific student
@student_bp.route("/<int:student_id>/grade", methods=["GET"])
def get_student_grade(student_id: int):
    grade = _get_service().get_grade_by_id(student_id)
    if grade is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(grade), 200
