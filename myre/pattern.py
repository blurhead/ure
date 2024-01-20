import heapq
import re
import sys
from dataclasses import dataclass
from typing import Any, Iterator, List, NamedTuple, Optional, Pattern, Set, Tuple, cast

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
class MatchAny:
    patterns: Tuple[PatternLike, ...]
    janitor: Pattern

    def _sanitize(self, string: str, pos: int, endpos: int) -> Iterator[Scope]:
        for match in self.janitor.finditer(string, pos, endpos):
            yield Scope(*match.span())

    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[OffsetMatch]:
        scopes = []
        for start, end in self._sanitize(string, pos, endpos):
            scopes.append(Scope(start, end))
            string = string[:start] + string[end:]

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

        def restore(matcher: MatchLike) -> OffsetMatch:
            start, end = matcher.start(), matcher.end()
            for s, e in scopes:
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

        while pq:
            _, matcher, follow = heapq.heappop(pq)
            yield restore(matcher)
            try:
                matcher = next(follow)
                if any(i in indices for i in range(*matcher.span())):
                    continue
                indices.update(range(*matcher.span()))
                heapq.heappush(pq, (matcher.start(), matcher, follow))
            except StopIteration:
                continue

    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]:
        return [match.group() for match in self.finditer(string, pos, endpos)]

    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[OffsetMatch]:
        return next(self.finditer(string, pos, endpos), None)

    @classmethod
    def compile(cls, *patterns: Any, janitor: Any = "^$", flag: int = 0) -> Self:
        return cls(tuple(_compile(pattern, flag) for pattern in patterns), re.compile(janitor, flag))
