import json
import os
import random
import time
from pathlib import Path

import requests  # type: ignore
from telebot_components.language import LanguageData


def translate_text(text: str, target: str, source: str):
    url = "https://translation.googleapis.com/language/translate/v2"

    params = {
        "q": text,
        "target": target,
        "source": source,
        "key": os.environ["GOOGLE_TRANSLATE_API_KEY"],
    }

    response = requests.post(url, params=params)
    if response.status_code == 200:
        result = response.json()
        return result["data"]["translations"][0]["translatedText"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


BASE_LANG = "en"
PREFILLED_MSGS_FILE = Path(__file__).parent.parent / "telebot_constructor/data/prefilled_messages.json"


def main() -> None:
    major_languages = [code for code in LanguageData.all().keys() if len(code) == 2]
    print(major_languages)
    prefilled_msgs = json.loads(PREFILLED_MSGS_FILE.read_text())
    keys: list[str] = list(prefilled_msgs.keys())
    try:
        for key in keys:
            print()
            print(f"Processing {key}...")
            translations: dict[str, str] = prefilled_msgs[key]
            base_text = translations.get("en")
            if not base_text:
                print(f"Base translation to {BASE_LANG} is not available, skipping")
                continue
            print(f"Base text: {base_text}")
            for lang in major_languages:
                if not translations.get(lang):
                    print(f"Translating {BASE_LANG} -> {lang}...")
                    try:
                        translated = translate_text(base_text, target=lang, source=BASE_LANG)
                        print(f"Translation: {translated}")
                        translations[lang] = translated
                        delay = random.random() * 0.5
                        time.sleep(delay)
                    except Exception as e:
                        print(f"Error translating to {lang}, skipping: {e}")
    finally:
        print("Saving...")
        PREFILLED_MSGS_FILE.write_text(json.dumps(prefilled_msgs, ensure_ascii=False, indent=2))
        print("Done")


if __name__ == "__main__":
    main()
