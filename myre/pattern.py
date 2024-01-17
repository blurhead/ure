import heapq
import re
import sys
from dataclasses import dataclass
from typing import Any, Iterator, List, Optional, Set, Tuple, cast

from typing_extensions import Self

from myre.protocol import MatchLike, PatternLike


def _compile(pattern: Any, flag: int = 0) -> PatternLike:
    if isinstance(pattern, re.Pattern):
        return cast(PatternLike, pattern)
    if isinstance(pattern, str):
        return cast(PatternLike, re.compile(pattern, flag))
    if isinstance(pattern, PatternLike):
        return pattern
    raise TypeError(f"{pattern} is not a valid pattern")


@dataclass
class MatchAny:
    patterns: Tuple[PatternLike, ...]
    # strip: PatternLike = ""

    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]:
        pq: List[Tuple[int, MatchLike, Iterator[MatchLike]]] = []
        indices: Set[int] = set()

        for pattern in self.patterns:
            it = pattern.finditer(string, pos, endpos)
            try:
                next_match = next(it)
                if any(i in indices for i in range(*next_match.span())):
                    continue
                indices.update(range(*next_match.span()))
                heapq.heappush(pq, (next_match.start(), next_match, it))
            except StopIteration:
                continue

        while pq:
            _, matched, it = heapq.heappop(pq)
            yield matched
            try:
                next_match = next(it)
                if any(i in indices for i in range(*next_match.span())):
                    continue
                indices.update(range(*next_match.span()))
                heapq.heappush(pq, (next_match.start(), next_match, it))
            except StopIteration:
                continue

    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]:
        return [match.group() for match in self.finditer(string, pos, endpos)]

    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike]:
        return next(self.finditer(string, pos, endpos), None)

    @classmethod
    def compile(cls, *patterns: Any, flag: int = 0) -> Self:
        return cls(tuple(_compile(pattern, flag) for pattern in patterns))
