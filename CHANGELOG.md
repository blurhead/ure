# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.8] - 2025-01-10

### Fixed
- Pre-commit hooks now use cross-platform `python -m` commands
  - Works on Windows, Linux, and macOS
  - Properly runs mypy and pytest in virtual environment
  - Migrated from Poetry to UV for dependency management

### Added
- `+` operator for sequence matching (`MatchSeq`)
  - `p1 + p2` matches patterns in sequential order
  - Simplifies creation of sequential patterns
- `/` operator for split matching (`SplitMatch`)
  - `p1 / p2` splits string by p2, then matches p1 in each segment
  - Returns matches with correct positions relative to original string
  - Supports multi-character delimiters and empty segments
- CI workflow for automated testing
  - Tests on Python 3.10, 3.11, 3.12, 3.13
  - Includes type checking (mypy) and linting (ruff)
- Comprehensive test suite
  - `test_re_compatibility.py`: 24 tests for stdlib re compatibility
  - `test_pattern_composition.py`: 26 tests for operator composition
  - `test_patternlike_protocol.py`: 58 tests for protocol compliance

### Changed
- Migrated from Poetry to UV for dependency management
  - Faster dependency resolution and installation
  - PEP 621 compliant `pyproject.toml` format
  - Using hatchling as build backend
- Updated documentation to use unified `myre.compile()` API
  - Replaced direct class usage with `Mode` enum
  - Added examples for new operators (`+`, `/`)

### Fixed
- Critical bug in `Masker.mask()` with `pos` parameter
  - Now preserves full string length with prefix and suffix
  - Fixes incorrect position calculation when `pos > 0`
  - Example: `search('abcabc', pos=1)` now correctly returns `(3, 6)` instead of `(2, 5)`
- Fixed `SplitMatch` implementation to use `finditer()` instead of `split()`
  - Accurately calculates segment positions based on delimiter matches
  - Properly handles edge cases (empty segments, multi-char delimiters)

## [0.0.7] - 2024-04-18

### Added
- `group()` and `groups()` methods support for `MatchLike` protocol, compatible with standard `re.Match`
- Improved documentation

### Changed
- Internal refactoring for better pattern matching compatibility

## [0.0.6] - 2024-02-04

### Added
- `group()` and `groups()` methods support for `MatchLike` protocol, compatible with standard `re.Match`
- Improved documentation

### Changed
- Internal refactoring for better pattern matching compatibility

## [0.0.6] - 2024-02-04

### Added
- `^` (XOR/EXCLUDE) operator for pattern exclusion
  - Allows matching patterns while excluding results containing deny patterns
  - Example: `pattern ^ deny` matches pattern but excludes if contains deny
- MatchALL support for ordered pattern matching
- Initial README documentation

### Fixed
- Error handling when using MatchALL with `order=True`

## [0.0.5] - 2024-01-28

### Added
- `MatchALL` pattern class
  - Requires all patterns to match somewhere in the search range
  - Returns combined match results from all patterns
  - Supports `&` operator for pattern composition

## [0.0.4] - 2024-01-20

### Added
- Preprocess workflow support for MatchAny
- Ability to clean/filter text before pattern matching

### Refactored
- Abstracted text cleaning process into dedicated class
- Simplified codebase architecture
- Added CI/CD workflow for publishing

### Fixed
- Poetry publish errors in CI pipeline

## [0.0.3] - 2024-01-17

### Added
- `ManyAny` pattern (early prototype)

## [0.0.2] - 2023-12-24

### Added
- Protocol-based type system (`PatternLike`, `MatchLike`)
- `_compile()` helper function for pattern compilation
- Type safety improvements with structural typing

## [0.0.1] - 2023-12-20

### Added
- Initial project release
- `MatchAny` pattern class with basic operators (`|`, `-`)
- Support for regex pattern composition
- Protocol-based polymorphism for pattern matching
- Position tracking for text preprocessing

---

## Version Summary

| Version | Date | Major Features |
|---------|------|----------------|
| 0.0.7 | 2024-04-18 | `group()`/`groups()` compatibility with re.Match |
| 0.0.6 | 2024-02-04 | `^` XOR operator, MatchALL ordering fixes |
| 0.0.5 | 2024-01-28 | MatchALL pattern class |
| 0.0.4 | 2024-01-20 | Text preprocessing, CI/CD pipeline |
| 0.0.3 | 2024-01-17 | ManyAny pattern prototype |
| 0.0.2 | 2023-12-24 | Protocol-based type system |
| 0.0.1 | 2023-12-20 | Initial release with MatchAny |
