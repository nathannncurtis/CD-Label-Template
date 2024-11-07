from cx_Freeze import setup, Executable
import sys

# Set base to "Console" to suppress GUI windows
base = "Console" if sys.platform == "win32" else None

# Define the executables
executables = [
    Executable("parse.py", base=base),
    Executable("main.py", base=base)
]

# Set up the build
setup(
    name="PDF to TDD Processor",
    version="1.0",
    description="Process PDFs and output .tdd files",
    executables=executables,
    options={
        "build_exe": {
            "include_files": [".config", "blank.tdd", "start.bat", "start.vbs"],
            "packages": ["os", "sys", "re", "subprocess", "fitz", "watchdog"],
            "excludes": ["tkinter"],  # Optional: excludes unused packages to minimize file size
        }
    }
)
