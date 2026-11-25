
import hashlib
from types import SimpleNamespace

from app.services.breach_service import check_password_breach


def test_breached_password_found(monkeypatch):
    password = "MyTestPassword123!"

    full_hash = hashlib.sha1(
        password.encode("utf-8")
    ).hexdigest().upper()

    suffix = full_hash[5:]

    def fake_get(url, headers, timeout):
        return SimpleNamespace(
            text=f"{suffix}:25",
            raise_for_status=lambda: None
        )

    monkeypatch.setattr(
        "app.services.breach_service.requests.get",
        fake_get
    )

    result = check_password_breach(password)

    assert result["is_breached"] is True
    assert result["times_seen"] == 25


def test_password_not_found(monkeypatch):
    def fake_get(url, headers, timeout):
        return SimpleNamespace(
            text="",
            raise_for_status=lambda: None
        )

    monkeypatch.setattr(
        "app.services.breach_service.requests.get",
        fake_get
    )

    result = check_password_breach("MyNewPassword123!")

    assert result["is_breached"] is False
    assert result["times_seen"] == 0
