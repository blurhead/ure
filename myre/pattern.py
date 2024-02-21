from __future__ import annotations

import heapq
import re
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Iterator, List, NamedTuple, Optional, Set, cast

from typing_extensions import Self, final

from myre.match import ComposeMatch, MatchWithOffset
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

    def restore(self, string: str, hit: MatchLike) -> ComposeMatch:
        start, end = hit.start(), hit.end()
        for s, e in self.scopes:
            if s <= start:
                start += e - s
            if s < end:
                end += e - s
            else:
                break
        if isinstance(hit, ComposeMatch):
            return ComposeMatch(hit.hits, hit.re, string)
        if isinstance(hit, re.Match):
            return ComposeMatch((MatchWithOffset(hit, (start - hit.start(), end - hit.end())),), hit.re, string)
        raise TypeError(f"{hit} is not a valid match")


_MATCH_NONE: PatternLike = cast(PatternLike, re.compile(r"(?!.?)"))
_MATCH_ALL: PatternLike = cast(PatternLike, re.compile(r".?"))


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

    def __finditer__(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        raise NotImplementedError

    @final
    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]:
        trimmer = Trimmer(self.p_trim)
        trimmed = trimmer.remove(string, pos, endpos)
        if self.p_deny.search(trimmed, pos, endpos):
            return
        for hit, _ in self.__finditer__(trimmed, pos, endpos):
            yield cast(MatchLike, trimmer.restore(string, hit))

    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]:
        return [match.group() for match in self.finditer(string, pos, endpos)]

    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike]:
        return next(self.finditer(string, pos, endpos), None)


@dataclass
class MatchAny(Base):
    patterns: tuple[PatternLike, ...]

    def __finditer__(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        pq: List[tuple[int, MatchLike, Iterator[MatchLike], PatternLike]] = []
        indices: Set[int] = set()

        for pattern in self.patterns:
            follow = pattern.finditer(string, pos, endpos)
            while hit := next(follow, None):
                if any(i in indices for i in range(*hit.span())):
                    continue
                indices.update(range(*hit.span()))
                heapq.heappush(pq, (hit.start(), hit, follow, pattern))
                break

        while pq:
            _, hit, follow, pattern = heapq.heappop(pq)
            yield hit, pattern
            while hit := next(follow, None):
                if any(i in indices for i in range(*hit.span())):
                    continue
                indices.update(range(*hit.span()))
                heapq.heappush(pq, (hit.start(), hit, follow, pattern))
                break

    @classmethod
    def compile(cls, *patterns: Any, flag: int = 0) -> Self:
        return cls(tuple(_compile(pattern, flag) for pattern in patterns))


@dataclass
class MatchALL(MatchAny):
    def __finditer__(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        if not self.patterns:
            return
        hits: list[MatchWithOffset] = []
        patterns = list(self.patterns)

        for hit, pattern in super().__finditer__(string, pos, endpos):
            if pattern not in patterns:
                continue
            patterns.remove(pattern)
            if isinstance(hit, re.Match):
                hits.append(MatchWithOffset(hit))
            elif isinstance(hit, ComposeMatch):
                hits.extend(hit.hits)

            if not patterns:
                yield cast(MatchLike, ComposeMatch(tuple(hits), self, string)), self
                patterns = list(self.patterns)
                hits = []


@dataclass
class MatchSeq(MatchAny):
    def __finditer__(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        if not self.patterns:
            return
        hits: list[MatchWithOffset] = []

        index = 0
        for hit, pattern in super().__finditer__(string, pos, endpos):
            if pattern == self.patterns[index]:
                index += 1
                if isinstance(hit, re.Match):
                    hits.append(MatchWithOffset(hit))
                elif isinstance(hit, ComposeMatch):
                    hits.extend(hit.hits)

            if index == len(self.patterns):
                yield cast(MatchLike, ComposeMatch(tuple(hits), self, string)), self
                index = 0
                hits = []


if __name__ == "__main__":
    pattern = MatchALL.compile(MatchAny.compile("(abc)", "(bcd)"), "(def.)", "(123)")
    for hit in pattern.finditer("abc deff123 bcd , abccdef1123"):
        print(hit.group(2))
    # pattern = MatchAny.compile("(?P<a>aaa)", "(?P<a>bbb)", "(?P<a>ccc)")
    # for hit in pattern.finditer("aaa aaa bbb aaa ccc bbb aaa"):
    # print(hit.span("a"), hit.group("a"), hit.span(1), hit.group(1))
