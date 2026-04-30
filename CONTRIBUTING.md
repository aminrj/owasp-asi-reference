# Contributing

Thanks for considering a contribution. This is a reference repo —
the bar for merge is *clarity and reproducibility*, not feature
completeness.

## What we want

- Fixes to existing categories that make the attack or defense
  clearer, smaller, or more reliable.
- New ASI categories (ASI03, ASI04, etc.) that follow the
  established folder pattern.
- Additional agent-framework variants (LangChain, LangGraph,
  AutoGen) of an *already-shipped* MCP-based category.
- Translations of `WALKTHROUGH.md` files. English content must
  stabilize first.

## What we don't want at this stage

- Interactive web UIs on top of the repo.
- Multi-vector attack chains. Those belong in
  [agentdojo-live](https://github.com/aminrj-labs/agentdojo-live).
- Production-grade defense libraries. The defenses here are
  *canonical illustrations*, not battle-hardened code.
- Rewrites of the OWASP category descriptions. We track upstream
  wording.

## Adding a new ASI category

Copy an existing folder (e.g. `asi02-tool-misuse/`) as a template:

```
asiNN-short-name/
├── README.md                # 2-paragraph summary + OWASP link
├── WALKTHROUGH.md           # narrative: setup → attack → fix → re-test
├── attack/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── <vulnerable_components>.py
│   ├── exploit.py           # single-command attack trigger
│   └── expected_output.txt  # what the reader should see
└── defense/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── <same components, with control applied>
    ├── exploit.py           # SAME exploit script
    └── expected_output.txt  # shows the defense blocking it
```

Constraints:

1. The `exploit.py` in `attack/` and `defense/` must be byte-identical.
   The whole point is "same attack, controlled environment differs."
2. Every demo must run with `docker compose up --build` plus at most
   one `python exploit.py` invocation from the host.
3. Use the `_shared/agent_harness/` rather than re-implementing an
   agent loop.
4. Use `qwen2.5:3b-instruct` via host Ollama as the default model.
   Other models are fine as additional examples but not as the
   default.

## Local development

```bash
git clone https://github.com/aminrj-labs/owasp-asi-reference
cd owasp-asi-reference
ollama pull qwen2.5:3b-instruct
cd asi02-tool-misuse/attack && docker compose up --build
```

## Code of conduct

Be civil. Don't use this repo to attack systems you don't own.

## License

By contributing you agree that your contributions are licensed under
[Apache-2.0](LICENSE).
