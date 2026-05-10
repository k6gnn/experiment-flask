import sqlite3
import os
from flask import Flask, g


def _open_db(app):
    """Open a fresh SQLite connection for the given app config."""
    uri = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    conn = sqlite3.connect(uri, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """Return the per-request SQLite connection stored in Flask's g."""
    from flask import current_app
    if "db" not in g:
        g.db = _open_db(current_app._get_current_object())
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create tables if they do not already exist."""
    with app.app_context():
        conn = _open_db(app)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT    NOT NULL,
                grade REAL    NOT NULL
            )
        """)
        conn.commit()
        conn.close()


def create_app(config_object=None):
    app = Flask(__name__)

    # Default configuration (mirrors application.properties / Spring defaults)
    app.config["APP_NAME"] = "grade-management"
    app.config["SERVER_PORT"] = 5000
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False

    if config_object:
        if isinstance(config_object, dict):
            app.config.update(config_object)
        else:
            app.config.from_object(config_object)

    app.teardown_appcontext(close_db)
    init_db(app)

    from app.routes.student_routes import student_bp
    app.register_blueprint(student_bp)

    return app
