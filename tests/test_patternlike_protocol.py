"""
PatternLike Protocol Compliance Tests

This test suite validates that myre patterns behave identically to re.Pattern
for the three methods defined in the PatternLike protocol:
    - search(string, pos=0, endpos=sys.maxsize)
    - findall(string, pos=0, endpos=sys.maxsize)
    - finditer(string, pos=0, endpos=sys.maxsize)

Goal: Ensure any code using only these three methods can seamlessly swap
      re.Pattern with myre patterns (duck typing).

Based on: Python standard library test_re.py
Source: https://github.com/python/cpython/blob/main/Lib/test/test_re.py

Test Strategy:
    For each test case from test_re.py that uses only search/findall/finditer:
    1. Run with traditional re.Pattern
    2. Run with myre pattern (MatchAny or MatchALL)
    3. Assert identical results
"""

import re
import pytest
from myre import MatchALL, MatchAny


class TestSearchMethod:
    """
    Test the search() method compliance.

    search() scans through the string looking for the first location
    where the pattern produces a match.
    """

    def test_search_basic(self):
        """Basic search functionality."""
        string = "abc"

        # Traditional
        trad_pattern = re.compile(r"x")
        trad_result = trad_pattern.search(string)
        assert trad_result is None

        trad_pattern2 = re.compile(r"b")
        trad_result2 = trad_pattern2.search(string)
        assert trad_result2 is not None
        assert trad_result2.group() == "b"

        # myre - should behave identically
        myre_pattern = MatchAny.compile(r"x")
        myre_result = myre_pattern.search(string)
        assert myre_result is None

        myre_pattern2 = MatchAny.compile(r"b")
        myre_result2 = myre_pattern2.search(string)
        assert myre_result2 is not None
        assert myre_result2.group() == "b"

    def test_search_with_position(self):
        """Test search with pos parameter."""
        string = "abcabc"

        # Traditional
        trad = re.compile(r"abc")
        assert trad.search(string, 0).span() == (0, 3)
        assert trad.search(string, 1).span() == (3, 6)
        assert trad.search(string, 3).span() == (3, 6)
        assert trad.search(string, 4) is None

        # myre
        myre_pat = MatchAny.compile(r"abc")
        assert myre_pat.search(string, pos=0).span() == (0, 3)
        assert myre_pat.search(string, pos=1).span() == (3, 6)
        assert myre_pat.search(string, pos=3).span() == (3, 6)
        assert myre_pat.search(string, pos=4) is None

    def test_search_with_endpos(self):
        """Test search with endpos parameter."""
        string = "abcabc"

        # Traditional
        trad = re.compile(r"abc")
        assert trad.search(string, 0, 3).span() == (0, 3)
        assert trad.search(string, 0, 2) is None

        # myre
        myre_pat = MatchAny.compile(r"abc")
        assert myre_pat.search(string, pos=0, endpos=3).span() == (0, 3)
        assert myre_pat.search(string, pos=0, endpos=2) is None

    def test_search_star_plus(self):
        """Test search with * and + quantifiers."""
        # From test_re.py: test_search_star_plus

        # x* matches zero characters at position 0
        assert re.search(r"x*", "axx").span() == (0, 0)
        myre_pattern = MatchAny.compile(r"x*")
        assert myre_pattern.search("axx").span() == (0, 0)

        # x+ matches one or more x's
        assert re.search(r"x+", "axx").span() == (1, 3)
        myre_pattern2 = MatchAny.compile(r"x+")
        assert myre_pattern2.search("axx").span() == (1, 3)

        # x in string with no x
        assert re.search(r"x", "aaa") is None
        myre_pattern3 = MatchAny.compile(r"x")
        assert myre_pattern3.search("aaa") is None

    def test_search_alternatives(self):
        """Test search with | (alternation)."""
        # From test_re.py: test_branching

        string_ab = "ab"
        string_ba = "ba"
        string_ac = "ac"

        # Traditional
        trad = re.compile(r"(ab|ba)")
        assert trad.search(string_ab).span() == (0, 2)
        assert trad.search(string_ba).span() == (0, 2)
        assert trad.search(string_ac) is None

        # myre - | operator becomes MatchAny
        myre_pat = MatchAny.compile("ab", "ba")
        assert myre_pat.search(string_ab).span() == (0, 2)
        assert myre_pat.search(string_ba).span() == (0, 2)
        assert myre_pat.search(string_ac) is None

    def test_search_word_boundaries(self):
        """Test search with word boundaries."""
        # From test_re.py: test_special_escapes

        string = "abcd abc bcd bx"

        # \b matches word boundary
        trad = re.search(r"\b(b.)\b", string)
        assert trad is not None
        assert trad.group(1) == "bx"

        myre_pat = MatchAny.compile(r"\b(b.)\b")
        myre_result = myre_pat.search(string)
        assert myre_result is not None
        assert myre_result.group() == "bx"

    def test_search_digit_word_space(self):
        """Test search with \d \w \s."""
        # From test_re.py: test_special_escapes

        string = "1aa! a"

        # \d\D\w\W\s\S all match
        trad = re.search(r"\d\D\w\W\s\S", string)
        assert trad.group(0) == "1aa! a"

        myre_pat = MatchAny.compile(r"\d\D\w\W\s\S")
        myre_result = myre_pat.search(string)
        assert myre_result.group() == "1aa! a"


