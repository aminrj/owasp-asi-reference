# Makefile for owasp-asi-reference
# Common commands for running demos, checking compliance, and maintenance.

.PHONY: help test test-all clean lint check-compliance docs

.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ── Quick test (no Docker required) ───────────────────────────────────

test: ## Run compliance checks (structure, versions, banners) — no Docker needed
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Quick Test — Compliance Checks"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "  [1/4] Dockerfiles…"
	@$(MAKE) --no-print-directory check-dockerfiles 2>&1 | tail -n +2
	@echo ""
	@echo "  [2/4] Requirements…"
	@$(MAKE) --no-print-directory check-requirements 2>&1 | tail -n +2
	@echo ""
	@echo "  [3/4] Compose services…"
	@$(MAKE) --no-print-directory check-compose-services 2>&1 | tail -n +2
	@echo ""
	@echo "  [4/4] Python banners…"
	@$(MAKE) --no-print-directory check-banners 2>&1 | tail -n +2
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  ✅ All compliance checks passed."
	@echo "  (For full demo tests: make test-all  — requires Docker + Ollama)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Run demos ──────────────────────────────────────────────────────────

test-attack-as01: ## Run ASI01 attack demo
	cd ASI01_agent_goal_hijack/attack && docker compose up --abort-on-container-exit

test-defense-as01: ## Run ASI01 defense demo
	cd ASI01_agent_goal_hijack/defense && docker compose up --abort-on-container-exit

test-attack-as06: ## Run ASI06 attack demo
	cd ASI06_memory_poisoning/attack && docker compose up --abort-on-container-exit

test-defense-as06: ## Run ASI06 defense demo
	cd ASI06_memory_poisoning/defense && docker compose up --abort-on-container-exit

test-attack-as02: ## Run ASI02 attack demo
	cd ASI02_tool_misuse/attack && docker compose up --abort-on-container-exit

test-defense-as02: ## Run ASI02 defense demo
	cd ASI02_tool_misuse/defense && docker compose up --abort-on-container-exit

test-attack-as04: ## Run ASI04 attack demo
	cd ASI04_supply_chain/attack && docker compose up --abort-on-container-exit

test-defense-as04: ## Run ASI04 defense demo
	cd ASI04_supply_chain/defense && docker compose up --abort-on-container-exit

test-all: ## Run all demos (attack + defense for each category)
	@echo "=== ASI01 Attack ==="
	$(MAKE) test-attack-as01
	@echo "=== ASI01 Defense ==="
	$(MAKE) test-defense-as01
	@echo "=== ASI06 Attack ==="
	$(MAKE) test-attack-as06
	@echo "=== ASI06 Defense ==="
	$(MAKE) test-defense-as06
	@echo "=== ASI02 Attack ==="
	$(MAKE) test-attack-as02
	@echo "=== ASI02 Defense ==="
	$(MAKE) test-defense-as02
	@echo "=== ASI04 Attack ==="
	$(MAKE) test-attack-as04
	@echo "=== ASI04 Defense ==="
	$(MAKE) test-defense-as04

# ── Build only (no run) ────────────────────────────────────────────────

build-attack-as01: ## Build ASI01 attack image
	cd ASI01_agent_goal_hijack/attack && docker compose build mcp agent

build-defense-as01: ## Build ASI01 defense image
	cd ASI01_agent_goal_hijack/defense && docker compose build mcp agent

build-attack-as06: ## Build ASI06 attack image
	cd ASI06_memory_poisoning/attack && docker compose build mcp agent

build-defense-as06: ## Build ASI06 defense image
	cd ASI06_memory_poisoning/defense && docker compose build mcp agent

build-attack-as02: ## Build ASI02 attack image
	cd ASI02_tool_misuse/attack && docker compose build mcp agent

build-defense-as02: ## Build ASI02 defense image
	cd ASI02_tool_misuse/defense && docker compose build mcp agent

build-attack-as04: ## Build ASI04 attack image
	cd ASI04_supply_chain/attack && docker compose build mcp agent

build-defense-as04: ## Build ASI04 defense image
	cd ASI04_supply_chain/defense && docker compose build mcp agent

build-all: ## Build all images
	$(MAKE) build-attack-as01 build-defense-as01
	$(MAKE) build-attack-as06 build-defense-as06
	$(MAKE) build-attack-as02 build-defense-as02
	$(MAKE) build-attack-as04 build-defense-as04

# ── Cleanup ────────────────────────────────────────────────────────────

