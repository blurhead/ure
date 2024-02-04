# myre

Another Way To Write Regular Expression.

## About

`myre` is a Python library that provides a way for human to create and use regular expressions.

## Installation

```bash
pip install myre
```

## Basic Concept
Currently, there are two class to use, `MatchAny` and `MatchALL`.

Each pattern support four operation: `&` `|` `^` `-`.

For example, we have two patterns, `patternA` and `patternB`,
- `patternA | patternB` means we can match `patternA` or `patternB`
- `patternA & patternB` means we must match `patternA` and `patternB` both
- `patternA ^ patternB` means we can match `patternA` but not `patternB`
- `patternA - patternB` means after using `patternB` to trim the origin string then we can match `patternA`


## Usage
- `MatchAny` is used to match any of multiple patterns

- `MatchALL` is used to match all of multiple patterns, if order is true, it will match these patterns in order

The detail could be found in tests/test_pattern