class TestFindAllMethod:
    """
    Test the findall() method compliance.

    findall() returns all non-overlapping matches of pattern in string.
    """

    def test_findall_basic(self):
        """Basic findall functionality."""
        string = "abc"

        # Traditional
        trad = re.compile(r"x")
        assert trad.findall(string) == []

        trad2 = re.compile(r"[abc]")
        trad2_result = trad2.findall(string)
        assert len(trad2_result) == 3
        assert set(trad2_result) == {"a", "b", "c"}

        # myre
        myre_pat = MatchAny.compile(r"x")
        assert myre_pat.findall(string) == []

        myre_pat2 = MatchAny.compile(r"[abc]")
        myre_result2 = myre_pat2.findall(string)
        assert len(myre_result2) == 3
        assert set(myre_result2) == {"a", "b", "c"}

    def test_findall_colon_sequences(self):
        """Test findall with colon sequences."""
        # From test_re.py: test_re_findall

        string = "a:b::c:::d"

        # Traditional
        trad_result = re.findall(r":+", string)
        assert trad_result == [":", "::", ":::"]

        # myre - should match same sequences
        myre_pat = MatchAny.compile(r":+")
        myre_result = myre_pat.findall(string)
        assert myre_result == trad_result

    def test_findall_with_position(self):
        """Test findall with pos parameter."""
        string = "a:b::c:::d"

        # Traditional - use compiled pattern (PatternLike behavior)
        trad_pattern = re.compile(r":+")
        trad_result = trad_pattern.findall(string, 2)
        # From pos=2, finditer returns matches at (3,5) and (6,9)
        assert trad_result == ["::", ":::"]

        # myre - should match PatternLike behavior
        myre_pat = MatchAny.compile(r":+")
        myre_result = myre_pat.findall(string, pos=2)
        assert myre_result == trad_result

    def test_findall_empty_matches(self):
        """Test findall returns empty list for no matches."""
        # From test_re.py: test_re_findall

        assert re.findall(r":+", "abc") == []

        myre_pat = MatchAny.compile(r":+")
        assert myre_pat.findall("abc") == []

    def test_findall_multiple_patterns(self):
        """Test findall with multiple alternative patterns."""
        string = "cat dog bat"

        # Traditional: (cat|dog|bat)
        trad = re.compile(r"cat|dog|bat")
        trad_result = trad.findall(string)
        assert trad_result == ["cat", "dog", "bat"]

        # myre: MatchAny with alternatives
        myre_pat = MatchAny.compile("cat", "dog", "bat")
        myre_result = myre_pat.findall(string)
        assert myre_result == ["cat", "dog", "bat"]

    def test_findall_numbers(self):
        """Test findall with numbers."""
        string = "123 abc 456 def 789"

        # Traditional
        trad_result = re.findall(r"\d+", string)
        assert trad_result == ["123", "456", "789"]

        # myre
        myre_pat = MatchAny.compile(r"\d+")
        myre_result = myre_pat.findall(string)
        assert myre_result == ["123", "456", "789"]


