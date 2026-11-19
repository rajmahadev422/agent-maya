import os
import json

MODEL = os.environ.get("AGENT_MODEL", "gemma4:e4b")      # must support tool calling
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
WORKDIR = os.path.abspath("workspace")                 # the agent only touches this folder
os.makedirs(WORKDIR, exist_ok=True)

STATE = {"auto": False}        # auto = skip approval for file edits and run_python
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv"}
MAX_TOOL_CHARS = 8000
MAX_STEPS = 25
BLOCKED = ("sudo", "rm -rf /", "rm -rf ~", "mkfs", ":(){", "shutdown", "reboot", "dd if=")

DIM, CYAN, YELLOW, GREEN, RED, RESET = (
    "\033[2m", "\033[36m", "\033[33m", "\033[32m", "\033[31m", "\033[0m")


SESSION_FILE = os.path.abspath("maya/chats.json")

os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)

if not os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)