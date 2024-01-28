from __future__ import annotations

import sys
from typing import (
    Any,
    AnyStr,
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
    def search(self: "PatternLike", string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike]:
        ...

    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]:
        ...

    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]:
        ...
