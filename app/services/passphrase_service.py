import secrets
from pathlib import Path


# Locate the word list
WORDLIST_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "eff_large_wordlist.txt"
)


def load_wordlist():

    words = []

    with open(WORDLIST_PATH, "r", encoding="utf-8") as file:

        for line in file:

            parts = line.strip().split()

            if len(parts) == 2:
                words.append(parts[1])

    if len(words) != 7776:
        raise RuntimeError("Invalid Diceware word list")

    return words


WORDLIST = load_wordlist()


def generate_passphrase(number_of_words: int):

    selected_words = []

    for _ in range(number_of_words):

        word = secrets.choice(WORDLIST)

        selected_words.append(word)

    return "-".join(selected_words)