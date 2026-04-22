import curses
from typing import Literal, Self
from types import TracebackType

from .curses_menu import Tui
from .types import STYLE, Chars


Position = Literal['center', 'top', 'bottom']


class ProgressBar:
	"""Framed progress bar drawn over the active Tui.

	Usage:
		with ProgressBar(total=100) as bar:
			for i in range(100):
				do_work()
				bar.update(i + 1, label='Step name')
	"""

	def __init__(
		self,
		total: int = 100,
		width: int | Literal['full'] = 60,
		position: Position = 'center',
	):
		self._total = max(1, total)
		self._width_req: int | Literal['full'] = width
		self._position: Position = position
		self._current = 0
		self._label: str | None = None
		self._win: curses.window | None = None

	def __enter__(self) -> Self:
		max_y, max_x = Tui.t().max_yx
		h = 3
		w = max_x if self._width_req == 'full' else min(self._width_req, max_x)
		w = max(20, w)

		match self._position:
			case 'top':
				y = 0
			case 'bottom':
				y = max_y - h
			case _:
				y = (max_y - h) // 2
		x = (max_x - w) // 2

		self._win = curses.newwin(h, w, y, x)
		self._win.bkgd(' ', curses.color_pair(STYLE.NORMAL.value))
		self._draw()
		return self

	def __exit__(
		self,
		exc_type: type[BaseException] | None,
		exc: BaseException | None,
		tb: TracebackType | None,
	) -> None:
		self._win = None
		Tui.t().screen.touchwin()
		Tui.t().screen.refresh()

	def update(self, current: int, label: str | None = None) -> None:
		self._current = max(0, min(current, self._total))
		if label is not None:
			self._label = label
		self._draw()

	def step(self, n: int = 1, label: str | None = None) -> None:
		self.update(self._current + n, label=label)

	def _draw(self) -> None:
		win = self._win
		if win is None:
			return
		win.erase()
		h, w = win.getmaxyx()

		# border
		win.addstr(0, 0, Chars.Upper_left + Chars.Horizontal * (w - 2) + Chars.Upper_right)
		win.addstr(1, 0, Chars.Vertical + ' ' * (w - 2) + Chars.Vertical)
		# last-row write: addstr on bottom-right cell raises; use insstr
		bottom = Chars.Lower_left + Chars.Horizontal * (w - 2) + Chars.Lower_right
		win.insstr(2, 0, bottom)

		inner = w - 4
		pct = self._current / self._total

		# title slot: custom label if given, else live numbers
		numeric = f'{int(pct * 100):3d}% {self._current}/{self._total}'
		title = f' {self._label} ({numeric}) ' if self._label else f' {numeric} '
		win.addstr(0, 2, title[: w - 4])

		# fill: accent-colored blocks
		filled = int(inner * pct)
		accent = curses.color_pair(STYLE.CURSOR_STYLE.value)
		win.addstr(1, 2, Chars.Block * filled, accent)
		win.addstr(1, 2 + filled, ' ' * (inner - filled))

		win.refresh()
