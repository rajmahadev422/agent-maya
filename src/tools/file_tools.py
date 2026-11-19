import os
import shutil
import re

# local modules
from src.utils.helpers import (
    _safe, confirm, show_diff
)
from src.config import WORKDIR, SKIP_DIRS



def read_file(path):
    with open(_safe(path), encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    full = _safe(path)
    old = read_file(path) if os.path.exists(full) else ""
    if old == content:
        return "No changes"
    show_diff(path, old, content)
    if not confirm(f"apply changes to {path}"):
        return "User denied"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} chars to {path}"


def edit_file(path, old, new):
    text = read_file(path)
    if text.count(old) != 1:
        return f"Error: 'old' must appear exactly once (found {text.count(old)})"
    updated = text.replace(old, new)
    show_diff(path, text, updated)
    if not confirm(f"apply edit to {path}"):
        return "User denied"
    with open(_safe(path), "w", encoding="utf-8") as f:
        f.write(updated)
    return f"Edited {path}"


def list_files():
    out = []
    for root, dirs, files in os.walk(WORKDIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        out += [os.path.relpath(os.path.join(root, f), WORKDIR) for f in files]
    return "\n".join(sorted(out)) or "(empty)"


def read_file_lines(path, start, end):
    lines = read_file(path).splitlines()
    s, e = max(int(start), 1), min(int(end), len(lines))
    body = "\n".join(f"{i}: {lines[i - 1]}" for i in range(s, e + 1))
    return f"({len(lines)} lines total)\n{body}"


def grep(pattern, path="."):
    rx, base, hits = re.compile(pattern), _safe(path), []
    if os.path.isfile(base):
        files = [base]
    else:
        files = []
        for root, dirs, names in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            files += [os.path.join(root, n) for n in names]
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    if rx.search(line):
                        hits.append(f"{os.path.relpath(fp, WORKDIR)}:{n}: {line.rstrip()[:200]}")
                        if len(hits) >= 100:
                            return "\n".join(hits) + "\n(truncated at 100 matches)"
        except (UnicodeDecodeError, OSError):
            continue
    return "\n".join(hits) or "No matches"


def delete_file(path):
    if not confirm(f"delete {path}"):
        return "User denied"
    full = _safe(path)
    shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
    return f"Deleted {path}"


def move_file(src, dst):
    os.makedirs(os.path.dirname(_safe(dst)), exist_ok=True)
    shutil.move(_safe(src), _safe(dst))
    return f"Moved {src} -> {dst}"
