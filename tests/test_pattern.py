import re
from myre import MatchALL, MatchAny


class TestMatchAny:
    p1 = MatchAny.compile(r"worl", r"world", r"world", r"hello", r"ello", flag=re.I)
    p2 = MatchAny.compile(r"worl|world|world|hello|ello", flag=re.I)

    def test_findall(self):
        for text in ["Hello World", "World hello"]:
            assert self.p1.findall(text) == self.p2.findall(text)

    def test_finditer(self):
        for text in ["Hello World", "World hello"]:
            assert list(self.p1.finditer(text)) == list(self.p2.finditer(text))

    def test_search(self):
        for text in ["Hello World", "World hello"]:
            assert self.p1.search(text) == self.p2.search(text)


class TestMatchAnySub:
    pattern = MatchAny.compile(r"hello", flag=re.I) - r"[$]"

    def test_findall(self):
        for text in ["Hell$o World"]:
            for hit in self.pattern.finditer(text):
                assert hit.group() == "Hell$o"

    def test_position(self):
        for text in ["Hell$o World"]:
            for hit in self.pattern.finditer(text):
                assert text[hit.start() : hit.end()] == "Hell$o"


class TestMatchAnyXor:
    pattern = MatchAny.compile(r"h\wllo", flag=re.I) ^ r"ell"

    def test_findall(self):
        assert self.pattern.findall("Hello World") == []
        assert self.pattern.findall("Hallo World") == ["Hallo"]


class TestMatchALL:
    p1 = MatchALL.compile(r"world", r"hello", flag=re.I)

    def test_findall(self):
        assert self.p1.findall("Hello word") == []
        assert self.p1.findall("Hello Hello World") == ["Hello Hello World"]
        assert self.p1.findall("Hello Hello World Hello World") == ["Hello Hello World", "Hello World"]
