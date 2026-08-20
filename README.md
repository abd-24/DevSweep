# DevSweep

> A desktop application that recursively scans developer workspaces, detects disposable artifacts, and safely cleans projects using a confidence-based classification system.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)

---

## What it does

Developer workspaces accumulate gigabytes of disposable artifacts — `__pycache__`, `node_modules/.cache`, `venv`, `dist`, `build` — that serve no purpose once a project is inactive. DevSweep finds them, scores them by confidence, and lets you clean them safely.

It never permanently deletes anything. Everything goes to the OS recycle bin.

---

## Features

- **Recursive scanning** — traverses entire project trees, respects `.gitignore`
- **Ecosystem detection** — identifies Python, Node.js, Java, Rust, and C++ projects automatically
- **Confidence scoring** — each artifact is scored 0–100 based on ecosystem context, contents, and proximity to signature files
- **Three-band classification** — Safe (auto-selected), Review (manual), Ignore (hidden)
- **Safe deletion** — moves to OS recycle bin via `send2trash`, never `shutil.rmtree`
- **Dry run mode** — preview what would be deleted before committing
- **Auto-select** — one click to select all high-confidence artifacts
- **Scan reports** — timestamped JSON reports saved automatically on every scan

---

## Supported Ecosystems

| Ecosystem | Detected By | Artifacts Cleaned |
|-----------|-------------|-------------------|
| Python | `requirements.txt`, `pyproject.toml`, `setup.py` | `__pycache__`, `venv`, `.pytest_cache`, `dist`, `build` |
| Node.js | `package.json`, `yarn.lock` | `node_modules`, `dist`, `.next`, `.nuxt`, `.parcel-cache` |
| Java | `pom.xml`, `build.gradle` | `target`, `build`, `.gradle` |
| Rust | `Cargo.toml` | `target` |
| C++ | `CMakeLists.txt`, `Makefile` | `build`, `CMakeFiles`, `cmake-build-debug` |

---

## Installation

### Windows
Download `DevSweep.exe` from the [latest release](https://github.com/abd-24/DevSweep/releases) and run directly — no installation required.

### macOS
Download `DevSweep.app` from the [latest release](https://github.com/abd-24/DevSweep/releases), unzip, and run.

### From source
```bash
git clone https://github.com/abd-24/DevSweep.git
cd DevSweep
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main.py
```

---

## How it works

```
Browse folder
     ↓
Scanner traverses directory tree
     ↓
Detector matches folder names against ecosystem rules
     ↓
Classifier scores each candidate (0–100)
     ↓
UI displays results with confidence labels
     ↓
User selects → Dry Run or Delete
     ↓
send2trash moves to OS recycle bin
```

### Confidence scoring

Each candidate starts at 0 and accumulates score based on evidence:

```
Name matches deletion rules       +40
Ecosystem detected nearby         +20
Listed in .gitignore              +20
No user source files inside       +15

Contains images or documents      -60
Contains source code              -50
No ecosystem detected             -30
```

### Safety guarantees

- Sensitive files (`.env`, `id_rsa`, `credentials.json`) are blacklisted — score forced to 0
- Semantically dangerous folders (`assets`, `photos`, `datasets`) are never auto-selected
- Symbolic links are never followed or deleted
- Nothing is permanently deleted — OS recycle bin only

---

## Project structure

```
DevSweep/
  main.py
  scanner/
    scanner.py       ← recursive traversal
    detector.py      ← candidate detection
    classifier.py    ← confidence scoring
  rules/
    python_rules.py
    node_rules.py
    java_rules.py
    rust_rules.py
    cpp_rules.py
  services/
    file_service.py    ← size calculation
    recycle_service.py ← safe deletion
    report_service.py  ← JSON reports
  models/
    candidate.py
    report.py
  ui/
    main_window.py
    tree_widget.py
    dialogs.py
    styles.py
  tests/
    test_scanner.py
    test_classifier.py
    test_rules.py
```

---

## Running tests

```bash
python -m pytest tests/ -v
```

---

## Known limitations

- Projects without formal signature files (`requirements.txt`, `package.json` etc.) may show `unknown` ecosystem and lower confidence scores
- macOS build not yet available as a pre-built binary
- No restore functionality yet (deleted items recoverable from OS recycle bin manually)

---

## Built with

- [Python 3.12+](https://python.org)
- [PySide6](https://doc.qt.io/qtforpython/) — Qt for Python
- [send2trash](https://github.com/arsenetar/send2trash) — safe cross-platform deletion

---

## License

MIT — see [LICENSE](LICENSE)
