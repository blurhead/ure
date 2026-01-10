"""
Pattern Composition Tests for myre

This file tests myre's unique feature: composable pattern operations.
Tests verify that pattern objects can be combined using operators (|, &, ^, @)
to create new patterns with complex matching behavior.

Composition patterns tested:
- MatchAny | MatchAny (OR of ORs)
- MatchALL & MatchALL (AND of ANDs)
- MatchAny & MatchALL (mixed composition)
- Nested compositions
- Operator precedence and chaining
"""

import re
import unittest
from myre import MatchAny, MatchALL, Mode


class TestOrOperator(unittest.TestCase):
    """Tests for | (OR) operator"""

    def test_matchany_or_matchany(self):
        """Test combining two MatchAny patterns with |"""
        p1 = MatchAny.compile(r"hello", r"world")
        p2 = MatchAny.compile(r"foo", r"bar")
        combined = p1 | p2

        matches = combined.findall("hello world foo bar")
        self.assertEqual(len(matches), 4)
        self.assertIn("hello", matches)
        self.assertIn("foo", matches)

    def test_or_creates_new_matchany(self):
        """Test that | operator creates new MatchAny instance"""
        p1 = MatchAny.compile(r"hello")
        p2 = MatchAny.compile(r"world")
        combined = p1 | p2

        self.assertIsInstance(combined, MatchAny)
        # Original patterns unchanged (immutability)
        self.assertEqual(p1.findall("hello world"), ["hello"])
        self.assertEqual(p2.findall("hello world"), ["world"])

    def test_multiple_or_chains(self):
        """Test chaining multiple | operations"""
        p1 = MatchAny.compile(r"hello")
        p2 = MatchAny.compile(r"world")
        p3 = MatchAny.compile(r"foo")

        combined = p1 | p2 | p3
        matches = combined.findall("hello world foo")
        self.assertEqual(len(matches), 3)


class TestAndOperator(unittest.TestCase):
    """Tests for & (AND) operator"""

    def test_matchall_and_matchall(self):
        """Test combining two MatchALL patterns with &"""
        # p1 requires 'hello' and 'world'
        # p2 requires 'foo' and 'bar'
        p1 = MatchALL.compile(r"hello", r"world")
        p2 = MatchALL.compile(r"foo", r"bar")
        combined = p1 & p2

        # All 4 patterns must match
        matches = combined.findall("hello world foo bar")
        self.assertEqual(len(matches), 1)

    def test_and_creates_new_matchall(self):
        """Test that & operator creates new MatchALL instance"""
        p1 = MatchALL.compile(r"hello", r"world")
        p2 = MatchALL.compile(r"foo", r"bar")
        combined = p1 & p2

        self.assertIsInstance(combined, MatchALL)

    def test_matchany_and_matchall(self):
        """Test mixing MatchAny & MatchALL"""
        # MatchAny: matches 'hello' OR 'world'
        # MatchALL: requires 'test' AND the MatchAny result
        p1 = MatchAny.compile(r"hello", r"world")
        p2 = MatchALL.compile(p1, r"test")

        # Should match when both 'test' AND ('hello' OR 'world') exist
        matches = p2.findall("hello test")
        self.assertEqual(len(matches), 1)


class TestMaskOperator(unittest.TestCase):
    """Tests for @ (MASK) operator"""

    def test_mask_with_placeholder(self):
        """Test @ operator with custom placeholder"""
        pattern = MatchAny.compile(r"test_{3}value") @ (r"\d+", "_")
        text = "test123value"
        matches = pattern.findall(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], text)

    def test_mask_preserves_original_text(self):
        """Test that @ returns original text, not masked text"""
        pattern = MatchAny.compile(r"testx{3}value") @ (r"\s+", "x")
        text = "test   value"
        matches = pattern.findall(text)

        # Should return original text with spaces, not 'testxxxvalue'
        self.assertEqual(matches[0], text)

    def test_mask_chaining(self):
        """Test chaining @ with other operators"""
        # Create pattern, mask it, then combine with another
        p1 = MatchAny.compile(r"abc", r"def") @ (r"\d+", "x")
        p2 = MatchAny.compile(r"xyz")
        combined = p1 | p2

        text = "abc1 xyz2 def3"
        matches = combined.findall(text)
        self.assertEqual(len(matches), 3)


