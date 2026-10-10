# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient

from oj import config
from oj.web.app import create_app


@pytest.fixture(autouse=True)
def _warmup_off_by_default():
    """业务测试默认关闭预热运行，避免每次 judge_code 都多跑一次；
    预热相关测试通过显式传 warmup=True 覆盖。"""
    prev = config.WARMUP_ENABLED
    config.WARMUP_ENABLED = False
    yield
    config.WARMUP_ENABLED = prev


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    return tmp_path_factory.mktemp("ojdb") / "test.db"


@pytest.fixture(scope="session")
def client(db_path):
    app = create_app(db_path)
    with TestClient(app) as c:
        yield c
