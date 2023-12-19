from __future__ import annotations

from typing import NamedTuple


class Version(NamedTuple):
    """
    Helper object for manipulating version strings.
    """

    major: int
    minor: int

    def __str__(self):
        return f"v{self.major}.{self.minor}"

    def format_major_version(self):
        return f"v{self.major}"

    @staticmethod
    def parse(version_str) -> Version:
        major, minor = [int(i) for i in version_str.lstrip("v").split(".")]
        return Version(major, minor)

    def increment_major(self) -> Version:
        return Version(self.major + 1, 0)

    def increment_minor(self) -> Version:
        return Version(self.major, self.minor + 1)
