import atexit
import os
import shutil
import subprocess
from pathlib import Path

# when constructor app is hosted within a larger web application, this base path will be used
BASE_PATH = "/constructor"


def print_cmd(cmd: list[str]) -> None:
    print("Running\n$ " + " ".join(cmd))


delimiter = "\n" + "=" * 30 + "\n"


print("Determining version from GIT_TAG_NAME env var")
version = os.environ.get("GIT_TAG_NAME", "development")
print(f"Package version: {version!r}")


print(delimiter)
print("Building frontend static files")
vite_cmd = ["npx", "vite", "build", "frontend", "--base", BASE_PATH]
print_cmd(vite_cmd)
subprocess.run(vite_cmd, env={"GIT_COMMIT_ID": version, **os.environ}, check=True)


print(delimiter)
print("Copying build artifacts to Python package")
target_dir = "telebot_constructor/static"
shutil.rmtree(target_dir, ignore_errors=True)
shutil.copytree("frontend/dist", target_dir)


print(delimiter)
print("Setting base path in backend Python code")
build_time_config_file = Path("telebot_constructor/build_time_config.py")
build_time_config_body = build_time_config_file.read_text()
atexit.register(lambda: build_time_config_file.write_text(build_time_config_body))
build_time_config_body_preprocessed = build_time_config_body.replace('BASE_PATH = ""', f'BASE_PATH = "{BASE_PATH}"')
build_time_config_file.write_text(build_time_config_body_preprocessed)


print(delimiter)
print("Building final package")
poetry_cmd = ["poetry", "build"]
print_cmd(poetry_cmd)
subprocess.run(poetry_cmd, check=True)


print(delimiter)
print("See ya")
