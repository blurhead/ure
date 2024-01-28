import re
from myre.pattern import MatchALL, MatchAny


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


class TestMatchAnyWithTrim:
    pattern = MatchAny.compile(r"hello", p_trim=r"[$]", flag=re.I)

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


class TestMatchALL:
    p1 = MatchALL.compile(r"world", r"hello", flag=re.I)

    def test_findall(self):
        assert self.p1.findall("Hello World") == ["Hello", "World"]

        assert self.p1.findall("Hello word") == []
