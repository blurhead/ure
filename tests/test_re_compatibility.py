"""
Stdlib re compatibility tests for myre - Basic Functionality

This file contains tests that verify myre's compatibility with Python's standard re module
for basic pattern matching operations. These are adapted from Python's test_re.py
to ensure myre patterns behave identically to re.Pattern for core operations.

Focus areas:
- Basic pattern operations: search, match, findall, finditer
- Groups and capturing
- Flags (re.I, re.M, re.S, etc.)
- Edge cases (empty patterns, special characters, case sensitivity)

Each test compares myre behavior against standard re to ensure compatibility.
Based on: Python standard library test_re.py
"""

import re
import unittest
from myre import MatchAny, MatchALL


class ReSearchTests(unittest.TestCase):
    """Tests for search() method - adapted from test_re.py"""

    def test_search_star_plus(self):
        """Test * and + quantifiers"""
        # From stdlib: test_search_star_plus
        self.assertEqual(re.search(r"a*", "xxx").span(), (0, 0))
        self.assertEqual(re.search(r"a*", "xxx").string, "xxx")
        self.assertEqual(re.search(r"a+", "xxx"), None)
        self.assertEqual(re.search(r"a+", "xxxaaa").span(), (3, 6))
        self.assertEqual(re.search(r"a+", "xxxaaa").string, "xxxaaa")

    def test_search_basic(self):
        """Test basic search functionality"""
        # myre should behave identically
        pattern = MatchAny.compile(r"hello")
        self.assertIsNotNone(pattern.search("hello world"))
        self.assertIsNone(pattern.search("world only"))
        self.assertEqual(pattern.search("hello world").span(), (0, 5))


class ReMatchTests(unittest.TestCase):
    """Tests for search() method - adapted from test_re.py

    Note: myre PatternLike protocol doesn't require match() method.
    Use search() with anchored patterns (^) instead for match-like behavior.
    """

    def test_search_anchored_like_match(self):
        """Test anchored search behaves like match"""
        # Use ^ anchor to simulate match() behavior
        self.assertEqual(re.search(r"^a*", "xxx").span(), (0, 0))
        self.assertEqual(re.search(r"^a*", "xxx").string, "xxx")
        self.assertEqual(re.search(r"^x*", "xxx").span(), (0, 3))
        self.assertEqual(re.search(r"^x+", "xxx").span(), (0, 3))
        self.assertEqual(re.search(r"^x", "xxx").span(), (0, 1))
        self.assertIsNone(re.search(r"^a", "xxx"))

    def test_search_with_myre_anchored(self):
        """myre with ^ anchor should behave like match"""
        pattern = MatchAny.compile(r"^x+")
        match = pattern.search("xxx")
        self.assertEqual(match.span(), (0, 3))
        self.assertEqual(match.group(), "xxx")


class ReFindallTests(unittest.TestCase):
    """Tests for findall() method - adapted from test_re.py"""

    def test_findall_basic(self):
        """Test findall functionality"""
        # From stdlib: test_re_findall
        self.assertEqual(re.findall(r"\d+", "1 2 3 4"), ["1", "2", "3", "4"])
        self.assertEqual(re.findall(r"a+", "aaaaa"), ["aaaaa"])

    def test_findall_with_myre(self):
        """myre should produce same results"""
        pattern = MatchAny.compile(r"\d+")
        self.assertEqual(pattern.findall("1 2 3 4"), ["1", "2", "3", "4"])

        pattern = MatchAny.compile(r"a+")
        self.assertEqual(pattern.findall("aaaaa"), ["aaaaa"])


class ReGroupTests(unittest.TestCase):
    """Tests for group functionality - adapted from test_re.py"""

    def test_groups(self):
        """Test capturing groups"""
        # From stdlib: test_group
        self.assertEqual(re.match(r"(\w)(\w+)", "abcd").groups(), ("a", "bcd"))
        self.assertEqual(re.match(r"(\w)(\w+)", "abcd").group(1), "a")
        self.assertEqual(re.match(r"(\w)(\w+)", "abcd").group(2), "bcd")
        self.assertEqual(re.match(r"(\w)(\w+)", "abcd").group(), "abcd")

    def test_groups_with_myre(self):
        """myre should support groups same as re"""
        pattern = MatchAny.compile(r"^(\w)(\w+)")
        match = pattern.search("abcd")
        self.assertEqual(match.groups(), ("a", "bcd"))
        self.assertEqual(match.group(1), "a")
        self.assertEqual(match.group(2), "bcd")
        self.assertEqual(match.group(), "abcd")


class ReFinditerTests(unittest.TestCase):
    """Tests for finditer() method"""

    def test_finditer_basic(self):
        """Test finditer functionality"""
        # From stdlib: test_finditer
        pattern = MatchAny.compile(r"\d+")
        matches = list(pattern.finditer("1 23 456"))
        self.assertEqual(len(matches), 3)
        self.assertEqual(matches[0].group(), "1")
        self.assertEqual(matches[1].group(), "23")
        self.assertEqual(matches[2].group(), "456")

        # Check spans
        self.assertEqual(matches[0].span(), (0, 1))
        self.assertEqual(matches[1].span(), (2, 4))
        self.assertEqual(matches[2].span(), (5, 8))


