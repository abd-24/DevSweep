# Detect candidate files/folders.
from pathlib import Path
from scanner.scanner import ScanResult
from rules import python_rules, node_rules, java_rules, rust_rules, cpp_rules
from models.candidate import Candidate

ECOSYSTEM_RULES = [
    ("python", python_rules),
    ("node",   node_rules),
    ("java",   java_rules),
    ("rust",   rust_rules),
    ("cpp",    cpp_rules),
]

def find_ecosystem(path: Path) -> str:
    for parent in path.parents:
        try:
            files_here = {f.name for f in parent.iterdir() if f.is_file()}
        except PermissionError:
            continue
        for ecosystem, rules in ECOSYSTEM_RULES:
            if any(sig in files_here for sig in rules.SIGNATURES):
                return ecosystem
    return "unknown"

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
    candidates = []

    
   
    for folder_path in scan_result.folders:
        if folder_path.name in ALL_DELETABLES:
            detected = find_ecosystem(folder_path)
            candidates.append(Candidate(
                path=folder_path,
                ecosystem=detected,
                category="deletable",
                matched_rule=folder_path.name
            ))

    for file_path in scan_result.files:
        if file_path.name in ALL_REVIEWABLES:
            detected = find_ecosystem(file_path)
            candidates.append(Candidate(
                path=file_path,
                ecosystem=detected,
                category="reviewable",
                matched_rule=file_path.name
            ))

    return candidates