#!/usr/bin/env bash
set -uo pipefail

DOCKER_BUILD_TIMEOUT=600
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

log()  { printf "[%s] %b\n" "$(date -u +%H:%M:%S)" "$*"; }
pass() { log "${GREEN}PASSED${NC} -- $1"; }
fail() { log "${RED}FAILED${NC} -- $1"; }
stop_at() { printf "\n${RED}${BOLD}Validation stopped at %s.${NC}\n" "$1"; exit 1; }

PING_URL="${1:-}"
REPO_DIR="${2:-.}"

if [ -z "$PING_URL" ]; then
  printf "Usage: %s <ping_url>\n" "$0"; exit 1
fi

printf "${BOLD}Step 1/3: Pinging HF Space${NC}...\n"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{}' "$PING_URL/reset" --max-time 30 || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
  pass "HF Space is live"
else
  fail "HF Space /reset returned $HTTP_CODE"; stop_at "Step 1"
fi

printf "${BOLD}Step 2/3: Docker build${NC}...\n"
if [ -f "Dockerfile" ] || [ -f "server/Dockerfile" ]; then
  if docker build . -t test-build > /dev/null 2>&1; then
    pass "Docker build succeeded"
  else
    fail "Docker build failed"; stop_at "Step 2"
  fi
else
  fail "No Dockerfile found"; stop_at "Step 2"
fi

printf "${BOLD}Step 3/3: OpenEnv validate${NC}...\n"
if openenv validate; then
  pass "openenv validate passed"
  printf "\n${GREEN}${BOLD}All 3/3 checks passed! Ready to submit.${NC}\n"
else
  fail "openenv validate failed"; stop_at "Step 3"
fi
