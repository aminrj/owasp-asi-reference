# Lab Setup

## Prerequisites

| Tool | Version | Why |
|------|---------|-----|
| Docker | 24+ with `compose` plugin | Each category folder runs as a compose stack |
| [Ollama](https://ollama.com) | latest | Local LLM backend; no API keys needed |
| Python | 3.11+ | Only needed if you want to run `exploit.py` from the host |

## One-time setup

```bash
# Install Ollama (macOS shown; see ollama.com for Linux/Windows)
brew install ollama
ollama serve &

# Pull the model used by the demo agents
ollama pull qwen2.5:3b-instruct
```

## Networking

The agent containers reach Ollama on the host at
`host.docker.internal:11434`.

- **macOS / Windows.** Works out of the box; Docker Desktop maps
  `host.docker.internal` automatically.
- **Linux.** Each `docker-compose.yml` adds:

  ```yaml
  extra_hosts:
    - "host.docker.internal:host-gateway"
  ```

  which makes the same hostname resolvable.

## Running a demo

```bash
cd asi02-tool-misuse/attack
docker compose up --build
# wait until you see "agent ready"
# in another terminal:
docker compose logs -f exfil
```

When you're done:

```bash
docker compose down -v
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Agent hangs at startup | Ollama not running on host | `ollama serve` |
| `connection refused` to `host.docker.internal` | Linux host without `extra_hosts` | Already added in compose; check Docker version ≥ 20.10 |
| Model pulls every run | Ollama model not pre-pulled | `ollama pull qwen2.5:3b-instruct` once |
| Attack output looks different from `expected_output.txt` | LLM stochasticity | `temperature=0` is set; re-run; if persistent, file an issue |
