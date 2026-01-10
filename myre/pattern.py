from __future__ import annotations

import heapq
import re
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator, List, NamedTuple, Optional, Set, cast

from typing_extensions import Self, final

from myre.match import ComposeMatch, MatchWithOffset
from myre.protocol import MatchLike, PatternLike


class Mode(Enum):
    """Pattern matching modes for unified compile interface."""

    ANY = "ANY"  # Match any pattern (MatchAny)
    ALL = "ALL"  # Match all patterns (MatchALL)
    SEQ = "SEQ"  # Match patterns in sequence (MatchSeq)


def _compile(pattern: Any, flag: int = 0) -> PatternLike:
    if isinstance(pattern, re.Pattern):
        return cast(PatternLike, pattern)
    if isinstance(pattern, str):
        return cast(PatternLike, re.compile(pattern, flag))
    if isinstance(pattern, PatternLike):
        return pattern
    raise TypeError(f"{pattern} is not a valid pattern")


def compile(*patterns: Any, mode: Mode = Mode.ANY, flag: int = 0) -> PatternLike:
    """
    Unified compile interface for creating pattern objects.

    Args:
        *patterns: Variable number of patterns (str, re.Pattern, or PatternLike)
        mode: Matching mode - Mode.ANY (default), Mode.ALL, or Mode.SEQ
        flag: Regex flags (re.I, re.M, re.S, etc.)

    Returns:
        PatternLike: Compiled pattern object

    Examples:
        >>> import myre
        >>> # Match any pattern
        >>> p1 = myre.compile(r'hello', r'world', mode=myre.Mode.ANY)
        >>> # Match all patterns
        >>> p2 = myre.compile(r'hello', r'world', mode=myre.Mode.ALL)
        >>> # With flags
        >>> p3 = myre.compile(r'hello', r'world', flag=re.I, mode=myre.Mode.ANY)
        >>> # Combine with operators
        >>> combined = p1 | p2  # OR operation
        >>> filtered = p1 ^ r'ell'  # XOR operation
    """
    if not patterns:
        raise ValueError("At least one pattern is required")

    if mode == Mode.ANY:
        return MatchAny.compile(*patterns, flag=flag)
    if mode == Mode.ALL:
        return MatchALL.compile(*patterns, flag=flag)
    if mode == Mode.SEQ:
        return MatchSeq.compile(*patterns, flag=flag)
    raise ValueError(f"Invalid mode: {mode}")


class Scope(NamedTuple):
    start: int
    end: int

    def __contains__(self, item: int):  # type: ignore[override]
        return self.start <= item < self.end


@dataclass
class Masker:
    """Mask pattern matches with placeholders while preserving positions."""

    pattern: PatternLike
    placeholder: str = "."  # Default: use dot which matches any character in regex

    def mask(self, string: str, pos: int, endpos: int) -> str:
        """Replace pattern matches with placeholder chars of same length."""
        # Preserve string length by including prefix and suffix
        result = [string[:pos]]  # Add prefix before pos
        last_end = pos
        for match in self.pattern.finditer(string, pos, endpos):
            # Add text before match
            result.append(string[last_end : match.start()])
            # Add placeholder of same length
            result.append(self.placeholder * len(match.group()))
            last_end = match.end()
        # Add remaining text within search range
        result.append(string[last_end:endpos])
        # Add suffix after endpos to preserve full string length
        result.append(string[endpos:])
        return "".join(result)


_MATCH_NONE: PatternLike = cast(PatternLike, re.compile(r"(?!.?)"))
_MATCH_ALL: PatternLike = cast(PatternLike, re.compile(r".?"))


