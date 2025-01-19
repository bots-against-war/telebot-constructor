import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
FRONTEND_BUILD_DIR = ROOT_DIR / "frontend/dist"
LANDING_BUILD_DIR = ROOT_DIR / "landing/build"


def build_landing(base_path: str | None):
    print(f"Building landing page with {base_path}")
    shutil.rmtree(LANDING_BUILD_DIR, ignore_errors=True)

    vite2_cmd = ["npx", "vite", "build", "landing"]
    print("Running\n$ " + " ".join(vite2_cmd))
    env: dict[str, str] = os.environ.copy()
    if base_path:
        env["BASE_PATH"] = base_path
    subprocess.run(vite2_cmd, check=True, env=env)

    print("Copying landing build to main frontend build dir")
    for src in LANDING_BUILD_DIR.iterdir():
        dest_name = src.name if src.name != "index.html" else "landing.html"
        dest = FRONTEND_BUILD_DIR / dest_name
        print(f"Copying {src.relative_to(ROOT_DIR)} => {dest.relative_to(ROOT_DIR)}")
        if src.is_dir():
            shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(src, dest)
        else:
            dest.unlink(missing_ok=True)
            shutil.copy(src, dest)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=None, required=False)
    args = p.parse_args()
    build_landing(args.base)
