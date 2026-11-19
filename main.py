import json
import os
import urllib.error
import urllib.request

# ------------------------------------------------------------------ config
from src.config import (
    WORKDIR,
    YELLOW, GREEN, RED, RESET, CYAN,
    MAX_STEPS,
    MAX_TOOL_CHARS,
    MODEL,
    STATE,
    OLLAMA_URL,
    DIM
)
from src.tool import TOOL_SCHEMAS, TOOLS
from src.utils.helpers import (
    _git,
    short,
    confirm   
)

from src.utils.save import save_chat, load_chat

#============ SYSTEM PROMPT ===========

SYSTEM = """You are a coding agent working inside a workspace folder. Use the tools to
create, read, edit and run files.

Workflow rules:
- For multi-step tasks, call update_todo first to write a plan, and update it as you go.
- Use list_files, grep and read_file_lines to find code before editing. Read a file before editing it.
- Prefer edit_file over rewriting whole files.
- After changing code, run it or its tests and fix failures before finishing.
- Never print or hard-code API keys; read them with os.environ.
- Finish with a short summary of what changed."""



# ------------------------------------------------------------------ model streaming
def stream_chat(messages, think=True):
    """Stream one model turn, printing thinking and text live. Returns the full message."""
    body = json.dumps({"model": MODEL, "messages": messages, "tools": TOOL_SCHEMAS,
                       "stream": True, "think": think}).encode()
    req = urllib.request.Request(OLLAMA_URL, body, {"Content-Type": "application/json"})

    content, thinking, calls, mode = "", "", [], None
    try:
        resp = urllib.request.urlopen(req, timeout=300)
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        if think and "think" in err.lower():          # model has no thinking support
            return stream_chat(messages, think=False)
        raise RuntimeError(err)
    except urllib.error.URLError:
        raise RuntimeError("Cannot reach Ollama. Is it running? (ollama serve)")

    with resp:
        for line in resp:                              # one JSON object per line
            if not line.strip():
                continue
            msg = json.loads(line).get("message", {})

            if msg.get("thinking"):
                if mode != "think":
                    print(f"\n{DIM}💭 thinking\n", end="")
                    mode = "think"
                print(msg["thinking"], end="", flush=True)
                thinking += msg["thinking"]

            if msg.get("content"):
                if mode != "text":
                    print(f"{RESET}\n\n{GREEN}🤖 ", end="")
                    mode = "text"
                print(msg["content"], end="", flush=True)
                content += msg["content"]

            calls.extend(msg.get("tool_calls") or [])
    print(RESET)

    out = {"role": "assistant", "content": content}
    if thinking:
        out["thinking"] = thinking
    if calls:
        out["tool_calls"] = calls
    return out


# ------------------------------------------------------------------ agent internals
def checkpoint():
    """Commit the workspace so /undo can roll back. Returns commit hash or None."""
    try:
        if not os.path.isdir(os.path.join(WORKDIR, ".git")):
            _git("init")
        _git("add", "-A")
        _git("commit", "-m", "checkpoint", "--allow-empty")
        return _git("rev-parse", "HEAD").stdout.strip() or None
    except FileNotFoundError:
        return None                                    # git not installed


def compact(messages, keep=8, limit=300):
    """Shrink old tool output and drop old reasoning to save context."""
    for m in messages[:-keep]:
        if m["role"] == "tool" and len(m["content"]) > limit:
            m["content"] = m["content"][:limit] + "\n...[old output removed]"
        if m["role"] == "assistant":
            m.pop("thinking", None)


def extract_calls(text):
    """Fallback: find {"name":..., "arguments":{...}} the model wrote as plain text."""
    calls, dec, i = [], json.JSONDecoder(), 0
    while (i := text.find("{", i)) != -1:
        try:
            obj, end = dec.raw_decode(text[i:])
        except ValueError:
            i += 1
            continue
        if (isinstance(obj, dict) and obj.get("name") in TOOLS
                and isinstance(obj.get("arguments"), dict)):
            calls.append({"function": {"name": obj["name"], "arguments": obj["arguments"]}})
        i += end
    return calls


def system_prompt():
    prompt = SYSTEM
    rules = os.path.join(WORKDIR, "AGENT.md")
    if os.path.exists(rules):
        with open(rules, encoding="utf-8") as f:
            prompt += "\n\nProject instructions:\n" + f.read()
    return prompt


def run_task(messages, task):
    messages.append({"role": "user", "content": task})
    recent = []
    for _ in range(MAX_STEPS):
        compact(messages)
        msg = stream_chat(messages)
        calls = msg.get("tool_calls") or extract_calls(msg.get("content", ""))
        if calls:
            msg["tool_calls"] = calls
        messages.append(msg)
        if not calls:
            return                                     # final answer already streamed

        for call in calls:
            name, args = call["function"]["name"], call["function"]["arguments"]
            print(f"\n{YELLOW}🔧 {name}({', '.join(f'{k}={short(v)}' for k, v in args.items())}){RESET}")
            sig = (name, json.dumps(args, sort_keys=True))
            recent.append(sig)
            if name not in TOOLS:
                result = f"Error: unknown tool '{name}'. Available: {', '.join(TOOLS)}"
            elif recent[-3:] == [sig] * 3:
                result = "Error: you repeated this exact call 3 times. Try a different approach."
            else:
                try:
                    result = str(TOOLS[name](**args))
                except Exception as e:
                    result = f"Error: {e}"
            color = RED if result.startswith("Error") else CYAN
            print(f"{color}{result[:600]}{'...' if len(result) > 600 else ''}{RESET}")
            messages.append({"role": "tool", "tool_name": name,
                             "content": result[:MAX_TOOL_CHARS]})
    print(f"\n{RED}Stopped: reached max steps.{RESET}")


# ------------------------------------------------------------------ main
def main():
    print(f"Coding agent ({MODEL}) - workspace: {WORKDIR}")
    print("Commands: /auto  /ask  /clear  /undo  /quit")
    messages = load_chat() or [{"role": "system", "content": system_prompt()}]
    cp = None
    
    while True:
        try:
            task = input(f"\n{GREEN}Task{RESET}: ").strip()
            if not task:
                continue
            if task in ("/quit", "/exit"):
                break
            if task == "/auto":
                STATE["auto"] = True
                print("Auto mode: file edits and run_python no longer ask. "
                      "Shell, pip, git commit, delete still ask.")
            elif task == "/ask":
                STATE["auto"] = False
                print("Ask mode: every action asks.")
            elif task == "/clear":
                messages = messages[:1]
                save_chat(messages=messages)
                print("Conversation cleared.")
            elif task == "/undo":
                if cp and confirm("reset workspace to the checkpoint before the last task"):
                    _git("reset", "--hard", cp)
                    _git("clean", "-fd")
                    print("Workspace restored.")
                else:
                    print("Nothing to undo (or git is not installed).")
            else:
                cp = checkpoint() or cp
                try:
                    run_task(messages=messages, task=task)
                finally:
                    save_chat(messages=messages)
                
        except KeyboardInterrupt:
            print(f"\n{RED}Interrupted.{RESET}")
        except Exception as e:
            print(f"\n{RED}Error: {e}{RESET}")


if __name__ == "__main__":
    main()