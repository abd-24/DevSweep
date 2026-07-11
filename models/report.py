"""
models/report.py

Represents the output of a full scan as a structured dataclass.
"""
from models.candidate import Candidate
from pathlib import Path
from dataclasses import dataclass, field
@dataclass
class ScanReport:
    timestamp: str
    root_path: Path
    total_candidates: int
    total_reclaimable: int
    safe: list[Candidate] = field(default_factory=list)
    review: list[Candidate] = field(default_factory=list)
    ignore: list[Candidate] = field(default_factory=list)
  