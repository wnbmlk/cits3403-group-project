import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from moviehub import create_app


@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client