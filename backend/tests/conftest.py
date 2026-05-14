from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import *  # noqa: F403
from app.ml.price_model import MODEL_PATH


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_test_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = get_test_session

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def clean_trained_model_file():
    if MODEL_PATH.exists():
        MODEL_PATH.unlink()

    yield

    if MODEL_PATH.exists():
        MODEL_PATH.unlink()