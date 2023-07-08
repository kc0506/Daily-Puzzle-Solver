from enum import Enum
import json
from typing import Callable


vector2 = tuple[int, int]


class Position:
    pos: vector2

    def __init__(self, x: int, y: int) -> None:
        self.pos = x, y

    def __eq__(self, __value: "Position") -> bool:
        return self.pos[0] == __value.pos[0] and self.pos[1] == __value.pos[1]

    def __lt__(self, __value: "Position") -> bool:
        if self.pos[0] == __value.pos[0]:
            return self.pos[1] < __value.pos[1]
        return self.pos[0] < __value.pos[0]

    def __add__(self, __value: "Position") -> "Position":
        return Position(self.pos[0] + __value.pos[0], self.pos[1] + __value.pos[1])

    def __getitem__(self, key) -> int:
        return self.pos[key]

    def __str__(self):
        return str(self.pos)

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self.pos)


class Blocks:
    blocks: list[Position]

    def __init__(self, blocks: list[vector2 | Position]) -> None:
        self.blocks = [Position(*pos) for pos in blocks]

    def __len__(self) -> int:
        return len(self.blocks)

    def __iter__(self):
        for b in sorted(self.blocks):
            yield b

    def __eq__(self, __value: "Blocks") -> bool:
        return all(pos == _pos for pos, _pos in zip(self, __value))

    def __str__(self) -> str:
        return str(sorted(self.blocks))

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(str(self))

    def display(self):
        X = "██"

        # ? Group by x-index
        _blocks = sorted(self, key=lambda b: b[0])
        block_groups: list[list[Position]] = [[]]
        cur = block_groups[0]
        for i, b in enumerate(_blocks):
            if len(cur) == 0:
                cur.append(b)
            else:
                if b[0] == cur[0][0]:
                    cur.append(b)
                else:
                    cur = [b]
                    block_groups.append(cur)

        # ? Sort each group by y-index
        block_groups = [sorted(g, key=lambda b: b[1]) for g in block_groups]

        # ? Print the shape line by line
        st = min(g[0][1] for g in block_groups)
        end = max(g[-1][1] for g in block_groups)

        for g in block_groups:
            cur = 0
            for i in range(st, end + 1):
                if cur >= len(g) or i < g[cur][1]:
                    print(" " * len(X), end="")
                else:
                    print(X, end="")
                    cur += 1
            print()


class transform(Enum):
    U = 0
    R = 1
    D = 2
    L = 3
    MU = 4
    MR = 5
    MD = 6
    ML = 7


def mirror(pos: Position) -> Position:
    return Position(-pos[0], pos[1])


transform_func: dict[transform, Callable[[Position], Position]] = {}
transform_func[transform.U] = lambda pos: pos
transform_func[transform.R] = lambda pos: Position(pos[1], -pos[0])
transform_func[transform.D] = lambda pos: Position(-pos[0], -pos[1])
transform_func[transform.L] = lambda pos: Position(-pos[1], pos[0])
transform_func[transform.MU] = lambda pos: transform_func[transform.U](mirror(pos))
transform_func[transform.MR] = lambda pos: transform_func[transform.R](mirror(pos))
transform_func[transform.MD] = lambda pos: transform_func[transform.D](mirror(pos))
transform_func[transform.ML] = lambda pos: transform_func[transform.L](mirror(pos))


def get_transform(blocks: Blocks, t: transform) -> Blocks:
    return Blocks([transform_func[t](pos) for pos in blocks])


def get_all_transforms(blocks: Blocks) -> dict[Blocks, transform]:
    return {get_transform(blocks, t): t for t in transform}


class Brick:
    blocks: Blocks
    id: int

    def __init__(self, _blocks: list[vector2 | Position]) -> None:
        self.blocks = Blocks(_blocks)


def build_bricks(json_path="bricks.json") -> list[Brick]:
    with open(json_path, "r") as f:
        _bricks = json.load(f)

    bricks = list(map(lambda arr: Brick(arr), _bricks))
    for i, b in enumerate(bricks):
        b.id = i

    return bricks
