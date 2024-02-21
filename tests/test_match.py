import re
from typing import cast
from myre.match import MatchWithOffset, ComposeMatch
from myre import MatchLike
from myre.protocol import PatternLike


class TestComposeMatchWithoutOffset:
    pattern: PatternLike = cast(PatternLike, re.compile(r"(?P<w1>\w+) (?P<w2>\w+)"))
    content: str = "hello world hello world"

    @property
    def hits(self):
        return tuple(MatchWithOffset(cast(re.Match, hit)) for hit in self.pattern.finditer(self.content))

    def test_match_like(self):
        assert isinstance(self.pattern, PatternLike)

    def test_protocol(self):
        assert isinstance(ComposeMatch[str](self.hits[:1], self.pattern, self.content), MatchLike)

    def test_eq(self):
        assert ComposeMatch[str](self.hits, self.pattern, self.content) == ComposeMatch[str](
            self.hits, self.pattern, self.content
        )

    def test_start(self):
        for key in (0, 1, "w1", "w2"):
            assert ComposeMatch[str](self.hits[:1], self.pattern, self.content).start(key) == self.hits[0].match.start(
                key
            )
            assert ComposeMatch[str](self.hits[-1:], self.pattern, self.content).start(key) == self.hits[
                -1
            ].match.start(key)

    def test_end(self):
        for key in (0, 1, "w1", "w2"):
            assert ComposeMatch[str](self.hits[:1], self.pattern, self.content).end(key) == self.hits[0].match.end(key)
            assert ComposeMatch[str](self.hits[-1:], self.pattern, self.content).end(key) == self.hits[-1].match.end(
                key
            )

    def test_span(self):
        for key in (0, 1, "w1", "w2"):
            assert ComposeMatch[str](self.hits[:1], self.pattern, self.content).span(key) == self.hits[0].match.span(
                key
            )
            assert ComposeMatch[str](self.hits[-1:], self.pattern, self.content).span(key) == self.hits[-1].match.span(
                key
            )

    def test_group(self):
        for key in (0, 1, 2, "w1", "w2"):
            print(
                key,
                ComposeMatch[str](self.hits[:1], self.pattern, self.content).group(key),
                ",",
                self.hits[0].match.group(key),
            )
            # assert ComposeMatch[str](self.hits[:1], self.pattern).group(key) == self.hits[0].match.group(key)
            # assert ComposeMatch[str](self.hits[-1:], self.pattern).group(key) == self.hits[-1].match.group(key)
