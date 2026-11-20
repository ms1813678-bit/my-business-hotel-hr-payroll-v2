import pytest
from pydantic import ValidationError
from app.config import Settings

SECRET = "test-session-secret-with-more-than-32-characters"


def build(**overrides):
    values = {"database_url": "postgresql+psycopg://test_user:test_password@localhost:5432/test_db", "session_secret": SECRET}
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.mark.parametrize("url", ["", "postgresql+psycopg://hr:CHANGE_ME@localhost/db", "sqlite:///./test.db"])
def test_database_url_rejects_placeholder_empty_or_non_postgres(url):
    with pytest.raises(ValidationError):
        build(database_url=url)


def test_database_url_accepts_explicit_postgres():
    assert build().database_url.startswith("postgresql+psycopg://")


@pytest.mark.parametrize("secret", ["", "short", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"])
def test_session_secret_rejects_missing_short_or_placeholder(secret):
    with pytest.raises(ValidationError):
        build(session_secret=secret)

@pytest.mark.parametrize(
    "host",
    ["192.168.1.20", "10.0.0.5", "db.hotel.local", "example.com"],
)
def test_database_url_rejects_remote_postgres_hosts(host):
    with pytest.raises(ValidationError, match="on this computer only"):
        build(database_url=f"postgresql+psycopg://test_user:test_password@{host}:5432/test_db")


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "[::1]"])
def test_database_url_accepts_loopback_postgres_hosts(host):
    assert build(
        database_url=f"postgresql+psycopg://test_user:test_password@{host}:5432/test_db"
    ).database_url.startswith("postgresql+psycopg://")
