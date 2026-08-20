from src.user_service import UserService


def test_create_user():
    service = UserService()

    user = service.create_user(
        1,
        "John Doe",
        "john@example.com",
    )

    assert user["id"] == 1
    assert user["name"] == "John Doe"
    assert user["email"] == "john@example.com"


def test_get_user():
    service = UserService()

    service.create_user(
        1,
        "John Doe",
        "john@example.com",
    )

    user = service.get_user(1)

    assert user["name"] == "John Doe"


def test_delete_user():
    service = UserService()

    service.create_user(
        1,
        "John Doe",
        "john@example.com",
    )

    assert service.delete_user(1) is True
    assert service.get_user(1) is None