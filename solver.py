import queue
from random import randint
from typing import Callable

from board import Board, CellType
from bricks import Blocks, Brick, Position, get_all_transforms, transform
from solver_display import display_status, running_bar

PositionSet = set[tuple[float, Position]]
Records = list[tuple[Position, transform]]

# * Global Variables
dead_count: int
blocks_suffix_sum: list[int]
pos_set: PositionSet
weight_map: dict[Position, float] = dict()
colormap: dict[int, str]
transform_maps: list[dict[Blocks, transform]]


def _weight(board: Board, pos: Position) -> float:
    # Corner first
    diff1 = abs(pos[0] - board.shape()[0] / 2)
    diff1 += diff1 * (diff1 % 2)
    diff1 *= randint(3, 7) / 10
    diff2 = abs(pos[1] - board.shape()[1] / 2)
    diff2 += diff2 * (diff2 % 2)
    diff2 *= randint(3, 7) / 10
    return diff1 + diff2


def weight(pos: Position) -> float:
    global weight_map
    return weight_map[pos]


# * Positions Verification
# ? Now built-in in Board
def in_range(board: Board, pos: Position) -> bool:
    N, M = board.shape()
    return pos[0] >= 0 and pos[0] < N and pos[1] >= 0 and pos[1] < M


def valid_pos(board: Board, pos: Position) -> bool:
    flag = (
        in_range(board, pos)
        and board[pos].type != CellType.NONE
        and not board[pos].taken
        and not board[pos].goal
    )
    return flag


DIRS = [Position(0, 1), Position(0, -1), Position(1, 0), Position(-1, 0)]


def dead_pos(board: Board, pos0: Position) -> bool:
    """Pos that can be set to dead."""
    return valid_pos(board, pos0) and all(
        not valid_pos(board, pos0 + dir) for dir in DIRS
    )


def is_dead(board: Board, pos: Position) -> bool:
    """Pos that are already dead"""
    return in_range(board, pos) and board[pos].taken and board[pos].brick_id == -1


def try_brick_at(board: Board, blocks: Blocks, pos0: Position) -> bool:
    return all(valid_pos(board, pos0 + block) for block in blocks)


# * Actions
def get_neighbors(pos0: Position) -> list[Position]:
    return [pos0 + dir for dir in DIRS]


def get_area(
    board: Board, pos0: Position, fn: Callable[[Position], bool]
) -> list[Position]:
    q = queue.Queue()
    q.put(pos0)
    area: list[Position] = []

    while not q.empty():
        pos = q.get()
        if not in_range(board, pos) or not fn(pos):
            continue

        if pos in area:
            continue
        area.append(pos)

        for n in get_neighbors(pos):
            q.put(n)
    return area


def get_area_to_kill(board: Board, pos0: Position) -> list[Position]:
    return get_area(board, pos0, lambda pos: valid_pos(board, pos))


def get_area_to_rescue(board: Board, pos0: Position) -> list[Position]:
    return get_area(board, pos0, lambda pos: is_dead(board, pos))


def remove_pos(board: Board, id: int, pos0: Position):
    cell = board[pos0]
    cell.taken = True
    cell.brick_id = id
    pos_set.remove((weight(pos0), pos0))


def add_pos(board: Board, id: int, pos0: Position):
    cell = board[pos0]
    assert cell.taken
    assert cell.brick_id == id

    cell.taken = False
    cell.brick_id = -1
    pos_set.add((weight(pos0), pos0))


def kill_area(board: Board, area: list[Position]):
    for pos in area:
        remove_pos(board, -1, pos)
    global dead_count
    dead_count += len(area)


def rescue_area(board: Board, area: list[Position]):
    for pos in area:
        add_pos(board, -1, pos)
    global dead_count
    dead_count -= len(area)


# def remove_pos(board: Board, id: int, pos0: Position, do_unit=True, spread=True):
#     if do_unit:
#         remove_pos_unit(board, id, pos0)

#     if spread:
#         for dir in DIRS:
#             neighbor = pos0 + dir
#             if dead_pos(board, neighbor):
#                 global dead_count
#                 dead_count += 1
#                 remove_pos(board, -1, neighbor)


