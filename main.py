import json
import re
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from ollama import chat
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

from config import PROJECT_DIR, MAYA_DIR
from utils.all_tools import available_functions, tools
from tool_file.common_tools import open_url_in_browser

MODEL = "qwen3:4b"
MAX_STEPS = 5
DATA_DIR = Path(PROJECT_DIR) / "maya"
DATA_DIR.mkdir(exist_ok=True)

SYSTEM = {
    "role": "system",
    "content": (
        "You are Maya, a professional coding Agent, problem solver and AI assistant. "
        "Use available tools when needed. "
        "Never claim execution succeeded without checking the result. "
        "Remember the conversation context when answering follow-up questions. "
        f"Current directory and Project directory: {PROJECT_DIR} and everything is done inside the this directory"
        "If user say you to call tool then call the tool"
        "If you have any confusion , don't think so much, just ask the user and clear your confusion"
    ),
}

app = FastAPI()
unsaved: dict[str, list] = {}  # new chats that have no file yet
ID_RE = re.compile(r"^[\w\-]+$")
THINK_RE = re.compile(r"<think>(.*?)</think>", re.S)


def chat_path(cid: str) -> Path:
    if not ID_RE.match(cid):
        raise HTTPException(400, "Bad chat id")
    return DATA_DIR / f"{cid}.json"


def load(cid: str) -> list:
    p = chat_path(cid)
    if p.exists():
        raw = json.loads(p.read_text(encoding="utf-8"))
        return raw.get("messages", []) if isinstance(raw, dict) else raw
    if cid in unsaved:
        return unsaved[cid]
    raise HTTPException(404, "Chat not found")


def save(cid: str, messages: list) -> None:
    chat_path(cid).write_text(
        json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    unsaved.pop(cid, None)


def to_ui(m: dict):
    role = m.get("role")
    content = m.get("content") or ""
    if role == "assistant":
        thinking = m.get("thinking") or ""
        found = THINK_RE.findall(content)
        if found:  # older chats may carry <think> tags inside content
            thinking = thinking or "\n".join(t.strip() for t in found)
            content = THINK_RE.sub("", content).strip()
        calls = []
        for c in m.get("tool_calls") or []:
            f = c.get("function", c) if isinstance(c, dict) else {}
            calls.append({"name": f.get("name", "?"), "arguments": f.get("arguments", {})})
        return {"role": role, "content": content, "thinking": thinking, "tool_calls": calls}
    if role == "tool":
        name = m.get("tool_name") or m.get("name") or ""
        return {"role": role, "name": name, "content": str(content)}
    if role == "user":
        return {"role": role, "content": content}
    return None  # hide system messages


def title_of(messages: list) -> str:
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            t = m["content"].strip().replace("\n", " ")
            return t[:48] + ("…" if len(t) > 48 else "")
    return "New chat"

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/info")
def info():
    return {"model": MODEL, "data_dir": PROJECT_DIR, "new_data": PROJECT_DIR}


@app.get("/api/chats")
def list_chats():
    out = []
    for p in sorted(DATA_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            msgs = raw.get("messages", []) if isinstance(raw, dict) else raw
            out.append({
                "id": p.stem,
                "title": title_of(msgs),
                "turns": sum(1 for m in msgs if m.get("role") in ("user", "assistant")),
                "updated": p.stat().st_mtime,
            })
        except Exception:
            continue  # skip files that are not chat histories
    return out


@app.post("/api/chats")
def new_chat():
    cid = datetime.now().strftime("chat_%Y%m%d_%H%M%S")
    unsaved[cid] = [dict(SYSTEM)]
    return {"id": cid}


@app.get("/api/chats/{cid}")
def get_chat(cid: str):
    msgs = [u for u in map(to_ui, load(cid)) if u]
    return {"id": cid, "title": title_of(load(cid)), "messages": msgs}


class Msg(BaseModel):
    text: str


def ev(**kw) -> str:
    return json.dumps(kw, ensure_ascii=False, default=str) + "\n"


def run_turn(cid: str, text: str):
    messages = load(cid)
    if not messages:
        messages.append(dict(SYSTEM))
    messages.append({"role": "user", "content": text})
    try:
        for _ in range(MAX_STEPS):
            yield ev(type="step")
            content, thinking, calls = "", "", []

            for chunk in chat(model=MODEL, messages=messages, tools=tools, think=True, stream=True):
                m = chunk["message"]
                if m.get("thinking"):
                    thinking += m["thinking"]
                    yield ev(type="thinking", text=m["thinking"])
                if m.get("content"):
                    content += m["content"]
                    yield ev(type="content", text=m["content"])
                for c in m.get("tool_calls") or []:
                    args = dict(c.function.arguments or {})
                    calls.append({"name": c.function.name, "arguments": args})
                    yield ev(type="tool_call", name=c.function.name, arguments=args)

            assistant = {"role": "assistant", "content": content}
            if thinking:
                assistant["thinking"] = thinking
            if calls:
                assistant["tool_calls"] = [{"function": c} for c in calls]
            messages.append(assistant)

            if not calls:
                break

            for c in calls:
                fn = available_functions.get(c["name"])
                if fn is None:
                    result = "Error: Unknown tool."
                else:
                    try:
                        result = fn(**c["arguments"])
                    except Exception as exc:
                        result = f"Tool failed: {exc}"
                messages.append({"role": "tool", "tool_name": c["name"], "content": str(result)})
                yield ev(type="tool_result", name=c["name"], result=str(result))
        else:
            yield ev(type="notice", text="Tool-call limit reached.")
    except Exception as exc:
        yield ev(type="error", text=str(exc))
    finally:
        save(cid, messages)
    yield ev(type="done")


@app.post("/api/chats/{cid}/message")
def send_message(cid: str, body: Msg):
    load(cid)  # 404 early if the chat does not exist
    return StreamingResponse(run_turn(cid, body.text), media_type="application/x-ndjson")


if __name__ == "__main__":
    open_url_in_browser("http://127.0.0.1:4220")
    uvicorn.run("main:app", host="127.0.0.1", port=4220, reload=True)