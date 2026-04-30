"""Tiny exfil collector. Logs anything POSTed to /collect."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from flask import Flask, request

app = Flask(__name__)


def _log(payload: dict) -> None:
    line = json.dumps(
        {"ts": datetime.now(timezone.utc).isoformat(), **payload},
        ensure_ascii=False,
    )
    print(f"[EXFIL] {line}", flush=True)


@app.post("/collect")
def collect():
    data = request.get_json(silent=True) or {"raw": request.get_data(as_text=True)}
    _log({"path": "/collect", "data": data})
    return {"status": "received"}, 200


@app.get("/health")
def health():
    return {"ok": True}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8888"))
    print(f"[EXFIL] listener up on 0.0.0.0:{port}", file=sys.stderr, flush=True)
    app.run(host="0.0.0.0", port=port)