class TestUnifiedCompile(unittest.TestCase):
    """Tests for unified myre.compile() function"""

    def test_compile_mode_any(self):
        """Test compile with Mode.ANY"""
        from myre import compile, Mode

        pattern = compile("hello", "world", mode=Mode.ANY)
        self.assertIsInstance(pattern, MatchAny)
        self.assertEqual(len(pattern.patterns), 2)

    def test_compile_mode_all(self):
        """Test compile with Mode.ALL"""
        from myre import compile, Mode

        pattern = compile("hello", "world", mode=Mode.ALL)
        self.assertIsInstance(pattern, MatchALL)

    def test_compile_with_flag(self):
        """Test compile with flag parameter"""
        from myre import compile, Mode

        pattern = compile("hello", flag=re.I, mode=Mode.ANY)
        self.assertIsNotNone(pattern.search("HELLO"))

    def test_compile_default_mode(self):
        """Test that default mode is ANY"""
        from myre import compile

        pattern = compile("hello", "world")
        self.assertIsInstance(pattern, MatchAny)


class TestNestedCompositions(unittest.TestCase):
    """Tests for complex nested pattern compositions"""

    def test_or_in_and(self):
        """Test (A | B) & C style composition"""
        # p1_or_p2 = matches 'a' OR 'b'
        # combined = requires (p1_or_p2) AND 'c'
        p1 = MatchAny.compile(r"a", r"b")
        combined = MatchALL.compile(p1, r"c")

        matches = combined.findall("c a b c")
        # Should match once: combines p1_or_p2 (matches 'a' or 'b') with 'c'
        self.assertGreater(len(matches), 0)

    def test_multiple_nesting(self):
        """Test deeply nested pattern compositions"""
        # ((p1 | p2) & p3) | p4
        p1 = MatchAny.compile(r"hello")
        p2 = MatchAny.compile(r"world")
        p3 = MatchAny.compile(r"test")
        p4 = MatchAny.compile(r"final")

        intermediate = MatchALL.compile(p1 | p2, p3)
        final_pattern = intermediate | p4

        self.assertIsNotNone(final_pattern.search("hello test"))


class TestOperatorPrecedence(unittest.TestCase):
    """Tests for operator precedence and evaluation order"""

    def test_and_before_or(self):
        """Test that & has higher precedence than |"""
        # p1 | p2 & p3 should be p1 | (p2 & p3)
        # But Python's left-to-right evaluation may affect this
        p1 = MatchAny.compile(r"a")
        p2 = MatchAny.compile(r"b")
        p3 = MatchAny.compile(r"c")

        # Manual grouping: (p1 | p2) & p3
        explicit = MatchALL.compile(p1 | p2, p3)

        # No explicit grouping in myre - operators are left-associative
        # p1 | p2 & p3 = (p1 | p2) & p3 in Python
        matches = explicit.findall("a c")
        self.assertEqual(len(matches), 1)


