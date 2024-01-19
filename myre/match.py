from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, AnyStr, Generic, Literal, Pattern, Tuple, TypeVar, overload

from myre.protocol import MatchLike

_T = TypeVar("_T")


@dataclass
class OffsetMatch(Generic[AnyStr]):
    _match: re.Match[AnyStr]
    _start_offset: int
    _end_offset: int

    def start(self, group: int = 0) -> int:
        return self._match.start(group) + self._start_offset

    def end(self, group: int = 0) -> int:
        return self._match.end(group) + self._end_offset

    def span(self, group: int = 0) -> Tuple[int, int]:
        return (self.start(group), self.end(group))

    @property
    def re(self) -> Pattern[AnyStr]:
        return self._match.re

    @overload
    def group(self, __group: Literal[0] = 0) -> AnyStr:
        ...

    @overload
    def group(self, __group: str | int) -> AnyStr | Any:
        ...

    def group(self, __group: str | int = 0) -> AnyStr | Any:
        return self._match.group(__group)

    @overload
    def groups(self) -> tuple[AnyStr | Any, ...]:
        ...

    @overload
    def groups(self, default: _T) -> tuple[AnyStr | _T, ...]:
        ...

    def groups(self, default=None):
        return self._match.groups(default)

    def groupdict(self, default=None):
        return self._match.groupdict(default)

    def expand(self, template):
        return self._match.expand(template)

    def __repr__(self):
        return f"OffsetMatch(start={self.start()}, end={self.end()}, match={self._match})"

    def __eq__(self, other: Any):
        if isinstance(other, (MatchLike, re.Match)):
            return self.span() == other.span()
        return False

    # def pos(self):
    #     return self._match.pos

    # def endpos(self):
    #     return self._match.endpos

    # def lastindex(self):
    #     return self._match.lastindex

    # def lastgroup(self):
    #     return self._match.lastgroup

    # def regs(self):
    #     return tuple((start + self._start_offset, end + self._end_offset) for start, end in self._match.regs)

    # def re(self):
    #     return self._match.re

    # def string(self):
    #     return self._match.string

    # def __copy__(self):
    #     return OffsetMatch(self._match, self._start_offset, self._end_offset)
