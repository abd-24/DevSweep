# Java project rules for DevSweep scanner.
SIGNATURES = [
    
    # Java package files
    "pom.xml",
    "build.gradle",
    
    # Config and metadata files
    "settings.gradle",
    "gradle.properties",
    "settings.gradle.kts",
    
    # Java lock files
    "gradle.lockfile",
    
    # Java build files
    "build.gradle.kts",
]

DELETABLES = [
    # Java build and distribution directories
    "target",
    "build",
    "out",
    
    # Java test and coverage directories
    "test-output",
    "coverage",
    "jacoco",
    
    # Java cache directories
    ".gradle",
]

REVIEWABLES = [
    "*.log",
    "*.tmp",
    "*.class",
    "hs_err_pid*",
    ]