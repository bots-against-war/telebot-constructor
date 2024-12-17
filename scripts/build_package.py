import atexit
import os
import shutil
import subprocess
from pathlib import Path

# when constructor app is hosted within a larger web application, this base path will be used
base_path = "/constructor"


def print_cmd(cmd: list[str]) -> None:
    print("Running\n$ " + " ".join(cmd))


delimiter = "\n" + "=" * 30 + "\n"


print("Determining version from GIT_TAG_NAME env var")
version = os.environ.get("GIT_TAG_NAME", "development")
print(f"Package version: {version!r}")


print(delimiter)
print("Replacing base path in custom HTML files")
paths = [
    Path("frontend/public") / filename
    for filename in ["group_chat_auth_login.html", "landing.html", "telegram_auth_login.html"]
]
original_contents: list[str] = []
processed_contents: list[str] = []
for path in paths:
    content = path.read_text()
    original_contents.append(content)
    processed_contents.append(content.replace('const BASE_PATH = "";', f'const BASE_PATH = "{base_path}";'))
atexit.register(lambda: [path.write_text(original_content) for path, original_content in zip(paths, original_contents)])
for path, content in zip(paths, processed_contents):
    path.write_text(content)


print(delimiter)
print("Building frontend")
vite_cmd = ["npx", "vite", "build", "frontend", "--base", base_path]
print_cmd(vite_cmd)
subprocess.run(vite_cmd, env={"GIT_COMMIT_ID": version, **os.environ}, check=True)


print(delimiter)
print("Copying frontend build artifacts to the /static dir inside Python package")
target_dir = "telebot_constructor/static"
shutil.rmtree(target_dir, ignore_errors=True)
shutil.copytree("frontend/dist", target_dir)


print(delimiter)
print("Setting build-time configuration in backend Python code")
build_time_config_file = Path("telebot_constructor/build_time_config.py")
build_time_config_body = build_time_config_file.read_text()
atexit.register(lambda: build_time_config_file.write_text(build_time_config_body))
build_time_config_body_preprocessed = build_time_config_body.replace('BASE_PATH = ""', f'BASE_PATH = "{base_path}"')
build_time_config_body_preprocessed = build_time_config_body_preprocessed.replace(
    'VERSION = ""', f'VERSION = "{version}"'
)
build_time_config_file.write_text(build_time_config_body_preprocessed)


print(delimiter)
print("Building final package")
poetry_cmd = ["poetry", "build"]
print_cmd(poetry_cmd)
subprocess.run(poetry_cmd, check=True)


print(delimiter)
print("See ya!")
