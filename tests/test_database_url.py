import pytest

from app.config import database_url_required, resolve_database_url


def test_unset_url_uses_the_sqlite_file():
    assert resolve_database_url("", "career_platform.db", require_url=False) == "sqlite:///career_platform.db"


@pytest.mark.parametrize("raw", ["postgres://u:p@h:5432/db", "postgresql://u:p@h:5432/db"])
def test_railway_style_urls_use_psycopg3(raw):
    assert resolve_database_url(raw, "x.db", require_url=False) == "postgresql+psycopg://u:p@h:5432/db"


def test_explicit_driver_is_left_alone():
    url = "postgresql+psycopg://u:p@h:5432/db"
    assert resolve_database_url(url, "x.db", require_url=False) == url


def test_explicit_sqlite_url_is_left_alone():
    assert resolve_database_url("sqlite:////tmp/t.db", "x.db", require_url=False) == "sqlite:////tmp/t.db"


def test_missing_url_when_required_is_an_error():
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        resolve_database_url("", "career_platform.db", require_url=True)


@pytest.mark.parametrize("environ, expected", [
    ({}, False),
    ({"APP_ENV": "development"}, False),
    ({"APP_ENV": "production"}, True),
    ({"RAILWAY_ENVIRONMENT_NAME": "production"}, True),
])
def test_database_url_required(environ, expected):
    assert database_url_required(environ) is expected


def test_rds_url_keeps_its_tls_options():
    raw = "postgresql://u:p@h:5432/db?sslmode=verify-full&sslrootcert=/x.pem"
    assert resolve_database_url(raw, "x.db", require_url=True) == (
        "postgresql+psycopg://u:p@h:5432/db?sslmode=verify-full&sslrootcert=/x.pem"
    )


def test_conftest_rejects_remote_test_database():
    # Import by the name pytest already registered ("conftest"); importing it as
    # tests.conftest would re-run its env setup mid-session and repoint the suite.
    from conftest import _test_database_url

    with pytest.raises(RuntimeError, match="local"):
        _test_database_url({"TEST_DATABASE_URL": "postgresql://u:p@db.railway.app:5432/railway"}, "/tmp/x.db")
    assert _test_database_url({}, "/tmp/x.db") == "sqlite:////tmp/x.db"
    local = "postgresql://localhost/career_platform_test"
    assert _test_database_url({"TEST_DATABASE_URL": local}, "/tmp/x.db") == local
