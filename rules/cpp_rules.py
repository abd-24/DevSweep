# C/C++ project rules for DevSweep scanner.

SIGNATURES = [

    # Build system files
    "CMakeLists.txt",
    "Makefile",

    # Build configuration files
    "compile_commands.json",
    "CMakePresets.json",

    # Package manager files
    "conanfile.txt",
    "conanfile.py",

    # Meson build files
    "meson.build",

    # Ninja build files
    "build.ninja",
]

DELETABLES = [
    # Build directories
    "build",

    # CMake cache directories
    "cmake-build-debug",
    "cmake-build-release",

    # CMake generated files
    "CMakeFiles",
    "Testing",
]

REVIEWABLES = [
    "*.log",
    "*.tmp",
    "*.o",
    "*.obj",
    "*.d",
    "CMakeCache.txt",
    "cmake_install.cmake",
    "CTestTestfile.cmake",
]