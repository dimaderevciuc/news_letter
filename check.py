import json, urllib.request

payload = {
    "model": "qwen2.5:3b",
    "prompt": "Reply with only this JSON and nothing else: {\"ok\": true}",
    "stream": False,
    "format": "json",
}
req = urllib.request.Request(
    "http://localhost:11434/api/generate",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(json.load(r)["response"])