import pytest
from app import create_app

TEST_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}


@pytest.fixture
def app():
    application = create_app(TEST_CONFIG)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()
