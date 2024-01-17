import re
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)


@runtime_checkable
class MatchLike(Protocol):
    def group(self, index: int = 0) -> str:
        ...

    def groups(self) -> Tuple[Optional[str], ...]:
        ...

    def start(self, group: int = 0) -> int:
        ...

    def end(self, group: int = 0) -> int:
        ...

    def span(self, group: int = 0) -> Tuple[int, int]:
        ...


@runtime_checkable
class PatternLike(Protocol):
    def search(self: "PatternLike", string: str, pos: int, endpos: int) -> Optional[MatchLike]:
        ...

    def match(self, string: str, pos: int, endpos: int) -> Optional[MatchLike]:
        ...

    def fullmatch(self, string: str, pos: int, endpos: int) -> Optional[MatchLike]:
        ...

    def findall(self, string: str, pos: int, endpos: int) -> List[str]:
        ...

    def finditer(self, string: str, pos: int, endpos: int) -> Iterator[MatchLike]:
        ...

    def sub(self, repl: Any, string: str, count: int) -> str:
        ...

    def subn(self, repl: Any, string: str, count: int) -> Tuple[str, int]:
        ...

    def split(self, string: str, maxsplit: int) -> List[str]:
        ...

    def flags(self) -> re.RegexFlag:
        ...

    def groupindex(self) -> Dict[str, int]:
        ...

    def pattern(self) -> str:
        ...
