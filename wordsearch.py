"""单词搜索谜题生成器 (wordsearch)。

把一批单词按 8 个方向塞进正方形网格，空位用随机字母填充。
小创意：支持自定义单词、固定种子复现、答案模式直接标出所有单词位置。
纯标准库，Python 3.10+。
"""

import argparse
import random
import sys

# 内置词表：约 200 个常见英文单词（全部小写字母）
WORDS = (
    "apple", "banana", "orange", "grape", "lemon", "melon", "peach", "berry",
    "mango", "kiwi", "cherry", "plum", "pear", "fig", "date", "olive",
    "cat", "dog", "bird", "fish", "horse", "sheep", "mouse", "tiger",
    "lion", "bear", "wolf", "frog", "snake", "eagle", "shark", "whale",
    "ant", "bee", "spider", "crab", "turtle", "rabbit", "deer", "fox",
    "house", "table", "chair", "door", "window", "floor", "roof", "wall",
    "bed", "lamp", "clock", "book", "pen", "paper", "phone", "key",
    "cup", "plate", "knife", "spoon", "bowl", "pan", "oven", "fridge",
    "red", "blue", "green", "yellow", "black", "white", "purple", "pink",
    "brown", "gray", "silver", "gold", "orange", "violet", "teal", "beige",
    "sun", "moon", "star", "cloud", "rain", "snow", "wind", "storm",
    "river", "lake", "ocean", "mountain", "forest", "desert", "island",
    "beach", "wave", "stone", "sand", "grass", "tree", "flower",
    "spring", "summer", "autumn", "winter", "morning", "night", "noon",
    "happy", "sad", "angry", "brave", "calm", "eager", "gentle", "kind",
    "quick", "slow", "strong", "weak", "bright", "dark", "loud", "quiet",
    "run", "jump", "swim", "fly", "walk", "climb", "dance", "sing",
    "read", "write", "draw", "cook", "play", "work", "sleep", "wake",
    "school", "teacher", "student", "class", "lesson", "exam", "grade",
    "music", "song", "piano", "drum", "guitar", "violin", "flute",
    "game", "ball", "team", "score", "win", "lose", "race", "goal",
    "city", "town", "street", "bridge", "park", "shop", "market", "road",
    "train", "plane", "ship", "car", "bike", "bus", "truck", "boat",
    "king", "queen", "prince", "knight", "castle", "sword", "shield",
    "dragon", "magic", "spell", "witch", "ghost", "pirate", "treasure",
)

# 8 个方向：(dr, dc)
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class PlacementError(Exception):
    """单词放不进网格时抛出。"""


def _fits(word, r, c, dr, dc, size, grid):
    """检查单词从 (r, c) 沿方向 (dr, dc) 是否能放入（允许交叉复用相同字母）。"""
    for i, ch in enumerate(word):
        nr, nc = r + dr * i, c + dc * i
        if not (0 <= nr < size and 0 <= nc < size):
            return False
        cur = grid[nr][nc]
        if cur is not None and cur != ch:
            return False
    return True


def _place(word, r, c, dr, dc, grid):
    """放入单词，返回占据的坐标列表。"""
    cells = []
    for i, ch in enumerate(word):
        nr, nc = r + dr * i, c + dc * i
        grid[nr][nc] = ch
        cells.append((nr, nc))
    return cells


def generate(words, size=10, seed=None, tries_per_word=500):
    """生成谜题。

    返回 (grid, placements)，grid 是 size×size 的字母矩阵，
    placements 是 {word: [(r, c), ...]} 的坐标映射。
    长词优先放置（网格空时长词最容易放，显著降低放不下的概率）。
    单词实在放不进时抛 PlacementError（调用方可缩小词表或调大网格）。
    """
    if size < 2:
        raise ValueError("网格边长至少为 2")
    rng = random.Random(seed)
    grid = [[None] * size for _ in range(size)]
    placements = {}
    # 长词优先：同样长度保持原顺序（稳定排序）
    ordered = sorted((w.lower() for w in words), key=len, reverse=True)
    for word in ordered:
        if len(word) > size:
            raise PlacementError(f"单词 {word!r} 比网格边长 {size} 还长，放不下")
        ok = False
        for _ in range(tries_per_word):
            dr, dc = rng.choice(DIRECTIONS)
            r = rng.randrange(size)
            c = rng.randrange(size)
            if _fits(word, r, c, dr, dc, size, grid):
                placements[word] = _place(word, r, c, dr, dc, grid)
                ok = True
                break
        if not ok:
            raise PlacementError(f"单词 {word!r} 尝试 {tries_per_word} 次仍放不下，试试更大的网格")
    # 空位填随机字母
    for r in range(size):
        for c in range(size):
            if grid[r][c] is None:
                grid[r][c] = rng.choice(ALPHABET)
    return grid, placements


def find_word(grid, word):
    """在网格里按 8 个方向找单词，返回坐标列表，找不到返回 None。"""
    size = len(grid)
    word = word.lower()
    for r in range(size):
        for c in range(size):
            for dr, dc in DIRECTIONS:
                cells = []
                for i, ch in enumerate(word):
                    nr, nc = r + dr * i, c + dc * i
                    if not (0 <= nr < size and 0 <= nc < size):
                        break
                    if grid[nr][nc] != ch:
                        break
                    cells.append((nr, nc))
                else:
                    return cells
    return None


def render(grid, placements=None, show_solution=False):
    """渲染网格。答案模式下单词字母大写标出。"""
    size = len(grid)
    sol_cells = set()
    if show_solution and placements:
        for cells in placements.values():
            sol_cells.update(cells)
    lines = []
    header = "    " + " ".join(f"{c:>2}" for c in range(size))
    lines.append(header)
    for r in range(size):
        row = [f"{r:>2} |"]
        for c in range(size):
            ch = grid[r][c]
            if (r, c) in sol_cells:
                row.append(f"[{ch.upper()}]")
            else:
                row.append(f" {ch} ")
        lines.append(" ".join(row))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="wordsearch",
        description="单词搜索谜题生成器：在字母网格里藏单词，找出来吧！",
    )
    ap.add_argument("--words", default=None,
                    help="自定义单词，逗号分隔，如 --words cat,dog,fish")
    ap.add_argument("--count", type=int, default=12,
                    help="从内置词表随机选几个单词（默认 12）")
    ap.add_argument("--size", type=int, default=10, help="网格边长（默认 10）")
    ap.add_argument("--seed", type=int, default=None, help="随机种子，方便复现")
    ap.add_argument("--solution", action="store_true", help="直接显示答案（单词字母大写标出）")
    args = ap.parse_args(argv)

    if args.words:
        words = [w.strip().lower() for w in args.words.split(",") if w.strip()]
        if not words:
            print("错误：--words 没有给出有效单词", file=sys.stderr)
            return 2
        bad = [w for w in words if not w.isalpha()]
        if bad:
            print(f"错误：单词只能是字母：{', '.join(bad)}", file=sys.stderr)
            return 2
    else:
        rng = random.Random(args.seed)
        words = rng.sample(list(WORDS), min(args.count, len(WORDS)))

    try:
        grid, placements = generate(words, size=args.size, seed=args.seed)
    except (PlacementError, ValueError) as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2

    print(f"单词搜索 {args.size}×{args.size}（{len(words)} 个单词，8 个方向）：\n")
    print(render(grid, placements, show_solution=args.solution))
    print("\n要找的单词：", ", ".join(sorted(words)))
    if args.solution:
        print("（答案已用 [大写] 标出）")
    else:
        print("加 --solution 直接看答案。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
