from enum import Enum
from typing import Self, override

from ._i18n import tr


class PasswordStrength(Enum):
	WEAK = 'weak'
	MODERATE = 'moderate'
	STRONG = 'strong'

	@property
	@override
	def value(self) -> str:  # pylint: disable=invalid-overridden-method
		match self:
			case PasswordStrength.WEAK:
				return tr('weak')
			case PasswordStrength.MODERATE:
				return tr('moderate')
			case PasswordStrength.STRONG:
				return tr('strong')

	@classmethod
	def strength(cls, password: str) -> Self:
		digit = any(c.isdigit() for c in password)
		upper = any(c.isupper() for c in password)
		lower = any(c.islower() for c in password)
		symbol = any(not c.isalnum() for c in password)
		return cls._check(digit, upper, lower, symbol, len(password))

	@classmethod
	def _check(cls, digit: bool, upper: bool, lower: bool, symbol: bool, length: int) -> Self:
		# https://github.com/archlinux/archinstall/issues/1304#issuecomment-1146768163
		if digit and upper and lower and symbol:
			match length:
				case num if num >= 13:
					return cls.STRONG
				case num if 11 <= num <= 12:
					return cls.MODERATE
				case num if 7 <= num <= 10:
					return cls.WEAK
		elif digit and upper and lower:
			match length:
				case num if num >= 14:
					return cls.STRONG
				case num if 11 <= num <= 13:
					return cls.MODERATE
				case num if 7 <= num <= 10:
					return cls.WEAK
		elif upper and lower:
			match length:
				case num if num >= 15:
					return cls.STRONG
				case num if 12 <= num <= 14:
					return cls.MODERATE
				case num if 7 <= num <= 11:
					return cls.WEAK
		elif lower or upper:
			match length:
				case num if num >= 18:
					return cls.STRONG
				case num if 14 <= num <= 17:
					return cls.MODERATE
				case num if 9 <= num <= 13:
					return cls.WEAK

		return cls.WEAK


class Password:
	"""Plain password holder. Encryption is caller's concern
	(attach .enc_password yourself via your crypt routine)."""

	def __init__(self, plaintext: str = '', enc_password: str | None = None):
		if not plaintext and not enc_password:
			raise ValueError('Either plaintext or enc_password must be provided')
		self._plaintext = plaintext
		self.enc_password = enc_password

	@property
	def plaintext(self) -> str:
		return self._plaintext

	@override
	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Password):
			return NotImplemented
		if self.enc_password and other.enc_password:
			return self.enc_password == other.enc_password
		return self._plaintext == other._plaintext

	def hidden(self) -> str:
		if self._plaintext:
			return '*' * len(self._plaintext)
		return '*' * 8