@dataclass
class Base:
    p_mask: PatternLike = field(init=False, default=_MATCH_NONE)
    p_deny: PatternLike = field(init=False, default=_MATCH_NONE)

    def __and__(self, other: Any) -> MatchALL:
        return MatchALL.compile(self, other)

    def __or__(self, other: Any) -> MatchAny:
        return MatchAny.compile(self, other)

    def __add__(self, other: Any) -> MatchSeq:
        """Sequence operation (+): Match patterns in sequential order."""
        return MatchSeq.compile(self, other)

    def __truediv__(self, other: Any) -> SplitMatch:
        """Split operation (/): Split string by delimiter, then match in each segment."""
        return SplitMatch.compile(self, other)

    def __xor__(self, other: Any) -> Self:
        self = deepcopy(self)
        self.p_deny = MatchAny.compile(self.p_deny, other)
        return self

    def __matmul__(self, other: Any) -> Self:
        """
        Mask operation (@): Replace pattern matches with a placeholder character.

        The placeholder character is used to mask out unwanted patterns while
        preserving text length and positions.

        Args:
            other: Can be a pattern string/PatternLike, or a tuple(pattern, placeholder)

        Examples:
            # Use default placeholder '.'
            pattern = myre.compile(r"hello.world") @ r"\\s+"

            # Use custom placeholder (e.g., space)
            pattern = myre.compile(r"hello world") @ (r"[.,!?]", " ")

        Note: Choose a placeholder that works with your pattern. For example:
            - Use '.' if your pattern uses wildcards
            - Use ' ' (space) for word matching
            - Use any character that makes sense in your context
        """
        self = deepcopy(self)
        if isinstance(other, tuple) and len(other) == 2:
            mask_pattern, placeholder = other
            self.p_mask = MatchAny.compile(self.p_mask, mask_pattern)
            # Store placeholder as an attribute on p_mask for later retrieval
            object.__setattr__(self.p_mask, "_placeholder", str(placeholder)[0])
        else:
            self.p_mask = MatchAny.compile(self.p_mask, other)
        return self

    def _findnext(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        raise NotImplementedError

    @final
    def finditer(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Iterator[MatchLike]:
        # Get placeholder from p_mask if set, otherwise use default
        placeholder = getattr(self.p_mask, "_placeholder", ".") if self.p_mask != _MATCH_NONE else "."
        masker = Masker(self.p_mask, placeholder=placeholder)
        masked = masker.mask(string, pos, endpos)
        if self.p_deny.search(masked, pos, endpos):
            return
        for hit, _ in self._findnext(masked, pos, endpos):
            # Since mask preserves positions, yield the hit with original string
            if isinstance(hit, re.Match):
                # Wrap with original string context
                from myre.match import MatchWithOffset

                yield cast(MatchLike, ComposeMatch((MatchWithOffset(hit, (0, 0)),), self, string))
            else:
                # For ComposeMatch, just update the string reference
                if isinstance(hit, ComposeMatch):
                    yield cast(MatchLike, ComposeMatch(hit.hits, hit.re, string))
                else:
                    yield hit

    def findall(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> List[str]:
        return [match.group() for match in self.finditer(string, pos, endpos)]

    def search(self, string: str, pos: int = 0, endpos: int = sys.maxsize) -> Optional[MatchLike]:
        return next(self.finditer(string, pos, endpos), None)


@dataclass
class MatchAny(Base):
    patterns: tuple[PatternLike, ...]

    def _findnext(
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
    def _findnext(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        if not self.patterns:
            return

        # MatchALL语义：所有pattern都必须在string中找到匹配
        # 允许匹配重叠（与标准库的lookahead类似）
        # 算法：为每个pattern取第一个匹配，组合成一个ComposeMatch

        all_hits: list[MatchWithOffset] = []

        # 为每个pattern收集第一个匹配（允许重叠）
        for pattern in self.patterns:
            for match in pattern.finditer(string, pos, endpos):
                if isinstance(match, re.Match):
                    all_hits.append(MatchWithOffset(match))
                    break  # 每个pattern只取第一个匹配
                elif isinstance(match, ComposeMatch):
                    # 对于ComposeMatch，取其所有hits（保留完整信息）
                    for hit in match.hits:
                        all_hits.append(hit)
                    break  # 每个pattern只取第一个匹配
            else:
                # 如果任何一个pattern没有匹配，则整个MatchALL失败
                return

        # 将所有匹配按位置排序
        sorted_hits = tuple(sorted(all_hits, key=lambda x: x.match.start()))
        yield cast(MatchLike, ComposeMatch(sorted_hits, self, string)), self


@dataclass
class MatchSeq(MatchAny):
    def _findnext(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        if not self.patterns:
            return
        hits: list[MatchWithOffset] = []

        index = 0
        for hit, pattern in super()._findnext(string, pos, endpos):
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


@dataclass
class SplitMatch(Base):
    """Split string by delimiter pattern, then match in each segment.

    The delimiter is the second pattern in self.patterns[1].
    The matching pattern is self.patterns[0].

    Example:
        pattern = SplitMatch.compile(myre.compile(r"\\d+"), ",")
        text = "123,456,789"
        # Splits by "," → ["123", "456", "789"]
        # Matches r"\\d+" in each segment → "123", "456", "789"
    """

    patterns: tuple[PatternLike, ...]
    delimiter: PatternLike = field(init=False)

    def __post_init__(self):
        if len(self.patterns) >= 2:
            object.__setattr__(self, "delimiter", self.patterns[1])
        else:
            object.__setattr__(self, "delimiter", _MATCH_NONE)

    def _findnext(
        self, string: str, pos: int = 0, endpos: int = sys.maxsize
    ) -> Iterator[tuple[MatchLike, PatternLike]]:
        if not self.patterns or self.delimiter == _MATCH_NONE:
            return

        pattern = self.patterns[0]

        # Find all delimiter positions
        delimiter_matches = list(self.delimiter.finditer(string, pos, endpos))

        # Build segments: from pos to first delimiter, between delimiters, after last delimiter
        segment_starts = [pos]
        segment_ends = []

        for delim_match in delimiter_matches:
            segment_ends.append(delim_match.start())
            segment_starts.append(delim_match.end())

        segment_ends.append(endpos)

        # Process each segment
        for seg_start, seg_end in zip(segment_starts, segment_ends, strict=False):
            if seg_start >= seg_end:  # Skip empty segments
                continue

            # Match the pattern in this segment
            for match in pattern.finditer(string, seg_start, seg_end):
                yield match, pattern

    @classmethod
    def compile(cls, *patterns: Any, flag: int = 0) -> Self:
        """Compile a SplitMatch pattern.

        Args:
            *patterns: First pattern to match, second pattern is delimiter
            flag: Regex flags

        Example:
            SplitMatch.compile(myre.compile("\\d+"), ",")
        """
        if len(patterns) < 2:
            raise ValueError("SplitMatch requires at least 2 patterns: (match_pattern, delimiter)")
        compiled = tuple(_compile(p, flag) for p in patterns)
        return cls(compiled)