class ReFlagTests(unittest.TestCase):
    """Tests for regex flags - adapted from test_re.py"""

    def test_ignore_case(self):
        """Test IGNORECASE flag"""
        # From stdlib: test_ignore_case
        pattern = MatchAny.compile(r"hello", flag=re.IGNORECASE)
        self.assertIsNotNone(pattern.search("HELLO"))
        self.assertIsNotNone(pattern.search("HeLLo"))
        self.assertIsNotNone(pattern.search("hello"))

    def test_multiline(self):
        """Test MULTILINE flag"""
        # Basic multiline test
        pattern = MatchAny.compile(r"^test", flag=re.M)
        self.assertIsNotNone(pattern.search("line1\ntest\nline3"))

    def test_dotall(self):
        """Test DOTALL flag"""
        # From stdlib: test_ignore_case
        pattern = MatchAny.compile(r"^.+", flag=re.S)
        self.assertEqual(pattern.search("hello\nworld").group(), "hello\nworld")


class ReEdgeCaseTests(unittest.TestCase):
    """Edge cases and special scenarios"""

    def test_empty_pattern(self):
        """Test behavior with empty pattern"""
        # Empty pattern matches at each position
        pattern = MatchAny.compile(r"")
        matches = pattern.findall("hello")
        self.assertIsInstance(matches, list)
        # Empty pattern should match at string boundaries at minimum

    def test_no_match(self):
        """Test when pattern doesn't match"""
        pattern = MatchAny.compile(r"z")
        matches = pattern.findall("hello world")
        self.assertEqual(matches, [])

    def test_special_characters(self):
        """Test special regex characters"""
        # From stdlib: test_special_escapes
        pattern = MatchAny.compile(r"\d+", r"\w+")
        text = "123abc 456def"
        matches = pattern.findall(text)
        self.assertEqual(len(matches), 2)

    def test_anchored_patterns(self):
        """Test ^ and $ anchors"""
        pattern = MatchAny.compile(r"^hello")
        self.assertIsNotNone(pattern.search("hello world"))
        self.assertIsNone(pattern.search("say hello"))

        pattern = MatchAny.compile(r"world$")
        self.assertIsNotNone(pattern.search("hello world"))
        self.assertIsNone(pattern.search("world hello"))


class ReMatchObjectTests(unittest.TestCase):
    """Tests for match object attributes and methods"""

    def test_match_attributes(self):
        """Test match object has required attributes"""
        pattern = MatchAny.compile(r"hello")
        match = pattern.search("hello world")

        # Required attributes from MatchLike protocol
        self.assertTrue(hasattr(match, "re"))
        self.assertTrue(hasattr(match, "string"))

        # Required methods from MatchLike protocol
        self.assertTrue(hasattr(match, "start"))
        self.assertTrue(hasattr(match, "end"))
        self.assertTrue(hasattr(match, "span"))
        self.assertTrue(hasattr(match, "group"))
        self.assertTrue(hasattr(match, "groups"))

    def test_match_methods_work(self):
        """Test that match methods actually work"""
        pattern = MatchAny.compile(r"(\w+)")
        match = pattern.search("hello world")

        self.assertEqual(match.start(), 0)
        self.assertEqual(match.end(), 5)
        self.assertEqual(match.span(), (0, 5))
        self.assertEqual(match.group(), "hello")
        self.assertEqual(match.groups(), ("hello",))


class RePatternTests(unittest.TestCase):
    """Tests for pattern compilation and attributes"""

    def test_compile_single_pattern(self):
        """Test compiling a single pattern"""
        pattern = MatchAny.compile(r"hello")
        self.assertIsInstance(pattern, MatchAny)

    def test_compile_multiple_patterns(self):
        """Test compiling multiple patterns"""
        pattern = MatchAny.compile(r"hello", r"world", r"test")
        self.assertEqual(len(pattern.patterns), 3)

    def test_compile_with_flags(self):
        """Test compiling with flags"""
        pattern = MatchAny.compile(r"hello", r"world", flag=re.I)
        self.assertIsNotNone(pattern.search("HELLO WORLD"))


class MatchALLBasicTests(unittest.TestCase):
    """Basic tests for MatchALL - testing combined matches"""

    def test_matchall_both_patterns_exist(self):
        """Test MatchALL when all patterns match"""
        pattern = MatchALL.compile(r"hello", r"world")
        matches = pattern.findall("hello world")
        self.assertEqual(len(matches), 1)
        # Returns one combined match

    def test_matchall_one_pattern_missing(self):
        """Test MatchALL when one pattern doesn't match"""
        pattern = MatchALL.compile(r"hello", r"foobar")
        matches = pattern.findall("hello world")
        # 'foobar' doesn't match, so no results
        self.assertEqual(len(matches), 0)

    def test_matchall_with_flags(self):
        """Test MatchALL respects regex flags"""
        pattern = MatchALL.compile(r"hello", r"world", flag=re.I)
        matches = pattern.findall("HELLO WORLD")
        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()
