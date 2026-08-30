from pathlib import Path
import subprocess

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path("/workspaces/Family_beacon").resolve()

BLOCKED_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}

BLOCKED_DIRECTORIES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
}

BLOCKED_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}


mcp = FastMCP("family-beacon")


def safe_path(relative_path: str) -> Path:
    path = (PROJECT_ROOT / relative_path).resolve()

    try:
        path.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError("Access outside Family_beacon is forbidden")

    if path.name in BLOCKED_NAMES:
        raise ValueError("Access to environment files is forbidden")

    if any(part in BLOCKED_DIRECTORIES for part in path.parts):
        raise ValueError("Access to protected directory is forbidden")

    if path.suffix.lower() in BLOCKED_SUFFIXES:
        raise ValueError("Access to key/certificate files is forbidden")

    return path


@mcp.tool()
def list_files(path: str = ".") -> str:
    """List files and directories inside the Family_beacon project."""
    target = safe_path(path)

    if not target.exists():
        raise ValueError("Path does not exist")

    if not target.is_dir():
        raise ValueError("Path is not a directory")

    entries = []

    for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if item.name in BLOCKED_NAMES:
            continue

        if item.name in BLOCKED_DIRECTORIES:
            continue

        if item.suffix.lower() in BLOCKED_SUFFIXES:
            continue

        relative = item.relative_to(PROJECT_ROOT)

        if item.is_dir():
            entries.append(f"{relative}/")
        else:
            entries.append(str(relative))

    return "\n".join(entries)


@mcp.tool()
def read_file(path: str) -> str:
    """Read a text file from the Family_beacon project."""
    target = safe_path(path)

    if not target.exists():
        raise ValueError("File does not exist")

    if not target.is_file():
        raise ValueError("Path is not a file")

    return target.read_text(encoding="utf-8")


@mcp.tool()
def search_files(query: str, path: str = ".") -> str:
    """Search text inside project files."""
    target = safe_path(path)

    if not target.exists():
        raise ValueError("Search path does not exist")

    results = []

    for file_path in target.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.name in BLOCKED_NAMES:
            continue

        if any(part in BLOCKED_DIRECTORIES for part in file_path.parts):
            continue

        if file_path.suffix.lower() in BLOCKED_SUFFIXES:
            continue

        if ".git" in file_path.parts:
            continue

        try:
            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            continue

        for line_number, line in enumerate(text.splitlines(), 1):
            if query.lower() in line.lower():
                relative = file_path.relative_to(PROJECT_ROOT)
                results.append(
                    f"{relative}:{line_number}: {line}"
                )

    if not results:
        return "NO RESULTS"

    return "\n".join(results)


@mcp.tool()
def git_status() -> str:
    """Return git status for Family_beacon."""
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.stdout or "WORKTREE CLEAN"


@mcp.tool()
def git_diff() -> str:
    """Return the current git diff."""
    result = subprocess.run(
        ["git", "diff", "--"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.stdout or "NO UNCOMMITTED DIFF"


@mcp.tool()
def git_log(limit: int = 10) -> str:
    """Return recent git commits."""
    limit = max(1, min(limit, 50))

    result = subprocess.run(
        ["git", "log", f"-{limit}", "--oneline"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.stdout or "NO COMMITS"


if __name__ == "__main__":
    mcp.run()
