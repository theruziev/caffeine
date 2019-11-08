import os

import pytest


@pytest.fixture
def static_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return f"{test_dir}/_static"


def pytest_configure(config):
    config.addinivalue_line("markers", "db: Database tests")
