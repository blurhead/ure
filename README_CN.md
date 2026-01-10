# myre - 人类可读的正则表达式

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version: 0.0.7](https://img.shields.io/badge/version-0.0.7-orange.svg)](https://github.com/blurhead/myre)

**myre** 是一个可组合的正则表达式库，将正则模式转化为支持代数运算的一等对象。它提供了一种人类友好的方式来组合、过滤和转换Python中的模式匹配，同时保持与标准 `re` 模块接口的完全兼容性。

## 特性

- **代数运算**: 使用 `|` (或)、`&` (且)、`^` (异或/排除)、`@` (遮蔽) 组合模式
- **类型安全**: 基于Protocol的设计，完整的类型提示
- **兼容 re**: 可作为标准 `re` 模模式的替代品
- **可组合**: 模式是不可变对象，可以像数学集合一样组合
- **零依赖**: 仅需要 `typing-extensions` 用于现代类型提示

## 安装

```bash
pip install myre
```

## 快速开始

```python
import myre

# 或运算：匹配任意模式（默认）
pattern = myre.compile(r"hello", r"world", r"foo")
for match in pattern.finditer("hello world foo"):
    print(match.group())  # 输出: hello, world, foo

# 且运算：所有模式都必须匹配
from myre import Mode
pattern = myre.compile(r"hello", r"world", mode=Mode.ALL)
for match in pattern.finditer("hello world"):
    print(match.group())  # 输出: hello world

# 序列运算：按顺序匹配模式
pattern = myre.compile(r"hello") + myre.compile(r"world")
for match in pattern.finditer("hello world"):
    print(match.group())  # 输出: hello world

# 异或运算：匹配模式但排除另一个
pattern = myre.compile(r"h\wllo") ^ r"ell"
for match in pattern.finditer("Hello Hallo Hillo"):
    print(match.group())  # 输出: Hallo, Hillo (排除 "Hello")

# 遮蔽运算：用占位符忽略特定模式
pattern = myre.compile(r"test_{3}value") @ (r"\d+", "_")
for match in pattern.finditer("test123value"):
    print(match.group())  # 输出: test123value
```

## 核心概念

### 模式类型

#### MatchAny (Mode.ANY - 默认)
匹配任意给定模式，避免重叠匹配：

```python
from myre import Mode

pattern = myre.compile(r"abc", r"bcd", r"cde", mode=Mode.ANY)
# 或者简写为: pattern = myre.compile(r"abc", r"bcd", r"cde")
for match in pattern.finditer("abc bcd cde"):
    print(match.group())  # 非重叠匹配
```

#### MatchALL (Mode.ALL)
要求**所有**模式在搜索范围内都找到匹配。返回一个组合的匹配结果：

```python
pattern = myre.compile(r"hello", r"world", mode=Mode.ALL)
for match in pattern.finditer("hello world"):
    print(match.group())  # "hello world"
```

**注意**: MatchALL 从每个模式中收集第一个匹配，并将它们组合成单个匹配结果。

### 运算符

| 运算符 | 名称 | 描述 | 示例 |
|--------|------|------|------|
| `\|` | 或 | 匹配任意模式 | `p1 \| p2` → MatchAny(p1, p2) |
| `&` | 且 | 匹配所有模式 | `p1 & p2` → MatchALL(p1, p2) |
| `+` | 序列 | 按顺序匹配模式 | `p1 + p2` → MatchSeq(p1, p2) |
| `^` | 异或 | 匹配模式但排除包含拒绝模式的内容 | `p1 ^ p2` → 匹配 p1，排除包含 p2 的结果 |
| `@` | 遮蔽 | 用占位符遮蔽模式 | `p1 @ (mask, placeholder)` → 用占位符替换 mask，匹配 p1 |

### 运算符使用说明

**`^` (异或)**: 当前在**字符串级别**操作 - 如果整个搜索字符串包含拒绝模式，则拒绝所有匹配。这与传统的集合异或不同。

**`@` (遮蔽)**: 用占位符替换匹配的文本（保持长度），然后匹配模式。返回**原始文本**（非遮蔽文本）。选择与你的模式匹配的占位符：
- 如果模式使用 `x+` 或 `x{N}`，使用 `'x'`
- 如果模式使用 `_{3}` 等，使用 `'_'`
- 默认是 `'.'` （点字符）

## API 参考

### PatternLike 协议

所有模式对象都实现 `PatternLike` 协议：

```python
class PatternLike(Protocol):
    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike]: ...
    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]: ...
    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]: ...
```

**TODO: 尚未实现的标准库方法:**
- `match()` - 在字符串开头匹配
- `fullmatch()` - 匹配整个字符串
- `split()` - 按模式出现分割字符串
- `sub()` / `subn()` - 替换模式匹配
- `flags` - 访问模式标志
- `pattern` - 访问模式字符串
- `groupindex` - 访问分组名映射

### MatchLike 协议

所有匹配对象都实现 `MatchLike` 协议：

```python
class MatchLike(Protocol):
    re: PatternLike
    string: str

    def start(self, group: int | str = 0) -> int: ...
    def end(self, group: int | str = 0) -> int: ...
    def span(self, group: int | str = 0) -> Tuple[int, int]: ...
    def group(self, group: int | str = 0) -> str: ...
    def groups(self) -> tuple[str, ...]: ...
```

**TODO: 尚未实现的标准库方法:**
- `groupdict()` - 返回命名分组的字典
- `expand()` - 使用分组展开模板
- `lastindex` - 最后匹配的分组索引
- `lastgroup` - 最后匹配的分组名
- `pos` / `endpos` - 搜索边界

### 模式类

#### Base
```python
@dataclass
class Base:
    p_trim: PatternLike  # 预处理过滤器
    p_deny: PatternLike  # 后处理过滤器

    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]
    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]
    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike]
```

#### MatchAny
```python
@dataclass
class MatchAny(Base):
    patterns: tuple[PatternLike, ...]

    @classmethod
    def compile(cls, *patterns: Any, flag: int = 0) -> Self
```

#### MatchALL
```python
@dataclass
class MatchALL(MatchAny):
    patterns: tuple[PatternLike, ...]

    @classmethod
    def compile(cls, *patterns: Any, flag: int = 0) -> Self
```

## 高级用法

### 使用 re.Pattern

```python
import re
import myre

# 混合正则字符串和编译后的模式
regex1 = re.compile(r"hello")
pattern = myre.compile(regex1, r"world", flag=re.IGNORECASE)
```

### 嵌套运算

```python
# 复杂模式: (hello 或 world) 但不包含 (foo 或 bar)
base = myre.compile(r"hello", r"world")
exclude = myre.compile(r"foo", r"bar")
pattern = base ^ exclude
```

### 位置感知匹配

```python
# 在匹配前遮蔽标点符号
pattern = myre.compile(r"\bhello\b") @ (r"[.,!?;:]", " ")
for match in pattern.finditer("Hello, world! Hello."):
    print(match.group())  # 输出两个 "Hello," 和 "Hello."
```

## 架构

该库建立在三个架构层之上：

1. **协议层** (`protocol.py`): 定义模式/匹配兼容性的结构化类型
2. **模式层** (`pattern.py`): 使用模板方法模式实现代数运算
3. **匹配层** (`match.py`): 提供位置感知的匹配结果包装器

### 关键设计模式

- **模板方法**: `Base.finditer()` 编排匹配管道
- **基于协议的多态**: 结构化子类型而非名义继承
- **不可变运算符**: 所有操作通过 `deepcopy` 创建新对象

## 开发

```bash
# 安装依赖
poetry install

# 运行测试
pytest tests/

# 类型检查
mypy myre/

# 代码检查和格式化
ruff check .
ruff format .
```

## 贡献

欢迎贡献！请确保：
- 所有测试通过: `pytest tests/`
- 类型检查通过: `mypy myre/`
- 代码已格式化: `ruff format .`

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 致谢

受 Python 中可组合、人类可读的正则表达式需求启发。
