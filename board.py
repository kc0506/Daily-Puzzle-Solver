from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generator, Iterable, Optional, overload

from colorama import Fore
from bricks import vector2, Position


class CellType(Enum):
    MONTH = "month"
    DAY = "day"
    WEEKDAY = "weekday"
    NONE = "none"


VALUE_RANGES: dict[CellType, Iterable] = {
    CellType.MONTH: range(1, 13),
    CellType.DAY: range(1, 32),
    CellType.WEEKDAY: range(1, 8),
    CellType.NONE: [-1],
}

SHAPE = (8, 7)


@dataclass
class Cell:
    _x: int
    _y: int
    type: CellType
    _value: int

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def value(self):
        return self._value

    taken: bool = field(init=False, default=False)
    goal: bool = field(init=False, default=False)
    brick_id: int = field(init=False, default=-1)
    is_nil: bool = field(default=False)

    def __bool__(self) -> bool:
        return not self.is_nil


MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dev",
]
WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thr", "Fri", "Sat"]


def cell2str(cell: Cell) -> str:
    value = cell.value
    if cell.type == CellType.MONTH:
        return MONTHS[value - 1]
    if cell.type == CellType.DAY:
        return f"{value:>3}"
    if cell.type == CellType.WEEKDAY:
        return WEEKDAYS[value % 7]
    if cell.type == CellType.NONE:
        return " " * 3
    raise Exception


class Board:
    _board: list[list[Cell]] = []
    _nil = Cell(-1, -1, CellType.NONE, -1, is_nil=True)

    def __len__(self) -> int:
        return len(self._board)

    def shape(self) -> tuple[int, int]:
        return len(self._board), len(self._board[0]) if self._board else 0

    def __iter__(self) -> Generator[tuple[int, int, Cell], Any, Any]:
        for i, row in enumerate(self._board):
            for j, c in enumerate(row):
                yield i, j, c

    def rows(self):
        return self._board

    @overload
    def __getitem__(self, key: int) -> list[Cell]:
        ...

    @overload
    def __getitem__(self, key: vector2 | Position) -> Cell:
        ...

    def __getitem__(self, key: int | vector2 | Position):
        if isinstance(key, int):
            return self._board[key]
        if type(key) is vector2 or isinstance(key, Position):
            N = len(self._board)
            M = len(self._board[0])
            if key[0] < 0 or key[0] >= N or key[1] < 0 or key[1] >= M:
                return self._nil
            return self._board[key[0]][key[1]]

    def append(self, row: list[Cell]):
        self._board.append(row)

    def display(
        self,
        colormap: Optional[dict[int, str]] = None,
        cursor: Optional[Position] = None,
    ):
        RESET = -1
        for i, row in enumerate(self.rows()):
            if cursor and cursor[0] == i:
                print(" " * 4 * cursor[1] + " ⬇️")
            else:
                print()
            for c in row:
                s = cell2str(c)
                if colormap:
                    if c.taken and c.brick_id == -1:
                        s = Fore.BLACK + s + colormap[RESET]
                    else:
                        s = colormap[c.brick_id] + s + colormap[RESET]
                print(s, end=" ")
            print()


def build_board() -> Board:
    board = Board()

    # * Months
    board.append(
        [Cell(-1, -1, CellType.MONTH, m) for m in range(1, 7)]
        + [Cell(-1, -1, CellType.NONE, 0)]
    )
    board.append(
        [Cell(-1, -1, CellType.MONTH, m) for m in range(7, 13)]
        + [Cell(-1, -1, CellType.NONE, 0)]
    )

    # * Days & Weekdays
    for i in range(1, 5):
        board.append(
            [Cell(-1, -1, CellType.DAY, day + 1) for day in range(7 * (i - 1), 7 * i)]
        )
    board.append(
        [Cell(-1, -1, CellType.DAY, day) for day in range(29, 32)]
        + [Cell(-1, -1, CellType.WEEKDAY, w) for w in range(4)]
    )
    board.append(
        [Cell(-1, -1, CellType.NONE, -1) for _ in range(4)]
        + [Cell(-1, -1, CellType.WEEKDAY, w) for w in range(4, 7)]
    )

    # * Check shapes
    assert len(board) == SHAPE[0]
    assert all(len(row) == SHAPE[1] for row in board.rows())

    # * Set proper indices
    for i, j, cell in board:
        cell._x = i
        cell._y = j

    return board


class NoSuchCellError(Exception):
    pass


def _search(board: Board, f: Callable[[Cell], bool]) -> Cell:
    for _, _, cell in board:
        if f(cell):
            return cell
    raise NoSuchCellError


def _search_month(board: Board, month: int):
    assert month in VALUE_RANGES[CellType.MONTH]
    return _search(
        board, lambda cell: cell.type == CellType.MONTH and cell.value == month
    )


def _search_day(board: Board, day: int):
    assert day in VALUE_RANGES[CellType.DAY]
    return _search(board, lambda cell: cell.type == CellType.DAY and cell.value == day)


def _search_weekday(board: Board, weekday: int):
    assert weekday in VALUE_RANGES[CellType.WEEKDAY]
    return _search(
        board, lambda cell: cell.type == CellType.WEEKDAY and cell.value == weekday
    )


def search(board: Board, month: int, day: int, weekday: int) -> tuple[Cell, Cell, Cell]:
    return (
        _search_month(board, month),
        _search_day(board, day),
        _search_weekday(board, weekday),
    )


def mark_date(_board: Board, month: int, day: int, weekday: int) -> Board:
    board = _board
    m, d, w = search(board, month, day, weekday)
    m.goal = True
    d.goal = True
    w.goal = True
    return board
