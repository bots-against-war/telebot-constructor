import collections
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend/src"
CYRILLIC_LOWER = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
CYRILLIC_UPPPER = CYRILLIC_LOWER.upper()
CYRILLIC = set(CYRILLIC_LOWER + CYRILLIC_UPPPER)


queue = collections.deque[Path]()
queue.append(FRONTEND_SRC)
unlocalized: list[tuple[Path, int]] = []
while True:
    try:
        path = queue.popleft()
    except Exception:
        break

    if path.name.startswith("."):
        continue
    if path.is_dir():
        for subpath in path.iterdir():
            queue.append(subpath)
    else:
        with open(path, "r") as f:
            for lineno, line in enumerate(f):
                if set(line) & CYRILLIC:
                    unlocalized.append((path, lineno))
                    break

for path, lineno in sorted(unlocalized, key=lambda p: p[0]):
    print(f"{path.relative_to(PROJECT_ROOT)}:{lineno + 1}")

if unlocalized:
    sys.exit(1)
