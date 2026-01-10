# myre - Human Readable Regular Expression

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version: 0.0.7](https://img.shields.io/badge/version-0.0.7-orange.svg)](https://github.com/blurhead/myre)

**myre** is a composable regular expression library that transforms regex patterns into first-class objects supporting algebraic operations. It provides a human-friendly way to combine, filter, and transform pattern matching in Python, maintaining full compatibility with the standard `re` module interface.

## Features

- **Algebraic Operations**: Combine patterns using `|` (OR), `&` (AND), `^` (XOR/EXCLUDE), `@` (MASK)
- **Type-Safe**: Protocol-based design with full type hints
- **re-Compatible**: Drop-in replacement for standard `re` module patterns
- **Composable**: Patterns are immutable objects that can be combined like mathematical sets
- **Zero Dependencies**: Only requires `typing-extensions` for modern type hints

## Installation

```bash
pip install myre
```

## Quick Start

```python
import myre

# OR operation: match any pattern (default)
pattern = myre.compile(r"hello", r"world", r"foo")
for match in pattern.finditer("hello world foo"):
    print(match.group())  # Prints: hello, world, foo

# AND operation: all patterns must match
from myre import Mode
pattern = myre.compile(r"hello", r"world", mode=Mode.ALL)
for match in pattern.finditer("hello world"):
    print(match.group())  # Prints: hello world

# SEQUENCE operation: match patterns in order
pattern = myre.compile(r"hello") + myre.compile(r"world")
for match in pattern.finditer("hello world"):
    print(match.group())  # Prints: hello world

# XOR operation: match pattern but exclude another
pattern = myre.compile(r"h\wllo") ^ r"ell"
for match in pattern.finditer("Hello Hallo Hillo"):
    print(match.group())  # Prints: Hallo, Hillo (excludes "Hello")

# MASK operation: ignore specific patterns by masking with placeholders
pattern = myre.compile(r"test_{3}value") @ (r"\d+", "_")
for match in pattern.finditer("test123value"):
    print(match.group())  # Prints: test123value
```

## Core Concepts

### Pattern Types

#### MatchAny (Mode.ANY - default)
Matches any of the given patterns, avoiding overlapping matches:

```python
from myre import Mode

pattern = myre.compile(r"abc", r"bcd", r"cde", mode=Mode.ANY)
# or simply: pattern = myre.compile(r"abc", r"bcd", r"cde")
for match in pattern.finditer("abc bcd cde"):
    print(match.group())  # Non-overlapping matches
```

#### MatchALL (Mode.ALL)
Requires **all** patterns to match somewhere in the search range. Returns a combined match:

```python
pattern = myre.compile(r"hello", r"world", mode=Mode.ALL)
for match in pattern.finditer("hello world"):
    print(match.group())  # "hello world"
```

**Note**: MatchALL collects the first match from each pattern and combines them into a single match result.

### Operators

| Operator | Name | Description | Example |
|----------|------|-------------|---------|
| `\|` | OR | Match any pattern | `p1 \| p2` → MatchAny(p1, p2) |
| `&` | AND | Match all patterns | `p1 & p2` → MatchALL(p1, p2) |
| `+` | SEQUENCE | Match patterns in order | `p1 + p2` → MatchSeq(p1, p2) |
| `^` | XOR | Exclude matches containing deny pattern | `p1 ^ p2` → Match p1, exclude if text contains p2 |
| `@` | MASK | Mask patterns with placeholders | `p1 @ (mask, placeholder)` → Replace mask with placeholder, match p1 |

### Operator Usage Notes

**`^` (XOR)**: Currently operates at the **string level** - if the entire search string contains the deny pattern, all matches are rejected. This is different from traditional set XOR.

**`@` (MASK)**: Replaces matched text with placeholder characters (preserving length), then matches the pattern. Returns the **original text** (not masked text). Choose a placeholder that works with your pattern:
- Use `'x'` if pattern uses `x+` or `x{N}` to match placeholders
- Use `'_'` if pattern uses `_{3}` etc.
- Default is `'.'` (dot character)

## API Reference

### PatternLike Protocol

All pattern objects implement the `PatternLike` protocol:

```python
class PatternLike(Protocol):
    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike]: ...
    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]: ...
    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]: ...
```

**TODO: Standard library methods not yet implemented:**
- `match()` - Match at the beginning of the string
- `fullmatch()` - Match the entire string
- `split()` - Split string by pattern occurrences
- `sub()` / `subn()` - Replace pattern matches
- `flags` - Access pattern flags
- `pattern` - Access pattern string
- `groupindex` - Access group name mapping

### MatchLike Protocol

All match objects implement the `MatchLike` protocol:

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

**TODO: Standard library methods not yet implemented:**
- `groupdict()` - Return dict of named groups
- `expand()` - Expand template using groups
- `lastindex` - Last matched group index
- `lastgroup` - Last matched group name
- `pos` / `endpos` - Search boundaries

### Pattern Classes

#### Base
```python
@dataclass
class Base:
    p_trim: PatternLike  # Pre-process filter
    p_deny: PatternLike  # Post-process filter

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

## Advanced Usage

### Working with re.Pattern

```python
import re
import myre

# Mix regex strings and compiled patterns
regex1 = re.compile(r"hello")
pattern = myre.compile(regex1, r"world", flag=re.IGNORECASE)
```

### Nested Operations

```python
# Complex pattern: (hello OR world) BUT NOT (foo OR bar)
base = myre.compile(r"hello", r"world")
exclude = myre.compile(r"foo", r"bar")
pattern = base ^ exclude
```

### Position-Aware Matching

```python
# Mask punctuation before matching
pattern = myre.compile(r"\bhello\b") @ (r"[.,!?;:]", " ")
for match in pattern.finditer("Hello, world! Hello."):
    print(match.group())  # Prints both "Hello," and "Hello."
```

## Architecture

The library is built on three architectural layers:

1. **Protocol Layer** (`protocol.py`): Defines structural types for pattern/match compatibility
2. **Pattern Layer** (`pattern.py`): Implements algebraic operations using Template Method pattern
3. **Match Layer** (`match.py`): Provides position-aware match result wrappers

### Key Design Patterns

- **Template Method**: `Base.finditer()` orchestrates the matching pipeline
- **Protocol-based Polymorphism**: Structural subtyping over nominal inheritance
- **Immutable Operators**: All operations create new objects via `deepcopy`

## Development

```bash
# Install dependencies
poetry install

# Run tests
pytest tests/

# Type checking
mypy myre/

# Linting and formatting
ruff check .
ruff format .
```

## Contributing

Contributions are welcome! Please ensure:
- All tests pass: `pytest tests/`
- Type checking passes: `mypy myre/`
- Code is formatted: `ruff format .`

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by the need for composable, human-readable regular expressions in Python.