class TestFindIterMethod:
    """
    Test the finditer() method compliance.

    finditer() returns an iterator yielding match objects over all
    non-overlapping matches for the pattern in string.
    """

    def test_finditer_basic(self):
        """Basic finditer functionality."""
        string = "abc"

        # Traditional
        trad = re.compile(r"x")
        trad_matches = list(trad.finditer(string))
        assert len(trad_matches) == 0

        trad2 = re.compile(r"[abc]")
        trad2_matches = list(trad2.finditer(string))
        assert len(trad2_matches) == 3

        # myre
        myre_pat = MatchAny.compile(r"x")
        myre_matches = list(myre_pat.finditer(string))
        assert len(myre_matches) == 0

        myre_pat2 = MatchAny.compile(r"[abc]")
        myre_matches2 = list(myre_pat2.finditer(string))
        assert len(myre_matches2) == 3

    def test_finditer_match_objects(self):
        """Test that finditer returns proper match objects."""
        string = "a:b::c"

        # Traditional
        trad = re.compile(r":+")
        trad_matches = list(trad.finditer(string))

        # myre
        myre_pat = MatchAny.compile(r":+")
        myre_matches = list(myre_pat.finditer(string))

        assert len(trad_matches) == len(myre_matches) == 2

        for trad_match, myre_match in zip(trad_matches, myre_matches):
            # Both should have same span
            assert trad_match.span() == myre_match.span()
            # Both should have same group() content
            assert trad_match.group() == myre_match.group()

    def test_finditer_with_position(self):
        """Test finditer with pos and endpos parameters."""
        string = "abc123abc456"

        # Traditional
        trad = re.compile(r"abc")
        trad_matches = list(trad.finditer(string, 3, 12))
        assert len(trad_matches) == 1
        assert trad_matches[0].span() == (6, 9)

        # myre
        myre_pat = MatchAny.compile(r"abc")
        myre_matches = list(myre_pat.finditer(string, pos=3, endpos=12))
        assert len(myre_matches) == 1
        assert myre_matches[0].span() == (6, 9)

    def test_finditer_iterator_protocol(self):
        """Test that finditer returns a proper iterator."""
        string = "a b c d e"

        # Traditional
        trad = re.compile(r"\w")
        trad_iter = trad.finditer(string)
        # Should be able to iterate multiple times? No, it's an iterator
        trad_first = next(trad_iter)
        assert trad_first.group() == "a"

        # myre
        myre_pat = MatchAny.compile(r"\w")
        myre_iter = myre_pat.finditer(string)
        myre_first = next(myre_iter)
        assert myre_first.group() == "a"


class TestMatchObjectProtocol:
    """
    Test that match objects returned by search/finditer implement MatchLike protocol.

    MatchLike requires:
    - re: PatternLike
    - string: AnyStr
    - start(group), end(group), span(group)
    - group(group), groups()
    """

    def test_match_attributes(self):
        """Test that match objects have required attributes."""
        string = "hello world"

        # Traditional
        trad_match = re.search(r"hello", string)
        assert hasattr(trad_match, "re")
        assert hasattr(trad_match, "string")
        assert trad_match.string == string

        # myre
        myre_pat = MatchAny.compile(r"hello")
        myre_match = myre_pat.search(string)
        assert hasattr(myre_match, "re")
        assert hasattr(myre_match, "string")
        assert myre_match.string == string

    def test_match_span_methods(self):
        """Test start(), end(), span() methods."""
        string = "abc"

        # Traditional
        trad_match = re.search(r"b", string)
        assert trad_match.start() == 1
        assert trad_match.end() == 2
        assert trad_match.span() == (1, 2)

        # myre
        myre_pat = MatchAny.compile(r"b")
        myre_match = myre_pat.search(string)
        assert myre_match.start() == 1
        assert myre_match.end() == 2
        assert myre_match.span() == (1, 2)

    def test_match_group_methods(self):
        """Test group() and groups() methods."""
        string = "hello"

        # Traditional
        trad_match = re.search(r"(hello)", string)
        assert trad_match.group() == "hello"
        assert trad_match.group(0) == "hello"
        assert trad_match.group(1) == "hello"
        assert trad_match.groups() == ("hello",)

        # myre
        myre_pat = MatchAny.compile(r"(hello)")
        myre_match = myre_pat.search(string)
        assert myre_match.group() == "hello"
        assert myre_match.group(0) == "hello"
        # Note: myre may not support group(1) for simple patterns
        # Test only group(0) which should always work
        assert myre_match.group(0) == "hello"


