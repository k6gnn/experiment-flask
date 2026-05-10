from typing import List, Optional
from app.models.student import Student


class StudentRepository:
    """
    Data access layer — mirrors Spring Data JpaRepository[Student, Long].
    Uses sqlite3 via Flask's g-stored connection.
    """

    def __init__(self, db_conn=None):
        """
        db_conn: an open sqlite3.Connection.
        If None, the production path fetches it from Flask g via get_db().
        Tests pass in an explicit connection to avoid Flask context requirements.
        """
        self._conn = db_conn

    def _db(self):
        if self._conn is not None:
            return self._conn
        from app import get_db
        return get_db()

    def find_all(self) -> List[Student]:
        cursor = self._db().execute("SELECT id, name, grade FROM students")
        return [Student.from_row(row) for row in cursor.fetchall()]

    def find_by_id(self, student_id: int) -> Optional[Student]:
        cursor = self._db().execute(
            "SELECT id, name, grade FROM students WHERE id = ?", (student_id,)
        )
        row = cursor.fetchone()
        return Student.from_row(row) if row else None

    def save(self, student: Student) -> Student:
        db = self._db()
        cursor = db.execute(
            "INSERT INTO students (name, grade) VALUES (?, ?)",
            (student.name, student.grade),
        )
        db.commit()
        student.id = cursor.lastrowid
        return student

    def delete(self, student: Student) -> None:
        db = self._db()
        db.execute("DELETE FROM students WHERE id = ?", (student.id,))
        db.commit()
