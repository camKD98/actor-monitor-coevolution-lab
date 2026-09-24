import platform
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=False,
        text=True,
    )


def collect_provenance() -> dict[str, object]:
    repo = Path(__file__).resolve().parents[2]
    revision = _git(repo, "rev-parse", "HEAD")
    unstaged = _git(repo, "diff", "--quiet")
    staged = _git(repo, "diff", "--cached", "--quiet")
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": revision.stdout.strip() if revision.returncode == 0 else None,
        "tracked_tree_dirty": unstaged.returncode != 0 or staged.returncode != 0,
        "command": shlex.join(sys.argv),
        "working_directory": str(Path.cwd()),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": {
            package: version(package)
            for package in ("numpy", "torch", "pytest", "ruff")
        },
    }
