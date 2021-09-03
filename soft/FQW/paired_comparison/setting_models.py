from secrets import choice
from string import ascii_letters, digits


def create_url(length: int = 50) -> str:
    alphabet: str = ascii_letters + digits
    url: str = ''
    for i in range(length):
        symbol: str = choice(alphabet)
        url += symbol
    return url