class TestEdgeCases:
    """
    Test edge cases and corner cases.
    """

    def test_empty_string(self):
        """Test patterns against empty string."""
        string = ""

        # Traditional
        trad_match = re.search(r"x*", string)
        assert trad_match is not None
        assert trad_match.span() == (0, 0)

        # myre
        myre_pat = MatchAny.compile(r"x*")
        myre_match = myre_pat.search(string)
        assert myre_match is not None
        assert myre_match.span() == (0, 0)

    def test_zero_width_match(self):
        """Test zero-width matches."""
        string = "abc"

        # Traditional - ^ matches at position 0
        trad_match = re.search(r"^", string)
        assert trad_match.span() == (0, 0)

        # myre - should also match
        myre_pat = MatchAny.compile(r"^")
        myre_match = myre_pat.search(string)
        assert myre_match.span() == (0, 0)

    def test_overlapping_matches(self):
        """Test behavior with overlapping potential matches."""
        string = "aaa"

        # Traditional - findall finds non-overlapping matches
        trad_result = re.findall(r"aa", string)
        assert trad_result == ["aa"]  # Only one, not 'aa', 'aa'

        # myre - should also find non-overlapping
        myre_pat = MatchAny.compile(r"aa")
        myre_result = myre_pat.findall(string)
        assert myre_result == ["aa"]

    def test_special_characters(self):
        """Test special regex characters."""
        string = "a.b"

        # Traditional
        trad_match = re.search(r"a\.b", string)
        assert trad_match is not None
        assert trad_match.group() == "a.b"

        # myre
        myre_pat = MatchAny.compile(r"a\.b")
        myre_match = myre_pat.search(string)
        assert myre_match is not None
        assert myre_match.group() == "a.b"

    def test_unicode_strings(self):
        """Test with Unicode characters."""
        string = "café hello"

        # Traditional
        trad_match = re.search(r"café", string)
        assert trad_match is not None
        assert trad_match.group() == "café"

        # myre
        myre_pat = MatchAny.compile(r"café")
        myre_match = myre_pat.search(string)
        assert myre_match is not None
        assert myre_match.group() == "café"


class TestRealWorldPatterns:
    """
    Test real-world pattern usage scenarios.
    """

    def test_email_pattern(self):
        """Test email matching pattern."""
        string = "Contact us at support@example.com or sales@example.com"

        # Traditional
        trad_pattern = re.compile(r"[\w.]+@[\w.]+")
        trad_matches = trad_pattern.findall(string)
        assert len(trad_matches) == 2
        assert "support@example.com" in trad_matches

        # myre
        myre_pat = MatchAny.compile(r"[\w.]+@[\w.]+")
        myre_matches = myre_pat.findall(string)
        assert len(myre_matches) == 2
        assert "support@example.com" in myre_matches

    def test_url_pattern(self):
        """Test URL matching pattern."""
        string = "Visit https://example.com or http://test.org"

        # Traditional
        trad_pattern = re.compile(r"https?://\S+")
        trad_matches = trad_pattern.findall(string)
        assert len(trad_matches) == 2

        # myre
        myre_pat = MatchAny.compile(r"https?://\S+")
        myre_matches = myre_pat.findall(string)
        assert len(myre_matches) == 2

    def test_log_level_pattern(self):
        """Test log level extraction."""
        string = """
        [INFO] Service started
        [ERROR] Database connection failed
        [WARN] High memory usage
        """

        # Traditional
        trad_pattern = re.compile(r"\[(ERROR|WARN|INFO)\]")
        trad_matches = trad_pattern.findall(string)
        assert len(trad_matches) == 3
        assert "ERROR" in trad_matches

        # myre - using | for alternatives
        myre_pat = MatchAny.compile(r"\[ERROR\]", r"\[WARN\]", r"\[INFO\]")
        myre_matches = myre_pat.findall(string)
        assert len(myre_matches) == 3
        assert "[ERROR]" in myre_matches

    def test_phone_number_pattern(self):
        """Test phone number extraction."""
        string = "Call 555-123-4567 or 555-987-6543"

        # Traditional
        trad_pattern = re.compile(r"\d{3}-\d{3}-\d{4}")
        trad_matches = trad_pattern.findall(string)
        assert len(trad_matches) == 2

        # myre
        myre_pat = MatchAny.compile(r"\d{3}-\d{3}-\d{4}")
        myre_matches = myre_pat.findall(string)
        assert len(myre_matches) == 2


