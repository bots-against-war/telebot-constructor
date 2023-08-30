"""Convert backend's pydantic types to JSON schema or validate that the existing JSON schema is up-to-date"""
import argparse
import json
import sys
from pathlib import Path

import dictdiffer  # type: ignore

from telebot_constructor.bot_config import BotConfig

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonschema-path", type=Path, default=Path(__file__).parent / "../../data/schema.json")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare the current schema with the one file and exit with error status if they differ",
    )

    args = parser.parse_args()

    current_schema = BotConfig.model_json_schema(mode="serialization")

    if not args.check:
        args.jsonschema_path.write_text(json.dumps(current_schema, ensure_ascii=False, indent=2))
    else:
        existing_schema = json.loads(args.jsonschema_path.read_text())
        if existing_schema == current_schema:
            sys.exit()
        diff = list(dictdiffer.diff(existing_schema, current_schema))
        print("JSON schema in the file is out of date, if you have updated Python data model, you must regenerate it")
        print("Diff:")
        print(json.dumps(diff, indent=4, ensure_ascii=False))
        sys.exit(1)
