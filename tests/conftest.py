from pathlib import Path
import pytest
import website
from website import master_key as mk
from website import views

@pytest.fixture
def app():
    website.db_path = Path.cwd() / "tests" / "tmp_pwmngr.db"
    views.db_path = website.db_path
    mk.salt_path = website.db_path.parent / "tmp_pwmngr.salt"
    app = website.create_app({
        "TESTING": True,
    })

    yield app
    Path.unlink(website.db_path, missing_ok=True)
    Path.unlink(mk.salt_path, missing_ok=True)
    # todo: use tempfile

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli__runner()