def put_brick_at(
    board: Board,
    id: int,
    blocks: Blocks,
    pos0: Position,
    check_fn: Callable[[Board, list[Position]], bool],
):
    for block in blocks:
        pos = pos0 + block
        remove_pos(board, id, pos)

    # print(pos0)

    for block in blocks:
        for n in get_neighbors(pos0 + block):
            area = get_area_to_kill(board, n)
            if not check_fn(board, area):
                kill_area(board, area)


# def add_pos(board: Board, id: int, pos0: Position, pos_set: PositionSet, do_unit=True, spread=True):

#     if do_unit:
#         add_pos_unit(board, id, pos0, pos_set)

#     if spread:
#         for dir in DIRS:
#             neighbor = pos0 + dir
#             if in_range(board, neighbor) and board[neighbor].taken and board[neighbor].brick_id == -1:
#                 global dead_count
#                 dead_count -= 1
#                 add_pos(board, -1, neighbor, pos_set)


def lift_brick_at(
    board: Board,
    id: int,
    blocks: Blocks,
    pos0: Position,
    check_fn: Callable[[Board, list[Position]], bool],
):
    for block in blocks:
        pos = pos0 + block
        add_pos(board, id, pos)

    for block in blocks:
        for n in get_neighbors(pos0 + block):
            area = get_area_to_rescue(board, n)
            if not check_fn(board, area):
                rescue_area(board, area)


def get_check_fn(bricks: list[Brick]) -> Callable[[Board, list[Position]], bool]:
    def check_fn(board: Board, area: list[Position]) -> bool:
        if not bricks:
            # board.display(colormap)
            return True

        if len(area) < min(len(b.blocks) for b in bricks):
            return False

        for brick in bricks:
            for blocks in transform_maps[brick.id]:
                for pos in area:
                    if try_brick_at(board, blocks, pos):
                        return True
        return False

    return check_fn


# * Solving Functions
def init(board: Board, _colormap: dict[int, str], bricks: list[Brick]):
    global dead_count
    dead_count = 0

    global weight_map
    for i, j, _ in board:
        pos = Position(i, j)
        weight_map[pos] = _weight(board, pos)
    weight_map[Position(0, 0)] = 100
    weight_map[Position(6, 0)] = 100
    weight_map[Position(0, 5)] = 100
    weight_map[Position(2, 6)] = 100
    weight_map[Position(7, 6)] = 100
    weight_map[Position(7, 4)] = 100

    global pos_set
    pos_set = set(
        (weight(Position(i, j)), Position(i, j))
        for i, j, cell in board
        if not cell.taken and cell.type != CellType.NONE
    )

    global colormap
    colormap = _colormap

    global blocks_suffix_sum
    blocks_suffix_sum = [len(b.blocks) for b in bricks]
    for i in range(len(blocks_suffix_sum) - 1, 0, -1):
        blocks_suffix_sum[i - 1] += blocks_suffix_sum[i]

    global transform_maps
    transform_maps = [get_all_transforms(b.blocks) for b in bricks]


count = 0


def solve_recur(
    board: Board,
    bricks: list[Brick],
    cur: int,
    records: Records,
) -> bool:
    # ? Branch Cutting
    if cur == len(bricks):
        return True
    if dead_count > 0:
        return False

    brick = bricks[cur]
    transforms = transform_maps[cur]
    left_count = len(bricks) - cur

    global count
    if count % 1000 == 1:
        print(f"Round {count}")
    # running_bar(left_count)
    count += 1

    for blocks in transforms:
        for _, pos0 in pos_set:
            display_status(board, pos0, blocks, left_count, colormap)
            # print(dead_count)

            if not try_brick_at(board, blocks, pos0):
                continue

            check_fn = get_check_fn(bricks[cur + 1 :])

            put_brick_at(board, brick.id, blocks, pos0, check_fn)
            if solve_recur(board, bricks, cur + 1, records):
                records[cur] = pos0, transforms[blocks]
                return True
            lift_brick_at(board, brick.id, blocks, pos0, check_fn)
    return False


def solve(
    _board: Board, bricks: list[Brick], _colormap: dict[int, str]
) -> tuple[Board, Records]:
    """
    Return a sequence of positions (x, y), each corresponding to a brick.
    """

    board = _board
    records: Records = [(Position(-1, -1), transform.U) for _ in range(len(bricks))]

    init(board, _colormap, bricks)

    print(blocks_suffix_sum)

    if solve_recur(board, bricks, 0, records):
        assert not any(pos[0] == -1 or pos[1] == -1 for pos, _ in records)
        return board, records

    return _board, []
