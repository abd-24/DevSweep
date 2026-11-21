# Detect candidate files/folders.
from pathlib import Path
from scanner.scanner import ScanResult
from rules import python_rules, node_rules, java_rules, rust_rules, cpp_rules
from models.candidate import Candidate
import os
from functools import lru_cache

ECOSYSTEM_RULES = [
    ("python", python_rules),
    ("node",   node_rules),
    ("java",   java_rules),
    ("rust",   rust_rules),
    ("cpp",    cpp_rules),
]

@lru_cache(maxsize=None)
def _ecosystems_in_dir(directory: Path) -> tuple[str, ...]:
    """Which ecosystems have a signature file directly inside this folder?
    The result is cached, so each folder is only ever listed once."""
    try:
        with os.scandir(directory) as entries:
            names = {e.name for e in entries if e.is_file()}
    except OSError:
        return ()
    return tuple(
        ecosystem
        for ecosystem, rules in ECOSYSTEM_RULES
        if any(sig in names for sig in rules.SIGNATURES)
    )
def find_ecosystems(path: Path) -> list[str]:
    for parent in path.parents:
        found = _ecosystems_in_dir(parent)
        if found:
            return list(found)      # nearest level wins, same as before
    return ["unknown"]

ALL_DELETABLES = set()
ALL_REVIEWABLES = set()

for ecosystem, rules in ECOSYSTEM_RULES:
    ALL_DELETABLES.update(rules.DELETABLES)
    ALL_REVIEWABLES.update(rules.REVIEWABLES)

def detect_candidates(scan_result: ScanResult):
    """
    Detects the scanned files and folders into candidates based on ecosystem rules.
    Returns a list of Candidate objects.
    """
    _ecosystems_in_dir.cache_clear()   # forget old answers; files may have changed since the last scan
    candidates = []
   
    for folder_path in scan_result.folders:
        if folder_path.name in ALL_DELETABLES:
            detected = find_ecosystems(folder_path)
            candidates.append(Candidate(
                path=folder_path,
                ecosystems=detected,
                category="deletable",
                matched_rule=folder_path.name
            ))

    for file_path in scan_result.files:
        if file_path.name in ALL_REVIEWABLES:
            detected = find_ecosystems(file_path)
            candidates.append(Candidate(
                path=file_path,
                ecosystems=detected,
                category="reviewable",
                matched_rule=file_path.name
            ))

    return candidates