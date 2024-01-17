import re
from myre.pattern import MatchAny


class TestMatchAny:
    p1 = MatchAny.compile(r"worl", r"world", r"world", r"hello", r"ello", flag=re.I)
    p2 = re.compile("worl|world|world|hello|ello", re.I)

    def test_findall(self):
        for text in [
            "Hello World",
        ]:
            assert self.p1.findall(text) == self.p2.findall(text)

    def test_finditer(self):
        for text in [
            "Hello World",
        ]:
            assert list(map(lambda x: (x.span(), x.groups()), self.p1.finditer(text))) == list(
                map(lambda x: (x.span(), x.groups()), self.p2.finditer(text))
            )
