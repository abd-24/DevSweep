"""
services/report_service.py

Generate and save scan reports in JSON format. 
The report includes classified candidates, their scores, and metadata about the scan.
"""

import json
import dataclasses
from datetime import datetime
from pathlib import Path
from models.candidate import Candidate
from services.file_service import get_size
from models.report import ScanReport

def generate_scan_report(
    candidates: list[Candidate],
    scores: dict[Path, tuple[int, str]],
    root: Path
) -> ScanReport:
    """
    Build a scan report dict from classified candidates.
    
    Args:
        candidates: list of Candidate objects from detector
        scores:     dict mapping candidate.path → (score, label)
        root:       the scanned root path
    """
    safe = []
    review = []
    ignore = []
    total_reclaimable = 0

    for candidate in candidates:
        score, label = scores[candidate.path]
        size = get_size(candidate.path)
        
        entry = {
            "path": str(candidate.path),
            "ecosystems": candidate.ecosystems,
            "score": score,
            "size": size,
        }

        if label == "safe":
            safe.append(entry)
            total_reclaimable += size
        elif label == "review":
            review.append(entry)
        else:
            ignore.append(entry)

    return ScanReport(
        timestamp=datetime.now().isoformat(),
        root_path=str(root),
        total_candidates=len(candidates),
        total_reclaimable_size=total_reclaimable,
        safe=safe,
        review=review,
        ignore=ignore,
    )


def save_report(report: ScanReport, path: Path) -> None:
    """
    Save a report dict to a JSON file.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(report), f, indent=4, default=str)
    except OSError as e:
        raise OSError(f"Failed to save report to {path}") from e
    
def cleanup_reports(reports_dir: Path, keep: int = 10) -> None:
    """Keep only the most recent N reports, delete the rest."""
    reports = sorted(reports_dir.glob("scan_*.json"))
    for old in reports[:-keep]:
        old.unlink()