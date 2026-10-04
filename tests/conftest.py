# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient

from oj.web.app import create_app


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    return tmp_path_factory.mktemp("ojdb") / "test.db"


@pytest.fixture(scope="session")
def client(db_path):
    app = create_app(db_path)
    with TestClient(app) as c:
        yield c
