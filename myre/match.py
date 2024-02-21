from __future__ import annotations

import re
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, AnyStr, Generic, TypeVar

from myre.protocol import MatchLike, PatternLike

_T = TypeVar("_T")


@dataclass(frozen=True)
class MatchWithOffset(Generic[AnyStr]):
    match: re.Match[AnyStr]
    offset: tuple[int, int] = (0, 0)

    def start(self, group: int | str = 0) -> int:
        return self.match.start(group) + self.offset[0]

    def end(self, group: int | str = 0) -> int:
        return self.match.end(group) + self.offset[1]

    def span(self, group: int | str = 0) -> tuple[int, int]:
        return (self.start(group), self.end(group))


@dataclass
class ComposeMatch(Generic[AnyStr]):
    _hits: tuple[MatchWithOffset[AnyStr], ...]
    _re: PatternLike
    _string: AnyStr

    @property
    def hits(self):
        return self._hits

    def start(self, group: int | str = 0) -> int:
        return self.span(group)[0]

    def end(self, group: int | str = 0) -> int:
        return self.span(group)[-1]

    def span(self, group: int | str = 0) -> tuple[int, int]:
        if group == 0:
            start = self._hits[0].start(group)
            end = self._hits[-1].end(group)
            return start, end
        if isinstance(group, str):
            for hit in self._hits:
                with suppress(IndexError):
                    return hit.span(group)
        elif isinstance(group, int):
            start = 0
            for hit in self._hits:
                while start < group:
                    try:
                        span = hit.span(start + 1)
                    except IndexError as e:
                        group -= start
                        if group == 0:
                            raise IndexError("no such group") from e
                        start = 0
                        break
                    if start + 1 == group:
                        return span
                    start += 1
        raise IndexError("no such group")

    @property
    def re(self) -> PatternLike[AnyStr]:
        return self._re

    @property
    def string(self) -> AnyStr:
        return self._string

    def groups(self) -> tuple[AnyStr, ...]:
        groups: tuple[AnyStr, ...] = ()
        for hit in self._hits:
            index = 1
            while True:
                try:
                    groups += (hit.match.group(index),)
                except IndexError:
                    break
                index += 1
        return groups

    def group(self, __group: str | int = 0) -> AnyStr:
        return self._string[self.start(__group) : self.end(__group)]

    def __repr__(self):
        return f"<myre.ComposeMatch(re={self.re!r}, string={self.string!r} object; span={self.span()}, match={self.group()})"

    def __eq__(self, other: Any):
        if isinstance(other, (MatchLike, re.Match)):
            return self.span() == other.span() and self.string == other.string
        return False
