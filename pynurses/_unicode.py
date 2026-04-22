import unicodedata
from functools import lru_cache


@lru_cache(maxsize=128)
def _is_wide_character(char: str) -> bool:
	return unicodedata.east_asian_width(char) in 'FW'


def _count_wchars(string: str) -> int:
	return sum(_is_wide_character(c) for c in string)


def unicode_ljust(string: str, width: int, fillbyte: str = ' ') -> str:
	return string.ljust(width - _count_wchars(string), fillbyte)


def unicode_rjust(string: str, width: int, fillbyte: str = ' ') -> str:
	return string.rjust(width - _count_wchars(string), fillbyte)
