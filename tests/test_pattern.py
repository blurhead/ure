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
        for text in [
            "Hell$o World",
        ]:
            assert self.pattern.findall(text) == ["Hello"]

    def test_position(self):
        for text in [
            "Hell$o World",
        ]:
            for matcher in self.pattern.finditer(text):
                assert matcher.group() == "Hello"
                assert text[matcher.start() : matcher.end()] == "Hell$o"


class TestMatchAnyXor:
    pattern = MatchAny.compile(r"h\wllo", flag=re.I) ^ r"ell"

    def test_findall(self):
        assert self.pattern.findall("Hello World") == []
        assert self.pattern.findall("Hallo World") == ["Hallo"]


class TestMatchALL:
    p1 = MatchALL.compile(r"world", r"hello", flag=re.I)
    p2 = MatchALL.compile(r"world", r"hello", flag=re.I, order=True)

    def test_findall(self):
        assert self.p1.findall("Hello word") == []
        assert self.p1.findall("Hello Hello World") == ["Hello", "Hello", "World"]
        assert self.p1.findall("Hello Hello World Hello World") == ["Hello", "Hello", "World", "Hello", "World"]
        assert self.p2.findall("Hello world") == []
        assert self.p2.findall("World Hello World Hello") == ["World", "Hello", "World", "Hello"]
        assert self.p2.findall("Hello Hello World Hello World Hello") == ["World", "Hello", "World", "Hello"]
