"""
Like poetry install, but for all open-ended dependencies locks them in
the lowest possible versions.
"""

import shutil
import subprocess
import time
from pathlib import Path

import toml  # type: ignore

PYPROJECT = Path("pyproject.toml")
if not PYPROJECT.exists():
    raise SystemExit("pyproject.toml file not found; make sure to run the script from project root")

LOCK_FILE = Path("poetry.lock")
if LOCK_FILE.exists():
    print("Removing lock file...")
    LOCK_FILE.unlink()
    print("Done")


PYPROJECT_BCK = Path("pyproject.toml.bck")
print(f"Backing up {PYPROJECT} to {PYPROJECT_BCK}")
shutil.copy(PYPROJECT, PYPROJECT_BCK)

try:
    pyproject = toml.loads(PYPROJECT.read_text())
    dependencies = pyproject["tool"]["poetry"]["dependencies"]
    pyproject["tool"]["poetry"]["dependencies"] = {
        key: value.removeprefix("^") if key != "python" else value for key, value in dependencies.items()
    }
    print(f"Saving temporary {PYPROJECT} with dependencies pinned at the lowest version")
    PYPROJECT.write_text(toml.dumps(pyproject))
    print(f"Installing...")
    subprocess.run(["poetry", "install"])
except Exception as e:
    raise SystemExit(f"Error: {e}")
finally:
    print(f"Restoring {PYPROJECT}...")
    shutil.copy(PYPROJECT_BCK, PYPROJECT)
    print("Removing backup...")
    PYPROJECT_BCK.unlink(missing_ok=True)
