# NodeJS project rules for DevSweep scanner.
SIGNATURES = [
    # NodeJS package files
    "package.json",
    "package-lock.json",

    # Config and metadata files
    "eslint.config.js",
    ".eslintignore",
    ".prettierrc",
    ".prettierignore",
    "tsconfig.json",

    # NodeJS lock files
    "yarn.lock",
    "pnpm-lock.yaml",
]

DELETABLES = [
    # NodeJS build and distribution directories
    "dist",
    "build",
    
    # NodeJS test and coverage directories
    ".nyc_output",
    "coverage",
    
    # NodeJS cache directories
    "node_modules",

    #Frontend build files
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".parcel-cache",
]

REVIEWABLES = [
    ".log",
    ".tmp",
    "npm-debug.log",
    "yarn-error.log",
    ".eslintcache",
    ".stylelintcache",
]