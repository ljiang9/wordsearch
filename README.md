# wordsearch · 单词搜索谜题生成器

在字母网格里按 8 个方向藏单词，然后把它们找出来。内置约 200 个常见英文单词，
也支持自定义单词、固定种子复现、一键看答案。纯标准库，Python 3.10+。

## 玩法

```bash
python -m wordsearch                  # 10×10，随机 12 个单词
python -m wordsearch --size 12        # 12×12 大网格
python -m wordsearch --words cat,dog,fish  # 自定义单词
python -m wordsearch --count 20       # 从内置词表选 20 个
python -m wordsearch --seed 42        # 固定种子，方便复现同一张谜题
python -m wordsearch --solution       # 直接显示答案（单词字母大写标出）
```

示例输出（`--words cat,dog --size 8 --seed 7 --solution`，真实运行结果）：

```
单词搜索 8×8（2 个单词，8 个方向）：

     0  1  2  3  4  5  6  7
 0 |  b   c   n  [D]  n   c   h   c
 1 |  r   n  [O]  b   s   d   h   u
 2 |  u  [G]  s   b   s   s  [C]  m
 3 |  b   h   b   r   e  [A]  j   n
 4 |  e   r   d   s  [T]  j   r   v
 5 |  f   d   s   s   u   g   l   d
 6 |  r   w   c   s   b   t   g   p
 7 |  v   r   n   y   k   o   s   o

要找的单词： cat, dog
（答案已用 [大写] 标出）
```

## 小创意

- **8 方向全覆盖**：横、竖、斜线，正读倒读都能藏，比只横竖的版本难找得多。
- **交叉复用字母**：两个单词可以在相同字母处交叉，谜题更紧凑。
- **种子复现**：同一 `--seed` 永远生成同一张谜题，适合出题给朋友做。
- **答案自检**：`find_word()` 是独立的暴力搜索实现，`--solution` 的标注位置
  都经过它二次确认，生成器自己不会"藏了却找不到"。

## 已知局限（诚实版）

- 单词比网格边长还长时直接报错放不下；单词太多、网格太小也可能放不下
  （此时会明确报错，建议调大 `--size` 或减少单词数）。
- 内置词表约 200 个常见词，不是完整词典；自定义单词只能是纯字母。
- 目前只有"生成+看答案"，没有交互式圈词玩法。
- 填充字母是纯随机的，偶尔会"意外"拼出别的单词——这是这类谜题的通病。

## 验证记录

- `py_compile`：两个模块均通过。
- 20 个种子 × 默认配置：所有放入的单词都能用 8 方向暴力搜索找回，无丢失。
- 自定义单词（`--words cat,dog,fish`）、`--size 12`、`--solution` 均实测正常。
- 边界：单词长于边长时抛 `PlacementError` 并给出中文提示；`--size 1` 被拒绝。
