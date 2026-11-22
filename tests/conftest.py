import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Use a throwaway database and fixed secrets for every test run (set before the app is imported).
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp, 'test.db').as_posix()}"
os.environ["JWT_SECRET"] = "x" * 40
os.environ["ADMIN_PASSCODE"] = "test-admin-passcode"
os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-used")  # tests never call the model
os.environ["APP_ENV"] = "development"

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clear_rate_limits():
    from api import guards

    guards._hits.clear()
    yield


def customer_token(client, email="aarav.mehta@example.com", password="paperleaf123"):
    r = client.post("/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def admin_token(client):
    r = client.post("/admin/login", json={"passcode": "test-admin-passcode"})
    assert r.status_code == 200, r.text
    return r.json()["token"]
