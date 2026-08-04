# tools/

## `cross_model_eval.py` — cross-model evaluation harness

Runs every category's attack and defense against a set of local models and
records the three-state verdict for each, then writes a results matrix. It
answers, at scale, the question each demo answers once:

> which models fall to which attack, and does the defense hold?

The harness introduces no new judgement. Each demo already resolves to a
deterministic, machine-checkable verdict (`SUCCEEDED` / `BLOCKED` /
`INCONCLUSIVE` via canary files and exit codes — see
[`shared/console.py`](../shared/console.py)); the harness just sets
`MODEL_NAME`, runs `docker compose up`, and parses the verdict the attacker
prints. The repo's own verdict logic is the source of truth.

### Usage

```bash
# All four categories, attack + defense, across three models:
python3 tools/cross_model_eval.py \
    --models qwen2.5:7b-instruct,qwen3:14b,glm-4.7-flash

# A focused slice:
python3 tools/cross_model_eval.py --models qwen3:14b --categories ASI01,ASI04
```

Flags: `--categories` (subset of `ASI01,ASI02,ASI04,ASI06`), `--phases`
(`attack,defense`), `--timeout` (per-run seconds, default 240), `--out`
(results path), `--base-url` (preflight endpoint), `--skip-preflight`.

Results are written to `tools/eval_results.md` (a matrix) and
`eval_results.json` (raw), both gitignored.

### Example output

```
| Category | qwen2.5:7b-instruct | qwen3:14b |
|----------|---------------------|-----------|
| ASI01    | SUCCEEDED / BLOCKED | declined / BLOCKED |
| ASI04    | SUCCEEDED / BLOCKED | SUCCEEDED / BLOCKED |
```

`SUCCEEDED` in the attack column means the model was exploited; `BLOCKED` in
the defense column means the control held; `declined` means the model refused
on its own — **not** proof of safety, just that this model/payload did not fire.
That distinction is the whole point of the three-state verdict.

### Prerequisites and the one networking gotcha

Docker + a local OpenAI-compatible endpoint the **containers** can reach. The
containers cannot see a server bound only to `localhost` on the host:

- **Ollama** must listen on all interfaces: `OLLAMA_HOST=0.0.0.0 ollama serve`.
- **Docker Desktop**: the compose default `host.docker.internal:11434` then works.
- **Rancher Desktop on macOS**: containers run in a Lima VM, so
  `host.docker.internal` resolves to the VM, not the Mac. Point the containers
  at the Mac's LAN IP instead:
  ```bash
  OPENAI_BASE_URL=http://$(ipconfig getifaddr en0):11434/v1 \
      python3 tools/cross_model_eval.py --models qwen3:14b
  ```

The harness runs a preflight check and refuses to start a long matrix if the
endpoint is unreachable, rather than producing a grid of errors.

### A note on run time

Each run builds (cached after the first) and then runs a full agent loop
against a local model. Small models on modest hardware can take several minutes
per run and may exceed the per-run `--timeout` (recorded as `TIMEOUT`). For a
clean matrix, give capable hardware a generous `--timeout`, or scope the run
with `--categories` / `--models` / `--phases`.
