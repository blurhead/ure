import re
from myre.match import OffsetMatch
from myre import MatchLike


class TestOffsetMatch:
    pattern = re.compile(".*")

    @property
    def default(self):
        return next(self.pattern.finditer(""))

    def test_protocol(self):
        assert isinstance(OffsetMatch(self.default, 0, 0), MatchLike)

    def test_eq(self):
        assert OffsetMatch(self.default, 0, 0) == OffsetMatch(self.default, 0, 0)

    def test_span(self):
        assert OffsetMatch(self.default, 1, 2).span() == (1, 2)

    def test_group(self):
        assert OffsetMatch(self.default, 1, 2).group() == self.default.group()
