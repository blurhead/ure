import re
from typing import Any, Tuple, cast

from myre.protocol import PatternLike


def _compile(pattern: Any, flag: int = 0) -> PatternLike:
    if isinstance(pattern, re.Pattern):
        return cast(PatternLike, pattern)
    if isinstance(pattern, str):
        return cast(PatternLike, re.compile(pattern, flag))
    if isinstance(pattern, PatternLike):
        return pattern
    raise TypeError(f"{pattern} is not a valid pattern")


class PositionPattern:
    patterns: Tuple[PatternLike]
