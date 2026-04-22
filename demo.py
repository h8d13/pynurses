#!/usr/bin/env python3
"""Consolidated demo: main menu on left, live preview on right.

Run: python demo.py
"""
import time
from typing import Any

from pynurses import *
# consult __init__.py for module declaration
# for simplicity we'll import all of them

STATE: dict[str, Any] = {
	'fruit': None,
	'toppings': [],
	'password': None,
	'workdir': None,
	'notes': '',
	'hostname': None,
	'proceed': None,
	'mode': 'dark',
	'accent': 'blue',
}

def _preview(item: MenuItem) -> str | None:
	key = item.key
	if key == 'fruit':
		v = STATE['fruit']
		return f'Single-select demo.\n\nPicked: {v or "(none)"}'
	if key == 'toppings':
		v = STATE['toppings']
		body = '\n'.join(f'  - {t}' for t in v) if v else '  (none)'
		return f'Multi-select demo.\nSpace/Tab to toggle, Enter to confirm.\n\nChecked:\n{body}'
	if key == 'password':
		pw = STATE['password']
		if pw is None:
			return 'Password prompt with confirmation + strength meter.\n\nNot set.'
		strength = PasswordStrength.strength(pw.plaintext).value
		return f'Stored: {pw.hidden()}\nStrength: {strength}'
	if key == 'workdir':
		v = STATE['workdir']
		return f'Directory prompt with validation.\n\nPath: {v or "(unset)"}'
	if key == 'notes':
		v = STATE['notes']
		if not v:
			return 'Multi-line content editor.\n\n(empty)'
		lines = v.split('\n')
		head = '\n'.join(lines[:10])
		more = f'\n... ({len(lines) - 10} more lines)' if len(lines) > 10 else ''
		return f'Multi-line content editor.\n\n{head}{more}'
	if key == 'hostname':
		v = STATE['hostname']
		return f'EditMenu with validator.\n\nHostname: {v or "(unset)"}'
	if key == 'proceed':
		v = STATE['proceed']
		return f'Horizontal Yes/No menu (Orientation.HORIZONTAL).\n\nAnswer: {v!r}'
	if key == 'loading':
		return 'ProgressBar demo. Runs a fake 2s task with a block-fill bar.'
	if key == 'settings':
		return (
			'Nested submenu demo. Live curses theme.\n\n'
			f'Mode: {STATE["mode"]}\n'
			f'Accent: {STATE["accent"]}'
		)
	if key == 'quit':
		return 'Exit the demo.\n\nCtrl+C on any menu clears its selection.'
	return None

def _pick_fruit() -> None:
	group = MenuItemGroup([
		MenuItem('Apples', value='apples'),
		MenuItem('Oranges', value='oranges'),
		MenuItem('Pears', value='pears'),
	])
	res = SelectMenu(
		group,
		header='Pick a fruit',
		allow_skip=True,
		allow_reset=True,
		reset_warning_msg='Clear fruit selection?',
	).run()
	if res.type_ == ResultType.Reset:
		STATE['fruit'] = None
	elif res.has_item():
		STATE['fruit'] = res.get_value()

def _pick_toppings() -> None:
	group = MenuItemGroup([
		MenuItem('Sugar', value='sugar'),
		MenuItem('Cinnamon', value='cinnamon'),
		MenuItem('Honey', value='honey'),
		MenuItem('Lemon', value='lemon'),
	])
	res = SelectMenu(
		group,
		header='Toppings (Space/Tab)',
		multi=True,
		allow_skip=True,
		allow_reset=True,
		reset_warning_msg='Clear all toppings?',
	).run()
	if res.type_ == ResultType.Reset:
		STATE['toppings'] = []
	elif res.has_item():
		STATE['toppings'] = res.get_values()


def _set_password() -> None:
	pw = get_password('Password', header='Set a password\n', allow_skip=True)
	if pw is not None:
		STATE['password'] = pw


def _set_workdir() -> None:
	path = prompt_dir('Working directory', allow_skip=True, must_exist=True)
	if path is not None:
		STATE['workdir'] = path


def _edit_notes() -> None:
	# direct ContentEditor construction (edit_content is a one-liner wrapper around this)
	text = ContentEditor(title='Notes', preset=STATE['notes']).edit()
	if text is not None:
		STATE['notes'] = text


