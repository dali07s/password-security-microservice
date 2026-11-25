
from app.services.passphrase_service import (
    generate_passphrase,
    WORDLIST
)


def test_passphrase_word_count():
    passphrase = generate_passphrase(5)

    words = passphrase.split("-")

    assert len(words) == 5


def test_passphrase_words_belong_to_wordlist():
    passphrase = generate_passphrase(5)

    words = passphrase.split("-")

    for word in words:
        assert word in WORDLIST


def test_minimum_word_count():
    passphrase = generate_passphrase(4)

    assert len(passphrase.split("-")) == 4


def test_maximum_word_count():
    passphrase = generate_passphrase(10)

    assert len(passphrase.split("-")) == 10