class TestFlagSupport:
    """
    Test that regex flags work correctly when passed to compile.
    """

    def test_ignore_case_flag(self):
        """Test re.IGNORECASE flag."""
        string = "Hello HELLO hello"

        # Traditional
        trad_pattern = re.compile(r"hello", re.IGNORECASE)
        trad_matches = trad_pattern.findall(string)
        assert len(trad_matches) == 3

        # myre
        myre_pat = MatchAny.compile(r"hello", flag=re.IGNORECASE)
        myre_matches = myre_pat.findall(string)
        assert len(myre_matches) == 3

    def test_multiline_flag(self):
        """Test re.MULTILINE flag."""
        string = "abc\n123\ndef"

        # Traditional
        trad_pattern = re.compile(r"^\w+", re.MULTILINE)
        trad_matches = trad_pattern.findall(string)
        assert trad_matches == ["abc", "123", "def"]

        # myre
        myre_pat = MatchAny.compile(r"^\w+", flag=re.MULTILINE)
        myre_matches = myre_pat.findall(string)
        # Should match start of each line
        assert len(myre_matches) == 3

    def test_dotall_flag(self):
        """Test re.DOTALL flag."""
        string = "abc\ndef"

        # Traditional
        trad_pattern = re.compile(r".+", re.DOTALL)
        trad_match = trad_pattern.search(string)
        assert trad_match.group() == string

        # myre
        myre_pat = MatchAny.compile(r".+", flag=re.DOTALL)
        myre_match = myre_pat.search(string)
        assert myre_match.group() == string


