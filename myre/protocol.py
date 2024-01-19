from __future__ import annotations

import re
from typing import (
    Any,
    AnyStr,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Pattern,
    Protocol,
    Tuple,
    TypeVar,
    overload,
    runtime_checkable,
)

_T = TypeVar("_T")


@runtime_checkable
class MatchLike(Protocol[AnyStr]):
    def start(self, group: int = 0) -> int:
        ...

    def end(self, group: int = 0) -> int:
        ...

    def span(self, group: int = 0) -> Tuple[int, int]:
        ...

    @property
    def re(self) -> Pattern[AnyStr]:
        ...

    @overload
    def group(self, __group: Literal[0] = 0) -> AnyStr:
        ...

    @overload
    def group(self, __group: str | int) -> AnyStr | Any:
        ...

    def group(self, __group: str | int = 0) -> AnyStr | Any:
        ...

    @overload
    def groups(self) -> tuple[AnyStr | Any, ...]:
        ...

    @overload
    def groups(self, default: _T) -> tuple[AnyStr | _T, ...]:
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
