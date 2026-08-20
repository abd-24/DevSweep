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
    """
    Inspect the candidate's directory and its parents to determine the ecosystem.
    """
    # Check the candidate's containing directory first, then walk up parents
    start_dirs = [path if path.is_dir() else path.parent, *(path.parents)]
    for parent in start_dirs:
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
        # Reviewable rules may include extensions (".log") or exact file names.
        suffix = file_path.suffix.lower()
        name = file_path.name
        if name in ALL_REVIEWABLES or suffix in ALL_REVIEWABLES:
            detected = find_ecosystem(file_path)
            matched_rule = name if name in ALL_REVIEWABLES else suffix
            candidates.append(Candidate(
                path=file_path,
                ecosystem=detected,
                category="reviewable",
                matched_rule=matched_rule
            ))

    return candidates
