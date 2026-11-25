
from app.services.generator_service import generate_password


def test_password_length():
    password = generate_password(16)
    assert len(password) == 16


def test_password_contains_lowercase():
    password = generate_password(16)
    assert any(c.islower() for c in password)


def test_password_contains_uppercase():
    password = generate_password(16)
    assert any(c.isupper() for c in password)


def test_password_contains_digit():
    password = generate_password(16)
    assert any(c.isdigit() for c in password)


def test_password_contains_symbol():
    password = generate_password(16)
    assert any(not c.isalnum() for c in password)


def test_minimum_password_length():
    password = generate_password(4)
    assert len(password) == 4


def test_maximum_password_length():
    password = generate_password(128)
    assert len(password) == 128
