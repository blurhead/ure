import re
from dataclasses import dataclass


@dataclass
class OffsetMatch:
    _match: re.Match
    _start_offset: int
    _end_offset: int

    def start(self, group=0):
        return self._match.start(group) + self._start_offset

    def end(self, group=0):
        return self._match.end(group) + self._end_offset

    def span(self, group=0):
        return (self.start(group), self.end(group))

    def group(self, __group: str | int):
        return self._match.group(__group)

    def groups(self, default=None):
        return self._match.groups(default)

    def groupdict(self, default=None):
        return self._match.groupdict(default)

    def expand(self, template):
        return self._match.expand(template)

    # 特殊方法
    def __getitem__(self, group):
        return self._match[group]

    def __repr__(self):
        return f"OffsetMatch(start={self.start()}, end={self.end()}, match={self._match})"

    def __eq__(self, other):
        if isinstance(other, OffsetMatch):
            return (
                self._match == other._match
                and self._start_offset == other._start_offset
                and self._end_offset == other._end_offset
            )
        return False

    # 以下是re.Match对象可能还包含的其他方法
    def pos(self):
        return self._match.pos

    def endpos(self):
        return self._match.endpos

    def lastindex(self):
        return self._match.lastindex

    def lastgroup(self):
        return self._match.lastgroup

    def regs(self):
        return tuple((start + self._start_offset, end + self._end_offset) for start, end in self._match.regs)

    def re(self):
        return self._match.re

    def string(self):
        return self._match.string

    def __copy__(self):
        # 返回一个新的OffsetMatch对象，它复制了当前的匹配和偏移量信息
        return OffsetMatch(self._match, self._start_offset, self._end_offset)


if __name__ == "__main__":
    for matched in re.finditer(r"(\w+)", "Hello, World!"):
        offset_match = OffsetMatch(matched, 0, 3)
        print(matched.group(1), offset_match.group(1))
