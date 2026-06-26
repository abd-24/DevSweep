#Responsible for scoring each candidate and returning a confidence label.
#No detection, no deletion — just scoring.


from pathlib import Path
from models.candidate import Candidate

BLACKLISTED_NAMES = {
    ".env", ".env.local", ".env.production",
    "secrets.json", "credentials.json",
    "id_rsa", "id_ed25519",
}

NEVER_AUTOSELECT = {
    # semantically dangerous folder names
    "assets", "photos", "datasets",
    "documents", "data", "media",
    "uploads", "backup",
}

USER_EXTENSIONS = {
    # compiled languages
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".kt", ".cs", ".go", ".rb",
    ".php", ".swift", ".rs",
    
    # systems languages
    ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",
    
    # web source files
    ".html", ".css", ".scss", ".sass", ".vue",
    
    # config/build — debatable but safer to keep
    ".toml",
}

UNSAFE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp",
    ".pdf", ".doc", ".docx", ".ppt", ".pptx",
    ".xls", ".xlsx", ".zip", ".rar", ".7z",
}

def _load_gitignore(path: Path) -> set[str]:
    """Collect gitignore patterns from the candidate path up to the filesystem root."""
    patterns: set[str] = set()
    start = path if path.is_dir() else path.parent

    for parent in [start, *start.parents]:
        try:
            gitignore_path = parent / ".gitignore"
        except TypeError:
            continue
        if not gitignore_path.is_file():
            continue

        try:
            for raw_line in gitignore_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith("!"):
                    continue
                line = line.rstrip("/")
                line = line.lstrip("/")
                if line:
                    patterns.add(line)
        except OSError:
            continue

    return patterns


def _scan_contents(path: Path) -> tuple[bool, bool]:
    """
    Returns (has_user_files, has_unsafe_files).
    Stops as soon as both are found — no need to scan everything.
    """
    target = path if path.is_dir() else path.parent
    has_user = False
    has_unsafe = False

    if not target.exists():
        return False, False

    for entry in target.rglob("*"):
        if not entry.is_file():
            continue
        suffix = entry.suffix.lower()
        if suffix in USER_EXTENSIONS:
            has_user = True
        if suffix in UNSAFE_EXTENSIONS:
            has_unsafe = True
        if has_user and has_unsafe:
            break  # found both, no need to go further

    return has_user, has_unsafe


ENVIRONMENT_FOLDERS = {"venv", ".venv", "node_modules"}

def score(candidate: Candidate, root: Path) -> int:
    s = 0
    s += 40

    if candidate.ecosystem != "unknown":
        s += 20

    if candidate.path.name.lower() in _load_gitignore(candidate.path):
        s += 20

    # skip contents scan for known environment folders
    if candidate.path.name.lower() not in ENVIRONMENT_FOLDERS:
        has_user, has_unsafe = _scan_contents(candidate.path)
        if not has_user:
            s += 15
        if has_unsafe:
            s -= 60
        if has_user:
            s -= 50
    else:
        s += 15  # assume clean, no user data inside

    if candidate.ecosystem == "unknown":
        s -= 30

    # only penalize root level if ecosystem is unknown
    if candidate.path.parent == root and candidate.ecosystem == "unknown":
        s -= 20

    return max(0, min(100, s))


def classify(candidate: Candidate, root: Path) -> tuple[int, str]:
    """Classify the candidate into a safe action label."""
    if candidate.path.name.lower() in BLACKLISTED_NAMES:
        return 0, "ignore"

    score_value = score(candidate, root)

    if candidate.path.name.lower() in NEVER_AUTOSELECT or candidate.category == "reviewable":
        if score_value >= 50:
            return score_value, "review"
        return score_value, "ignore"

    if score_value >= 90:
        return score_value, "safe"
    if score_value >= 50:
        return score_value, "review"
    return score_value, "ignore"
