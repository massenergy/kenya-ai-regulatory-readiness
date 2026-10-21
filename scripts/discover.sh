#!/usr/bin/env bash
# Kenya AI Regulatory Readiness — discovery scan.
#
# Read-only. Greps the target directory for leads on each of the 8
# regulatory questions. Makes no network call. Writes nothing outside
# this script's own stdout. Treat every hit as a lead to go read, not
# as a finished verdict.
set -uo pipefail

TARGET="${1:?Usage: discover.sh <target_dir>}"
if [ ! -d "$TARGET" ]; then
  echo "Not a directory: $TARGET" >&2
  exit 1
fi

# Skipped entirely (not just filtered after the fact) so the scan stays fast
# even on a repo that carries a virtualenv, node_modules, or nested worktrees.
EXCLUDE_DIRS=(.git node_modules .venv venv __pycache__ dist build .next coverage htmlcov worktrees)
EXCLUDE_ARGS=()
for d in "${EXCLUDE_DIRS[@]}"; do EXCLUDE_ARGS+=(--exclude-dir="$d"); done

g() { grep -r "${EXCLUDE_ARGS[@]}" "$@"; }

# Masks user:pass@ in URLs so a committed .env with a real credential never
# shows up verbatim in this script's output.
redact() { sed -E 's#://[^:@/[:space:]]+:[^@/[:space:]]+@#://<redacted>@#g'; }

section() { printf '\n=== %s ===\n' "$1"; }

cd "$TARGET" || exit 1

section "1/2 — Existing compliance / DPIA / impact-assessment docs"
g -liE 'dpia|impact.assessment|privacy.impact|data.protection.act|compliance.posture' \
  --include='*.md' --include='*.txt' --include='*.rst' . 2>/dev/null | head -30

section "3 — Cloud region / data-residency config"
g -niE '(aws|gcp|azure)_?region|gcp_location|data[_-]?residency|location\s*=\s*["\x27](us|eu|africa|europe)' \
  --include='*.yml' --include='*.yaml' --include='*.env*' --include='*.py' \
  --include='*.ts' --include='*.js' --include='*.tf' . 2>/dev/null | head -40
echo "--- DATABASE_URL / connection host hints (credentials redacted) ---"
g -niE 'database_url|db_host|DATABASE_HOST' --include='*.env*' --include='*.yml' --include='*.yaml' . 2>/dev/null \
  | redact | head -10

section "4 — Sector signals (education / health / finance / civil registration)"
g -liE 'student|curriculum|grade[0-9]|patient|diagnos|payment|transaction|national.id|civil.registr' \
  --include='*.md' --include='*.py' --include='*.ts' . 2>/dev/null | head -5
echo "(sampled — this just tells you whether to care about Section 50/Reg 26 at all)"

section "5 — AI vendor SDK usage (which channel: enterprise vs. consumer key)"
echo "--- SDK imports ---"
g -lE 'import (openai|anthropic|google\.generativeai|vertexai)|from google import genai|aws.bedrock|AzureOpenAI' \
  --include='*.py' --include='*.ts' --include='*.js' . 2>/dev/null | head -30
echo "--- enterprise-channel flags (good sign: Vertex/Bedrock/Azure routing) ---"
g -niE 'vertexai\s*=\s*true|use_vertex|bedrock|AzureOpenAI\(' \
  --include='*.py' --include='*.ts' --include='*.js' . 2>/dev/null | head -20
echo "--- raw API key usage (check: is this the same traffic, or a second pathway?) ---"
g -niE '(OPENAI|GEMINI|ANTHROPIC|LLM)_API_KEY' \
  --include='*.py' --include='*.ts' --include='*.js' --include='*.yml' --include='*.yaml' --include='*.env*' . 2>/dev/null \
  | sed -E 's/(_API_KEY["\x27]?[:=][[:space:]]*["\x27]?)[^"\x27[:space:]]{6,}/\1<redacted>/' | head -30

section "6 — Retention / deletion config, and whether it reaches AI-specific stores"
g -liE 'retention|ttl|expire|hard_delete|purge' \
  --include='*.py' --include='*.ts' --include='*.js' --include='*.yml' . 2>/dev/null | head -20
echo "--- vector / embedding stores (check these are in the retention list above) ---"
g -liE 'pinecone|weaviate|chroma|faiss|vertex.search|embedding|vector.?store|datastore' \
  --include='*.py' --include='*.ts' --include='*.js' --include='*.yml' . 2>/dev/null | head -20

section "1 & 7 — Privacy policy / ToS language on automated decisions and vendor terms"
PRIVACY_FILES=$(find . \( -path '*/.git' -o -path '*/node_modules' -o -path '*/.venv' -o -path '*worktrees*' \) -prune -o \
  -regextype posix-extended \
  -iregex '.*(privacy[_-]?policy|terms[_-]?of[_-]?service|data[_-]?processing).*\.(md|html|txt)$' -print \
  2>/dev/null)
echo "Files found: ${PRIVACY_FILES:-none}"
if [ -n "$PRIVACY_FILES" ]; then
  echo "$PRIVACY_FILES" | xargs grep -niE 'automated decision|solely.*automat|right to (object|reconsider)|human review|sub.?processor|data processing addendum|breach notif' 2>/dev/null | head -20
fi

section "8 — AI governance / safety / inventory signals"
g -liE 'ai.?inventory|risk.?register|model.?card|ai.?governance' \
  --include='*.md' . 2>/dev/null | head -10
echo "--- safety/guardrail/judge-style modules (a working 'Measure' function, even without a formal inventory) ---"
g -liE 'safety.?judge|content.?judge|guardrail|moderation|safety.?filter|compliance.?judge' \
  --include='*.py' --include='*.ts' --include='*.js' . 2>/dev/null | head -20

section "Done"
echo "This is a lead list, not a verdict. Open the files above and check the actual logic."
exit 0
