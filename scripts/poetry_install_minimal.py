"""
Like poetry install, but for all open-ended dependencies locks them in
the lowest possible versions.
"""

import shutil
import subprocess
from pathlib import Path

import toml  # type: ignore

PYPROJECT = Path("pyproject.toml")
if not PYPROJECT.exists():
    raise SystemExit("pyproject.toml file not found; make sure to run the script from project root")

LOCK_FILE = Path("poetry.lock")
LOCK_FILE_BCK = Path("poetry.lock.bck")
if LOCK_FILE.exists():
    print(f"Backing up {LOCK_FILE}")
    shutil.move(LOCK_FILE, LOCK_FILE_BCK)
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
    print("Installing...")
    subprocess.run(["poetry", "install"])
except Exception as e:
    raise SystemExit(f"Error: {e}")
finally:
    print(f"Restoring {PYPROJECT}...")
    shutil.move(PYPROJECT_BCK, PYPROJECT)
    print(f"Restoring {LOCK_FILE}")
    shutil.move(LOCK_FILE_BCK, LOCK_FILE)
