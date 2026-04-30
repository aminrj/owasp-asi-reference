# `_shared/`

Reusable scaffolding consumed by every category folder. Two pieces:

- **`exfil_listener/`** — a tiny Flask server on port 8888 that
  prints whatever it receives. Stand-in for "the attacker's
  collection point." Each category's compose stack runs an instance
  as a service named `exfil`.
- **`agent_harness/`** — a thin Python wrapper around Ollama's chat
  API plus an MCP client loop. Lets every category implement a
  vulnerable agent in ~30 lines of glue code.

## Why bake-in vs. mount

Each category's `Dockerfile` `COPY`s `_shared/` into the image at
build time:

```dockerfile
COPY _shared/ /opt/_shared/
RUN pip install -e /opt/_shared/agent_harness
```

This keeps the resulting image self-contained and shippable
independently of the repo layout, while still letting all categories
share one source of truth.
