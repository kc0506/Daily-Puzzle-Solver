from io import StringIO
import re
import sys
import time

from board import Board
from bricks import Blocks, Position
from output_utils import clear

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
BASE = 35
SHIFT = 3
COUNT = 10
DURATION = 0.007

DELTA = 0.05
N_DOTS = 10


def running_bar(count: int):
    clear()
    s = "." * N_DOTS + f"   {count} left"

    print(s, end="")
    sys.stdout.flush()

    for i in range(N_DOTS):
        _s = s
        for j in range(i - 2, i + 1):
            if j >= 0:
                _s = _s[:j] + "˙" + _s[j + 1 :]
        print("\r" + _s, end="")
        sys.stdout.flush()
        time.sleep(DELTA)


def concat_output(board_output: list[str], blocks_output: list[str], count: int):
    for i, ln2 in enumerate(blocks_output):
        ln1 = board_output[SHIFT + i]
        board_output[SHIFT + i] = (
            ln1
            + " " * (BASE - len(ANSI_ESCAPE.sub("", ln1)))
            + (" " if "⬇️" in ln1 else "")
            + ln2
        )

    count_ln = board_output[COUNT]
    board_output[COUNT] = (
        count_ln
        + " " * (BASE - len(ANSI_ESCAPE.sub("", count_ln)))
        + (" " if "⬇️" in count_ln else "")
        + f"{count} left"
    )
    return board_output


def display_status(
    board: Board, pos: Position, blocks: Blocks, count: int, colormap: dict[int, str]
):
    clear()

    board_buf = StringIO()
    sys.stdout = board_buf
    board.display(colormap, cursor=pos)
    board_output = board_buf.getvalue()
    if board_output.startswith("\r\n"):
        board_output = [""] + board_output.split("\n")
    else:
        board_output = board_output.split("\n")

    blocks_buf = StringIO()
    sys.stdout = blocks_buf
    blocks.display()
    blocks_output = blocks_buf.getvalue().split("\n")

    sys.stdout = sys.__stdout__

    for ln in concat_output(board_output, blocks_output, count):
        print(ln)
    time.sleep(DURATION)
