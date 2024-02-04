from __future__ import annotations

import heapq
import re
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Iterator, List, NamedTuple, Optional, Set, Tuple, cast

from typing_extensions import Self

from myre.match import OffsetMatch
from myre.protocol import MatchLike, PatternLike


def _compile(pattern: Any, flag: int = 0) -> PatternLike:
    if isinstance(pattern, re.Pattern):
        return cast(PatternLike, pattern)
    if isinstance(pattern, str):
        return cast(PatternLike, re.compile(pattern, flag))
    if isinstance(pattern, PatternLike):
        return pattern
    raise TypeError(f"{pattern} is not a valid pattern")


class Scope(NamedTuple):
    start: int
    end: int

    def __contains__(self, item: int):  # type: ignore[override]
        return self.start <= item < self.end


@dataclass
class Trimmer:
    pattern: PatternLike

    @cached_property
    def scopes(self) -> List[Scope]:
        return []

    def remove(self, string: str, pos: int, endpos: int) -> str:
        for match in self.pattern.finditer(string, pos, endpos):
            scope = Scope(*match.span())
            string = string[: scope.start] + string[scope.end :]
            self.scopes.append(scope)
        return string

    def restore(self, matcher: MatchLike) -> OffsetMatch:
        start, end = matcher.start(), matcher.end()
        for s, e in self.scopes:
            if s <= start:
                start += e - s
            if s < end:
                end += e - s
            else:
                break
        if isinstance(matcher, OffsetMatch):
            matcher = matcher._match
        elif not isinstance(matcher, re.Match):
            raise TypeError(f"{matcher} is not a valid match")
        return OffsetMatch(matcher, start - matcher.start(), end - matcher.end())


_MATCH_NONE = re.compile(r"(?!.?)")
_MATCH_ALL = re.compile(r".?")


@dataclass
class Base:
    p_trim: PatternLike = field(init=False, default=_MATCH_NONE)
    p_deny: PatternLike = field(init=False, default=_MATCH_NONE)

    def __and__(self, other: Any) -> PatternLike:
        return MatchALL.compile(self, other)

    def __or__(self, other: Any) -> PatternLike:
        return MatchAny.compile(self, other)

    def __xor__(self, other: Any) -> PatternLike:
        self = deepcopy(self)
        self.p_deny = MatchAny.compile(self.p_deny, other)
        return self

    def __sub__(self, other: Any) -> PatternLike:
        self = deepcopy(self)
        self.p_trim = MatchAny.compile(self.p_trim, other)
        return self

    def findnext(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]:
        raise NotImplementedError

    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[OffsetMatch]:
        trimmer = Trimmer(self.p_trim)
        string = trimmer.remove(string, pos, endpos)
        for match in self.findnext(string, pos, endpos):
            if self.p_deny.search(match.group()):
                continue
            yield trimmer.restore(match)

    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]:
        return [match.group() for match in self.finditer(string, pos, endpos)]

    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[OffsetMatch]:
        return next(self.finditer(string, pos, endpos), None)


@dataclass
class MatchAny(Base):
    patterns: Tuple[PatternLike, ...]

    def findnext(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]:
        pq: List[Tuple[int, MatchLike, Iterator[MatchLike]]] = []
        indices: Set[int] = set()

        for pattern in self.patterns:
            follow = pattern.finditer(string, pos, endpos)
            try:
                matcher = next(follow)
                if any(i in indices for i in range(*matcher.span())):
                    continue
                indices.update(range(*matcher.span()))
                heapq.heappush(pq, (matcher.start(), matcher, follow))
            except StopIteration:
                continue

        while pq:
            _, matcher, follow = heapq.heappop(pq)
            yield matcher
            try:
                matcher = next(follow)
                if any(i in indices for i in range(*matcher.span())):
                    continue
                indices.update(range(*matcher.span()))
                heapq.heappush(pq, (matcher.start(), matcher, follow))
            except StopIteration:
                continue

    @classmethod
    def compile(cls, *patterns: Any, flag: int = 0) -> Self:
        return cls(tuple(_compile(pattern, flag) for pattern in patterns))


@dataclass
class MatchALL(MatchAny):
    order: bool = False

    def findnext(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]:
        if not self.patterns:
            return
        matches = []
        patterns = list(self.patterns)

        for matched in super().findnext(string, pos, endpos):
            if self.order:
                if matched.re == patterns[0]:
                    patterns.pop(0)
                    matches.append(matched)
                elif matches and matched.re == matches[-1].re:
                    matches.append(matched)
            else:
                if matched.re in patterns:
                    patterns.remove(matched.re)
                matches.append(matched)

            if not patterns:
                yield from iter(matches)
                patterns = list(self.patterns)
                matches = []

    @classmethod
    def compile(cls, *patterns: Any, flag: int = 0, order: bool = False) -> Self:
        return cls(tuple(_compile(pattern, flag) for pattern in patterns), order=order)
