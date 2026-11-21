# DevSweep

**A desktop utility for detecting and safely cleaning disposable developer artifacts.**

DevSweep scans developer workspaces, identifies generated files and directories across multiple programming ecosystems, and classifies cleanup candidates using a confidence-based scoring system.

Instead of permanently deleting files, DevSweep uses the operating system's recycle-bin mechanism, giving you an opportunity to recover removed items.

[**Download DevSweep v1.2.0**](https://github.com/abd-24/DevSweep/releases/tag/v1.2.0) · [Source Code](https://github.com/abd-24/DevSweep) · [Report an Issue](https://github.com/abd-24/DevSweep/issues)

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![GUI](https://img.shields.io/badge/GUI-PySide6-green)
![Version](https://img.shields.io/badge/Version-1.2.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## Overview

Developer workspaces accumulate generated artifacts over time:

- Python caches and virtual environments
- Node.js dependencies and frontend build outputs
- Java build directories
- Rust compilation artifacts
- C/C++ build-system outputs

These files can consume substantial disk space without being necessary for everyday development.

DevSweep identifies potential cleanup candidates, evaluates them using project context, and presents them in a desktop interface where you can review, preview, and selectively clean them.

**The goal is simple: make developer workspace cleanup safer, more transparent, and less tedious.**

## Features

- **Multi-ecosystem detection** — identifies Python, Node.js, Java, Rust, and C/C++ project environments.
- **Iterative filesystem scanning** — uses `os.scandir()`-based traversal to efficiently explore large directory trees.
- **Confidence-based classification** — assigns each candidate a score from 0–100.
- **Three-level classification** — separates candidates into Safe, Review, and Ignore categories.
- **Background scanning** — performs scanning and candidate analysis in a separate `QThread` to keep the interface responsive.
- **Incremental results** — candidates are delivered to the interface as they are processed.
- **Background deletion** — moves selected items to the OS recycle bin without blocking the main interface.
- **Dry-run mode** — previews selected items and their estimated sizes before deletion.
- **Automatic selection** — selects candidates classified as Safe.
- **Cached size calculations** — calculates candidate sizes once and reuses the results throughout the interface and reporting pipeline.
- **JSON scan reports** — automatically saves timestamped reports containing candidate details, classifications, and sizes.

## Supported ecosystems

| Ecosystem | Project signatures | Detected cleanup artifacts |
|---|---|---|
| Python | `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile` | `__pycache__`, `venv`, `.venv`, `build`, `dist`, test and lint caches |
| Node.js | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` | `node_modules`, `dist`, `build`, `.next`, `.nuxt`, `.svelte-kit` |
| Java | `pom.xml`, `build.gradle`, `settings.gradle` | `target`, `build`, `out`, `.gradle`, coverage outputs |
| Rust | `Cargo.toml`, `Cargo.lock` | `target` |
| C/C++ | `CMakeLists.txt`, `Makefile`, `meson.build`, `build.ninja` | `build`, `CMakeFiles`, CMake build directories and generated outputs |

Detection is based on project signatures and configured artifact rules. When no matching project context is found, candidates may be classified under an `unknown` ecosystem.

## Performance

Performance was a major focus of the v1.2.0 development cycle.

The filesystem traversal and size-calculation pipeline was optimized using iterative `os.scandir()` operations. Candidate sizes are also calculated once and cached for subsequent UI operations and report generation.

### Local benchmark

Measured on the same developer workspace:

| Metric | Previous implementation | v1.2.0 performance branch |
|---|---:|---:|
| Directories scanned | 112 | 112 |
| Files scanned | 190 | 191 |
| Candidates detected | 25 | 25 |
| Scan | 0.02 s | 0.01 s |
| Detection | 0.04 s | 0.00 s* |
| Classification | 0.02 s | 0.02 s |
| Size calculation | 6.60 s | 1.32 s |
| **Total** | **6.68 s** | **1.35 s** |

**Approximately 4.95× faster overall** in this benchmark, with size calculation reduced by approximately 80%.

Total measured artifact size was approximately 3.91 GB in both runs. The small difference in file counts and byte totals may reflect filesystem changes between runs.

\*Detection time is rounded to two decimal places; it does not imply zero execution time.

*These are local benchmark results, not a guarantee of identical performance across different machines, storage devices, or project structures.*

## How it works

DevSweep follows a modular scanning and cleanup pipeline:

```text
          Select project directory
                    |
                    v
          Filesystem Scanner
          (iterative traversal)
                    |
                    v
          Ecosystem Detector
          (project signatures)
                    |
                    v
          Candidate Generator
                    |
                    v
          Confidence Classifier
                (0–100)
                    |
                    v
          Desktop Interface
                    |
             User selection
                    |
             +------+------+
             |             |
             v             v
          Dry Run        Delete
             |             |
             v             v
          Preview      Delete Worker
                           |
                           v
                     OS Recycle Bin
                           |
                           v
                    JSON Scan Report
```

### Confidence classification

Each candidate receives a score based on several signals:

| Signal | Score adjustment |
|---|---:|
| Name matches a configured artifact rule | +40 |
| Ecosystem detected in the project hierarchy | +20 |
| Candidate name appears in applicable `.gitignore` patterns | +20 |
| No user source files detected inside the candidate | +15 |
| Contains images or documents | -60 |
| Contains user source files | -50 |
| Ecosystem is unknown | -30 |
| Unknown ecosystem and candidate is at project root | -20 |

The score is bounded between 0 and 100.

The resulting classification is:

| Classification | Score | Behaviour |
|---|---:|---|
| Safe | 90–100 | Automatically selected |
| Review | 50–89 | Requires manual selection |
| Ignore | 0–49 | Not selected by default |

Certain names, including sensitive-file names and semantically important directories, receive additional protection through explicit rules.

**Important:** Confidence scores are heuristic estimates, not proof that a directory is disposable. Review candidates before deletion, especially when working with unfamiliar projects.

## Safety considerations

DevSweep is designed to make cleanup decisions more transparent.

- **Recycle-bin deletion:** selected items are passed through `send2trash` rather than being permanently removed using `shutil.rmtree`.
- **Sensitive-name blacklist:** configured names such as `.env`, `credentials.json`, and SSH private-key filenames are excluded from automatic selection.
- **Conservative classification:** directories such as `assets`, `datasets`, `photos`, and `uploads` are never automatically selected.
- **Symlink and junction handling:** filesystem scanning and size calculation skip symbolic links and junctions rather than following them.
- **Manual review:** candidates that do not meet the Safe threshold are not automatically selected.
- **Dry-run preview:** users can inspect the selected paths and estimated space savings before deletion.

The recycle bin and classification system reduce risk, but they do not replace reviewing the selected paths.

## Installation

### Windows — prebuilt executable

1. Visit the [DevSweep v1.2.0 release page](https://github.com/abd-24/DevSweep/releases/tag/v1.2.0).
2. Download `DevSweep.exe`.
3. Run the executable.

No separate Python installation is required for the packaged Windows build.

### Run from source

**Requirements:** Python 3.12 or later.

```bash
git clone https://github.com/abd-24/DevSweep.git
cd DevSweep

python -m venv venv
```

Activate the environment:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

Install dependencies and launch:

```bash
pip install -r requirements.txt
python main.py
```

The prebuilt release currently targets Windows. Running from source on other platforms may require platform-specific adjustments and has not been established as a supported packaged release.

## Project structure

```text
DevSweep/
│
├── main.py
│
├── scanner/
│   ├── scanner.py          # Filesystem traversal
│   ├── detector.py         # Ecosystem and candidate detection
│   ├── classifier.py       # Confidence scoring
│   └── scan_worker.py      # Background scanning worker
│
├── rules/
│   ├── python_rules.py
│   ├── node_rules.py
│   ├── java_rules.py
│   ├── rust_rules.py
│   └── cpp_rules.py
│
├── services/
│   ├── file_service.py     # File and directory size calculation
│   ├── recycle_service.py  # Recycle-bin operations
│   ├── delete_worker.py    # Background deletion worker
│   └── report_service.py   # JSON report generation
│
├── models/
│   ├── candidate.py
│   └── report.py
│
├── ui/
│   ├── main_window.py
│   ├── tree_widget.py
│   ├── dialogs.py
│   └── styles.py
│
├── tests/
│   ├── test_scanner.py
│   ├── test_classifier.py
│   └── test_rules.py
│
├── requirements.txt
└── README.md
```

## Scan reports

After a successful scan, DevSweep automatically generates a timestamped JSON report inside the `reports/` directory.

Reports contain:

- Scan timestamp and root directory
- Total candidate count
- Total estimated reclaimable size
- Candidate paths and detected ecosystems
- Confidence scores and classifications
- Estimated size of each candidate

These reports provide a record of scan results without requiring users to manually export information.

## Running tests

Install the project dependencies, then run:

```bash
python -m pytest tests/ -v
```

## Known limitations

- Ecosystem detection depends on configured project signatures. Projects without recognizable signatures may be classified as `unknown`.
- Confidence classification is heuristic and cannot guarantee that every detected artifact is safe to remove.
- The prebuilt executable is currently available for Windows only.
- There is no dedicated restore feature inside DevSweep. Items moved to the recycle bin must be restored through the operating system.
- Scan reports are stored locally in the `reports/` directory.
- Filesystem changes during a scan can affect reported sizes and results.

## Built with

- [Python](https://www.python.org/) — application logic
- [PySide6](https://doc.qt.io/qtforpython/) — desktop interface
- [Send2Trash](https://github.com/arsenetar/send2trash) — recycle-bin integration
- [pytest](https://pytest.org/) — testing

## Contributing

Contributions, bug reports, and suggestions are welcome.

If you encounter an issue:

1. Check the existing [GitHub Issues](https://github.com/abd-24/DevSweep/issues).
2. Open a new issue with a description of the problem.
3. Include reproduction steps, relevant logs, and your operating system where possible.

For code contributions, fork the repository, create a feature branch, and submit a pull request.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

**DevSweep — Clean workspaces. Keep control.**
