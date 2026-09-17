from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.api import routes
from app.main import app
from app.service.user_service import UserService


class FakeAuthService:
    async def verify_access_token(self, token):
        assert token == "valid-token"
        return {"username": "user-123"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(routes, "auth_service", FakeAuthService())
    return TestClient(app)


def test_get_me_uses_username_from_token_and_filters_attributes(client, monkeypatch):
    user_service = Mock()
    user_service.get_user.return_value = {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "user",
    }
    monkeypatch.setattr(routes, "user_service", user_service)

    response = client.get(
        "/api/v1/me",
        headers={"Authorization": "Bearer valid-token"},
        params={"username": "attacker"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "user",
    }
    user_service.get_user.assert_called_once_with("user-123")


def test_patch_me_passes_only_allowed_fields(client, monkeypatch):
    user_service = Mock()
    user_service.update_user.return_value = {
        "email": "new@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "user",
    }
    monkeypatch.setattr(routes, "user_service", user_service)

    response = client.patch(
        "/api/v1/me",
        headers={"Authorization": "Bearer valid-token"},
        json={"email": "new@example.com", "first_name": "Jane"},
    )

    assert response.status_code == 200
    user_service.update_user.assert_called_once()
    assert user_service.update_user.call_args.args[0] == "user-123"
    assert user_service.update_user.call_args.args[1].model_dump(
        exclude_unset=True
    ) == {
        "email": "new@example.com",
        "first_name": "Jane",
    }


def test_patch_me_rejects_forbidden_fields(client):
    response = client.patch(
        "/api/v1/me",
        headers={"Authorization": "Bearer valid-token"},
        json={"role": "admin"},
    )

    assert response.status_code == 422


def test_user_service_returns_404_for_missing_user():
    service = UserService()
    service.repo = Mock()
    service.repo.get_user.return_value = None

    with pytest.raises(HTTPException) as error:
        service.get_user("missing-user")

    assert error.value.status_code == 404


def test_user_service_rejects_empty_update():
    service = UserService()

    with pytest.raises(HTTPException) as error:
        service.update_user("user-123", service_profile_update())

    assert error.value.status_code == 422


def service_profile_update():
    from app.domain.models import UserProfileUpdate

    return UserProfileUpdate()
