import datetime
import sys
from typing import Optional
from board import build_board, mark_date
from bricks import Brick, build_bricks, get_transform
from solver import Records, solve
from output_utils import PALLATES, RESET_COLOR


def display_records(
    bricks: list[Brick], records: Records, colormap: Optional[dict[int, str]] = None
):
    for brick, (pos, t) in zip(bricks, records):
        blocks = get_transform(brick.blocks, t)
        if colormap:
            print(colormap[brick.id])
        blocks.display()
        if colormap:
            print(RESET_COLOR)
        print(pos)
        print()


def main():
    month: int
    day: int
    weekday: int

    if len(sys.argv) == 1:
        today = datetime.date.today()
        month = today.month
        day = today.day
        weekday = (today.weekday() + 1) % 7
    else:
        raise NotImplementedError

    board = build_board()
    board = mark_date(board, month, day, weekday)
    bricks = build_bricks()

    for b in bricks:
        b.blocks.display()
        print()

    colormap: dict[int, str] = {
        b.id: c for b, c in zip(bricks, PALLATES[: len(bricks)])
    }
    colormap[-1] = RESET_COLOR

    board, records = solve(board, bricks, colormap)
    board.display(colormap)
    print(records)
    # display_records(bricks, records, colormap)


if __name__ == "__main__":
    main()