def _set_hostname() -> None:
	def _valid(s: str | None) -> str | None:
		if not s:
			return 'hostname must not be empty'
		if any(c.isspace() for c in s):
			return 'no whitespace allowed'
		return None

	res: Result = EditMenu(
		'Hostname',
		validator=_valid,
		allow_skip=True,
		default_text=STATE['hostname'] or '',
	).input()
	if res.type_ == ResultType.Selection and res.text():
		STATE['hostname'] = res.text()


def _fake_load() -> None:
	# centered, fixed width, numeric
	with ProgressBar(total=40, width=60) as bar:
		for _ in range(40):
			time.sleep(0.03)
			bar.step()

	# bottom, full width, numeric
	with ProgressBar(total=30, width='full', position='bottom') as bar:
		for _ in range(30):
			time.sleep(0.03)
			bar.step()


def _ask_proceed() -> None:
	group = MenuItemGroup([MenuItem.yes(), MenuItem.no()])
	frame = FrameProperties('Confirm', FrameStyle.MIN, FrameStyle.MAX)
	res = SelectMenu(
		group,
		header='Proceed?',
		orientation=Orientation.HORIZONTAL,
		frame=frame,
		alignment=Alignment.CENTER,
		allow_skip=True,
	).run()
	if res.has_item():
		STATE['proceed'] = res.get_value()


def _apply_theme() -> None:
	Tui.set_mode(STATE['mode'])
	Tui.set_accent(STATE['accent'])
	Tui.t()._set_up_colors()


def _pick_mode() -> None:
	group = MenuItemGroup([
		MenuItem('Dark', value='dark'),
		MenuItem('Light', value='light'),
	])
	res = SelectMenu(group, header='Mode', allow_skip=True).run()
	if res.has_item():
		STATE['mode'] = res.get_value()
		_apply_theme()

def _pick_accent() -> None:
	group = MenuItemGroup([
		MenuItem('Blue', value='blue'),
		MenuItem('Cyan', value='cyan'),
		MenuItem('Green', value='green'),
		MenuItem('Magenta', value='magenta'),
		MenuItem('Orange', value='orange'),
		MenuItem('Red', value='red'),
	])
	res = SelectMenu(group, header='Accent color', allow_skip=True).run()
	if res.has_item():
		STATE['accent'] = res.get_value()
		_apply_theme()

_SETTINGS_GROUP = MenuItemGroup([
	MenuItem('Mode', value=_pick_mode, key='mode'),
	MenuItem('Accent color', value=_pick_accent, key='accent'),
	MenuItem.separator(),
	MenuItem('Back', value=None, key='back'),
])


def _open_settings() -> None:
	while True:
		res = SelectMenu(
			_SETTINGS_GROUP,
			header='Settings (submenu)',
			allow_skip=True,
		).run()
		if not res.has_item():
			return
		chosen = res.item().value
		if chosen is None:
			return
		chosen()

def main() -> None:
	items = [
		MenuItem.separator(),
		MenuItem('Pick fruit (single-select)', value=_pick_fruit, key='fruit', preview_action=_preview),
		MenuItem('Pick toppings (multi-select)', value=_pick_toppings, key='toppings', preview_action=_preview),
		MenuItem('Set password', value=_set_password, key='password', preview_action=_preview),
		MenuItem('Set working dir', value=_set_workdir, key='workdir', preview_action=_preview),
		MenuItem('Edit notes', value=_edit_notes, key='notes', preview_action=_preview),
		MenuItem('Set hostname (EditMenu)', value=_set_hostname, key='hostname', preview_action=_preview),
		MenuItem('Proceed? (horizontal)', value=_ask_proceed, key='proceed', preview_action=_preview),
		MenuItem('Fake loading bar', value=_fake_load, key='loading', preview_action=_preview),
		MenuItem.separator(),
		MenuItem('Settings...', value=_open_settings, key='settings', preview_action=_preview),
		MenuItem.separator(),
		MenuItem('Quit', value=None, key='quit', preview_action=_preview),
	]
	group = MenuItemGroup(items)

	with Tui():
		while True:
			res = SelectMenu(
				group,
				preview_style=PreviewStyle.RIGHT,
				preview_size='auto',
				preview_frame=FrameProperties.max('Info'),
				alignment=Alignment.LEFT,
				allow_skip=True,
			).run()

			if not res.has_item():
				break
			chosen = res.item().value
			if chosen is None:
				break
			chosen()

	print('final state:')
	for k, v in STATE.items():
		if k == 'password' and v is not None:
			v = v.hidden()
		print(f'  {k}: {v}')


if __name__ == '__main__':
	main()
