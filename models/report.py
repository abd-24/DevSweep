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
    # store root as a string for easier JSON serialization
    root_path: str
    total_candidates: int
    total_reclaimable_size: int
    safe: list[dict] = field(default_factory=list)
    review: list[dict] = field(default_factory=list)
    ignore: list[dict] = field(default_factory=list)