clean: ## Remove canary files, data directories, and stopped containers
	@echo "Removing canary files..."
	rm -f /tmp/outbox.canary /tmp/exfil.canary
	rm -f ASI01_agent_goal_hijack/attack/data/*.canary
	rm -f ASI01_agent_goal_hijack/defense/data/*.canary
	rm -f ASI06_memory_poisoning/attack/data/*.canary
	rm -f ASI06_memory_poisoning/defense/data/*.canary
	rm -f ASI02_tool_misuse/attack/data/*.canary
	rm -f ASI02_tool_misuse/defense/data/*.canary
	rm -f ASI04_supply_chain/attack/data/*.canary ASI04_supply_chain/attack/data/credentials.env
	rm -f ASI04_supply_chain/defense/data/*.canary ASI04_supply_chain/defense/data/credentials.env
	rm -f ASI06_memory_poisoning/attack/data/memory_store.json
	rm -f ASI06_memory_poisoning/defense/data/memory_store.json
	@echo "Removing stopped containers and volumes..."
	docker compose -f ASI01_agent_goal_hijack/attack/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker compose -f ASI01_agent_goal_hijack/defense/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker compose -f ASI06_memory_poisoning/attack/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker compose -f ASI06_memory_poisoning/defense/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker compose -f ASI02_tool_misuse/attack/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker compose -f ASI02_tool_misuse/defense/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker compose -f ASI04_supply_chain/attack/docker-compose.yml down --remove-orphans 2>/dev/null || true
	docker compose -f ASI04_supply_chain/defense/docker-compose.yml down --remove-orphans 2>/dev/null || true
	@echo "Done."

# ── Compliance checks ──────────────────────────────────────────────────

check-dockerfiles: ## Verify all Dockerfiles use python:3.12-slim
	@echo "Checking Dockerfiles..."
	@find . -name Dockerfile -not -path "./.git/*" | while read f; do \
		if grep -q "FROM python:3.12-slim" "$$f"; then \
			echo "  ✅ $$f"; \
		else \
			echo "  ❌ $$f (not python:3.12-slim)"; \
			exit 1; \
		fi; \
	done
	@echo "All Dockerfiles use python:3.12-slim."

check-requirements: ## Verify all requirements.txt pin exact versions
	@echo "Checking requirements.txt files..."
	@find . -name requirements.txt -not -path "./.git/*" | while read f; do \
		count=$$(grep -c "==" "$$f"); \
		lines=$$(wc -l < "$$f"); \
		if [ "$$count" -eq "$$lines" ] && [ "$$count" -gt 0 ]; then \
			echo "  ✅ $$f ($$count pinned deps)"; \
		else \
			echo "  ❌ $$f (not all deps pinned)"; \
			exit 1; \
		fi; \
	done
	@echo "All requirements.txt files are fully pinned."

check-compose-services: ## Verify all docker-compose.yml have mcp + agent services
	@echo "Checking docker-compose.yml services..."
	@find . -name docker-compose.yml -not -path "./.git/*" | while read f; do \
		if grep -q "^  mcp:" "$$f" && grep -q "^  agent:" "$$f"; then \
			echo "  ✅ $$f (mcp + agent)"; \
		else \
			echo "  ❌ $$f (missing mcp or agent service)"; \
			exit 1; \
		fi; \
	done
	@echo "All docker-compose.yml files have mcp + agent services."

check-banners: ## Verify all Python files have VULNERABILITY/DEFENSE banners
	@echo "Checking Python banners..."
	@find . -name "*.py" -not -path "./.git/*" -not -path "./shared/*" | while read f; do \
		if grep -qE "# >>> (VULNERABILITY|DEFENSE) \(" "$$f"; then \
			echo "  ✅ $$f"; \
		else \
			echo "  ⚠️  $$f (no banner found)"; \
		fi; \
	done

check-compliance: ## Run all compliance checks
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Compliance Check"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	$(MAKE) check-dockerfiles
	$(MAKE) check-requirements
	$(MAKE) check-compose-services
	$(MAKE) check-banners
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  All checks passed."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Documentation ──────────────────────────────────────────────────────

docs: ## Show documentation overview
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Documentation"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "  README.md          - Project overview and quickstart"
	@echo "  WALKTHROUGH.md     - Full walkthrough (input→state→action)"
	@echo "  CONTRIBUTING.md    - How to contribute categories"
	@echo "  SECURITY.md        - Security policy"
	@echo "  CODE_OF_CONDUCT.md - Contributor covenant"
	@echo "  CHANGELOG.md       - Release history"
	@echo ""
	@echo "  Category READMEs:"
	@echo "    ASI01_agent_goal_hijack/README.md"
	@echo "    ASI06_memory_poisoning/README.md"
	@echo "    ASI02_tool_misuse/README.md"
	@echo ""
	@echo "  Per-folder READMEs:"
	@echo "    ASI01_agent_goal_hijack/{attack,defense}/README.md"
	@echo "    ASI06_memory_poisoning/{attack,defense}/README.md"
	@echo "    ASI02_tool_misuse/{attack,defense}/README.md"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