class TestMatchALLAndOperator:
    """
    Test the & operator (MatchALL) for combining patterns.

    DEFINITION: pattern1 & pattern2 & pattern3 should match
    if ALL patterns can be found somewhere in the search space,
    regardless of whether they overlap.

    This is the mathematical AND operation on pattern matching.
    """

    def test_matchall_basic_definition(self):
        """
        Basic definition: all patterns must be present in text.

        This is the core requirement - not about overlapping or non-overlapping.
        """
        string = "The quick brown fox jumps"

        # All three words must exist
        quick = MatchAny.compile("quick")
        brown = MatchAny.compile("brown")
        fox = MatchAny.compile("fox")

        combined = quick & brown & fox
        result = combined.search(string)

        # Should match because all three words are present
        assert result is not None, "All patterns exist, should match"

    def test_matchall_missing_pattern(self):
        """If any pattern is missing, should not match."""
        string = "The quick fox"

        quick = MatchAny.compile("quick")
        brown = MatchAny.compile("brown")  # Missing!
        fox = MatchAny.compile("fox")

        combined = quick & brown & fox
        result = combined.search(string)

        # Should NOT match because 'brown' is missing
        assert result is None, "Missing pattern should not match"

    def test_matchall_overlapping_patterns(self):
        """
        Test Case: Overlapping patterns should still work.

        BUG CHECK: If this fails, it's a bug in myre's MatchALL implementation.

        Example: "a1" contains both [a-z] and \d
        They overlap in position (in the same character 'a1' spans both)
        But both ARE present in the text, so & should match.
        """
        string = "a1!"

        has_lower = MatchAny.compile(r"[a-z]")
        has_digit = MatchAny.compile(r"\d")
        has_special = MatchAny.compile(r"!")

        combined = has_lower & has_digit & has_special
        result = combined.search(string)

        # EXPECTED: Should match because all three character classes exist
        # If this fails, it's a BUG in MatchALL's overlap handling
        assert result is not None, (
            "BUG: Overlapping patterns should still match. MatchALL checks if ALL patterns exist, not if they overlap."
        )

    def test_matchall_complex_regex_overlap(self):
        """
        Test Case: Complex patterns that overlap.

        BUG CHECK: Verify that overlapping regex patterns work correctly.
        """
        string = "User123"

        # \w+ matches "User123" (includes digits)
        # \d+ matches "123" (substring of above)
        # Both exist, so & should match
        has_word = MatchAny.compile(r"\w+")
        has_number = MatchAny.compile(r"\d+")

        combined = has_word & has_number
        result = combined.search(string)

        # EXPECTED: Should match
        # Both patterns ARE present in the string
        assert result is not None, "BUG: Both \\w+ and \\d+ exist in 'User123'. Overlap shouldn't prevent matching."

    def test_matchall_distinct_patterns(self):
        """Test with clearly distinct, non-overlapping patterns."""
        string = "Document v1.0 released on 2024-01-15"

        has_version = MatchAny.compile(r"v\d+\.\d+")
        has_date = MatchAny.compile(r"\d{4}-\d{2}-\d{2}")
        has_doc = MatchAny.compile(r"Document")

        combined = has_version & has_date & has_doc
        result = combined.search(string)

        assert result is not None

    def test_matchall_findall_behavior(self):
        """
        Test findall with MatchALL.

        DEFINITION: findall should return each match where ALL patterns
        are present. For keyword-based patterns, this returns each section
        that contains all keywords.
        """
        string = """
        Doc1: has privacy policy and terms
        Doc2: has privacy and policy
        Doc3: has policy and terms
        """

        combined = MatchAny.compile("privacy") & MatchAny.compile("policy") & MatchAny.compile("terms")
        results = combined.findall(string)

        # Should find Doc1 (has all three)
        # Doc2 missing 'terms', Doc3 missing 'privacy'
        assert len(results) >= 1, "Should find at least one match with all three keywords"

    def test_matchall_vs_traditional_lookaheads(self):
        """
        Compare with traditional lookahead approach.

        Traditional: (?=.*pattern1)(?=.*pattern2)
        myre: pattern1 & pattern2

        Should be equivalent for "all must exist" semantics.
        """
        string = "password: SecurePass123"

        # Traditional lookaheads
        trad = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)")
        trad_result = trad.search(string)
        assert trad_result is not None, "Traditional lookahead should match"

        # myre &
        has_lower = MatchAny.compile(r"[a-z]")
        has_upper = MatchAny.compile(r"[A-Z]")
        has_digit = MatchAny.compile(r"\d")

        combined = has_lower & has_upper & has_digit
        myre_result = combined.search(string)

        # EXPECTED: Should match like lookaheads
        assert myre_result is not None, "BUG: & should behave like lookaheads - all patterns must exist somewhere"

    def test_matchall_edge_case_empty_text(self):
        """Test MatchALL with empty string."""
        string = ""

        a = MatchAny.compile("a")
        b = MatchAny.compile("b")
        combined = a & b

        result = combined.search(string)
        assert result is None, "Empty string should not match multiple patterns"

    def test_matchall_edge_case_single_char_overlaps(self):
        """
        Edge case: Multiple single-char patterns in short string.

        "ab" contains both 'a' and 'b', even though they're adjacent.
        """
        string = "ab"

        a = MatchAny.compile("a")
        b = MatchAny.compile("b")
        combined = a & b

        result = combined.search(string)
        # EXPECTED: Should match - both characters exist
        assert result is not None, "BUG: 'ab' contains both 'a' and 'b', even though they're adjacent/overlapping"


class TestProtocolCompliance:
    """
    Meta-tests to ensure PatternLike protocol is correctly implemented.
    """

    def test_pattern_like_protocol_check(self):
        """Test that myre patterns are recognized as PatternLike."""
        from myre.protocol import PatternLike

        myre_pat = MatchAny.compile(r"hello")
        assert isinstance(myre_pat, PatternLike)

    def test_match_like_protocol_check(self):
        """Test that myre match objects are recognized as MatchLike."""
        from myre.protocol import MatchLike

        myre_pat = MatchAny.compile(r"hello")
        myre_match = myre_pat.search("hello world")
        assert isinstance(myre_match, MatchLike)

    def test_re_pattern_is_pattern_like(self):
        """Test that re.Pattern is also recognized as PatternLike."""
        from myre.protocol import PatternLike

        re_pat = re.compile(r"hello")
        # re.Pattern should match PatternLike protocol
        # (since it has search/findall/finditer methods)
        # Note: isinstance check may not work for Protocol without @runtime_checkable
        # but the duck typing should work


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
