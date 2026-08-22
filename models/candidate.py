# Represents a single artifact candidate found during scanning.
# Holds the path, ecosystem context, and category.

from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Candidate:
    """
    A folder or file flagged as a potential artifact.
    """
    path: Path
    ecosystems: list[str]   # e.g. ["python", "node"] or ["unknown"]
    category: str         # "deletable" or "reviewable"
    matched_rule: str     # the exact name that triggered the match e.g. "__pycache__"

    def __str__(self) -> str:
        return (
            f"[{self.category.upper()}] {self.path} "
            f"(ecosystem: {self.ecosystem}, rule: {self.matched_rule})"
        )