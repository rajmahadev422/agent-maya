import urllib.request
import re


from src.utils.helpers import (
    confirm
)
from src.config import MAX_TOOL_CHARS


def fetch_url(url):
    if not confirm(f"GET {url}"):
        return "User denied"
    req = urllib.request.Request(url, headers={"User-Agent": "coding-agent"})
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read(300000).decode("utf-8", "ignore")
    html = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
    text = re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", html))
    return text[:MAX_TOOL_CHARS]
