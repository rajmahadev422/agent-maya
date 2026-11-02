from pathlib import Path
import json

from utils.config import MAYA_DIR

# Maya internal data directory
DATA_DIR = MAYA_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_next_file():
    files = [
        int(file.stem)
        for file in DATA_DIR.glob("*.json")
        if file.stem.isdigit()
    ]

    next_id = max(files, default=0) + 1
    return DATA_DIR / f"{next_id}.json"


def save_messages(messages):
    file_path = get_next_file()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            messages,
            f,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    print(f"Chat history saved: {file_path}")


def load_messages(system_prompt, file_path=None):
    if file_path is None:
        return [{"role": "system", "content": system_prompt}]

    file_path = Path(file_path)

    if not file_path.is_absolute():
        file_path = DATA_DIR / file_path

    if not file_path.exists():
        return [{"role": "system", "content": system_prompt}]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        messages = [
            msg for msg in messages
            if msg.get("role") != "system"
        ]

        return [
            {"role": "system", "content": system_prompt},
            *messages
        ]

    except (json.JSONDecodeError, OSError) as e:
        print("Load error:", e)
        return [{"role": "system", "content": system_prompt}]