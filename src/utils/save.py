import json

from src.config import SESSION_FILE

def save_chat(messages):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


def load_chat():
    try:
        with open(SESSION_FILE, encoding="utf-8") as f:
            messages = json.load(f)
            
        return messages
    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        return None