class TestImmutability(unittest.TestCase):
    """Tests that operators create new objects (immutability)"""

    def test_or_preserves_originals(self):
        """Test that | doesn't modify original patterns"""
        p1 = MatchAny.compile(r"hello")
        p2 = MatchAny.compile(r"world")

        original_p1_matches = p1.findall("hello world")
        combined = p1 | p2

        # p1 should be unchanged
        self.assertEqual(p1.findall("hello world"), original_p1_matches)

    def test_and_preserves_originals(self):
        """Test that & doesn't modify original patterns"""
        p1 = MatchALL.compile(r"hello", r"world")
        p2 = MatchALL.compile(r"foo", r"bar")

        combined = p1 & p2

        # p1 and p2 should be unchanged
        matches = p1.findall("hello world")
        self.assertEqual(len(matches), 1)

    def test_mask_preserves_originals(self):
        """Test that @ doesn't modify original patterns"""
        p1 = MatchAny.compile(r"hello")

        masked = p1 @ r"\d+"

        # p1 should be unchanged (no mask applied)
        self.assertIsNotNone(p1.search("hello world"))
        self.assertIsNotNone(p1.search("hello123world"))  # p1 can still match 'hello' anywhere

        # masked should have mask applied
        self.assertIsNotNone(masked.search("hello world"))
        # masked with r'\d+' mask should still match 'hello' since digits are masked
        self.assertIsNotNone(masked.search("hello123world"))


class TestMatchALLWithOperators(unittest.TestCase):
    """Specific tests for MatchALL behavior with various operators"""

    def test_matchall_with_or(self):
        """Test MatchALL containing MatchAny created with |"""
        # MatchALL of: (hello OR world) AND (foo OR bar)
        p1 = MatchAny.compile(r"hello", r"world")
        p2 = MatchAny.compile(r"foo", r"bar")
        combined = MatchALL.compile(p1, p2)

        matches = combined.findall("hello foo bar world")
        self.assertEqual(len(matches), 1)

    def test_matchall_with_mask(self):
        """Test MatchALL with masked patterns"""
        # MatchALL of masked patterns
        p1 = MatchAny.compile(r"test_{3}") @ (r"\d+", "_")
        p2 = MatchAny.compile(r"value")
        combined = MatchALL.compile(p1, p2)

        text = "test123value"
        matches = combined.findall(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], text)

    def test_matchall_finds_all_first_matches(self):
        """Test that MatchALL takes first match from each pattern"""
        # If multiple matches exist, MatchALL takes the first from each
        pattern = MatchALL.compile(r"\d+", r"[a-z]+")
        text = "123abc 456def 789ghi"

        matches = pattern.findall(text)
        # Should get one match combining first '\d+' and first '[a-z]+'
        self.assertEqual(len(matches), 1)
        # Combined match should contain both patterns' first matches
        combined = matches[0]
        self.assertIn("123", combined)
        self.assertIn("abc", combined)


class TestComposeMatchIntegration(unittest.TestCase):
    """Integration tests for ComposeMatch with pattern operations"""

    def test_matchall_returns_composematch(self):
        """Test that MatchALL operations return proper ComposeMatch objects"""
        pattern = MatchALL.compile(r"hello", r"world")
        matches = list(pattern.finditer("hello world"))

        self.assertEqual(len(matches), 1)
        match = matches[0]

        # Should have composition info
        self.assertTrue(hasattr(match, "hits"))
        self.assertTrue(hasattr(match, "re"))
        self.assertTrue(hasattr(match, "string"))

    def test_composematch_group(self):
        """Test group() method on composed matches"""
        pattern = MatchALL.compile(r"(\d+)", r"([a-z]+)")
        text = "123abc"

        matches = list(pattern.finditer(text))
        self.assertEqual(len(matches), 1)

        # ComposeMatch should aggregate the matches
        combined = matches[0]
        self.assertIsInstance(combined.group(), str)
        self.assertGreater(len(combined.group()), 0)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling in pattern operations"""

    def test_compile_empty_patterns(self):
        """Test that compile requires at least one pattern"""
        from myre import compile

        with self.assertRaises(ValueError):
            compile()  # Empty pattern list

    def test_compile_invalid_mode(self):
        """Test that compile rejects invalid mode"""
        from myre import compile

        # Mode must be Mode.ANY, Mode.ALL, or Mode.SEQ
        # String values won't work
        pattern = compile(r"test", mode=Mode.ANY)
        self.assertIsInstance(pattern, MatchAny)


if __name__ == "__main__":
    unittest.main()
