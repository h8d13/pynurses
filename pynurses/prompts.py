from pathlib import Path

from ._i18n import tr
from .password import Password, PasswordStrength

from .curses_menu import EditMenu
from .result import ResultType
from .types import STYLE, Alignment, ViewportEntry


_STRENGTH_STYLE = {
	PasswordStrength.WEAK: STYLE.ERROR,
	PasswordStrength.MODERATE: STYLE.WARNING,
	PasswordStrength.STRONG: STYLE.HELP,
}


def _confirm_header_entries(
	header: str | None,
	password: Password,
	strength: PasswordStrength,
) -> list[ViewportEntry]:
	rows: list[tuple[str, STYLE]] = []
	if header:
		for line in header.rstrip('\n').split('\n'):
			rows.append((line, STYLE.NORMAL))
	rows.append((f'{tr("Password")}: {password.hidden()}', STYLE.NORMAL))
	rows.append((
		f'{tr("Password strength")}: {strength.value}',
		_STRENGTH_STYLE[strength],
	))
	rows.append(('', STYLE.NORMAL))
	return [ViewportEntry(text, i, 0, style) for i, (text, style) in enumerate(rows)]


def get_password(
	text: str,
	header: str | None = None,
	allow_skip: bool = False,
	preset: str | None = None,
	skip_confirmation: bool = False,
) -> Password | None:
	failure: str | None = None

	while True:
		user_hdr = None
		if failure is not None:
			user_hdr = f'{header}\n{failure}\n'
		elif header is not None:
			user_hdr = header

		result = EditMenu(
			text,
			header=user_hdr,
			alignment=Alignment.CENTER,
			allow_skip=allow_skip,
			default_text=preset,
			hide_input=True,
		).input()

		if allow_skip and (not result.has_item() or not result.text()):
			return None

		password = Password(plaintext=result.text())
		strength = PasswordStrength.strength(result.text())

		if skip_confirmation:
			return password

		result = EditMenu(
			tr('Confirm password'),
			header_entries=_confirm_header_entries(header, password, strength),
			alignment=Alignment.CENTER,
			allow_skip=False,
			hide_input=True,
		).input()

		if password._plaintext == result.text():
			return password

		failure = tr('The confirmation password did not match, please try again')


def prompt_dir(
	text: str,
	header: str | None = None,
	validate: bool = True,
	must_exist: bool = True,
	allow_skip: bool = False,
	preset: str | None = None,
) -> Path | None:
	def validate_path(path: str | None) -> str | None:
		if path:
			dest_path = Path(path)

			if must_exist:
				if dest_path.exists() and dest_path.is_dir():
					return None
			else:
				return None

		return tr('Not a valid directory')

	validate_func = validate_path if validate else None

	result = EditMenu(
		text,
		header=header,
		alignment=Alignment.CENTER,
		allow_skip=allow_skip,
		validator=validate_func,
		default_text=preset,
	).input()

	match result.type_:
		case ResultType.Skip:
			return None
		case ResultType.Selection:
			if not result.text():
				return None
			return Path(result.text())

	return None
