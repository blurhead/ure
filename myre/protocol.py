from __future__ import annotations

import sys
from typing import (
    AnyStr,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    overload,
    runtime_checkable,
)

_T = TypeVar("_T")


@runtime_checkable
class MatchLike(Protocol[AnyStr]):
    re: PatternLike[AnyStr]
    string: AnyStr

    def start(self, group: int | str = 0) -> int: ...

    def end(self, group: int | str = 0) -> int: ...

    def span(self, group: int | str = 0) -> Tuple[int, int]: ...

    @overload
    def group(self, __group: Literal[0] = 0) -> AnyStr: ...
    @overload
    def group(self, __group: str | int) -> AnyStr: ...

    def groups(self) -> tuple[AnyStr, ...]: ...


@runtime_checkable
class PatternLike(Protocol[AnyStr]):
    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike[AnyStr]]: ...

    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[AnyStr]: ...

    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike[AnyStr]]: ...
