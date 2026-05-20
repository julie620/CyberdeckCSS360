#!/bin/bash
# =============================================================================
# deploy.sh — One-touch CI/CD pipeline for CyberdeckCSS360
# Usage: chmod +x deploy.sh && ./deploy.sh
# =============================================================================

set -e  # Exit immediately on any error

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

step()  { echo -e "\n${CYAN}${BOLD}[$1/6] $2${NC}"; }
ok()    { echo -e "${GREEN}✔  $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠  $1${NC}"; }
fail()  { echo -e "${RED}✘  $1${NC}"; exit 1; }

echo -e "${BOLD}"
echo "================================================"
echo "   CyberdeckCSS360 — CI/CD Deploy Pipeline"
echo "================================================"
echo -e "${NC}"

# =============================================================================
# 1. PULL LATEST CODE FROM MAIN
# =============================================================================
step 1 "Pulling latest code from main..."

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  fail "Not inside a git repository. Run this script from the project root."
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  warn "Currently on branch '$CURRENT_BRANCH'. Switching to main..."
  git checkout main
fi

git fetch origin
git pull origin main
ok "Repository is up to date with origin/main."

# =============================================================================
# 2. STATIC ANALYSIS — verified via GitHub Actions
# =============================================================================
step 2 "Verifying static analysis passed on GitHub Actions..."

# Static analysis (pylint, flake8, ESLint) is enforced automatically by the
# GitHub Actions workflow on every push/PR to main. This step confirms that
# the latest commit on main has a green Actions run before we deploy.

REPO="dippityy/CyberdeckCSS360"
COMMIT_SHA=$(git rev-parse HEAD)

echo "  → Checking Actions status for commit ${COMMIT_SHA:0:7}..."

# Requires the GitHub CLI (gh) to be installed and authenticated.
# Install: https://cli.github.com  |  Auth: gh auth login
if command -v gh &>/dev/null; then
  # Get the conclusion of the most recent CI workflow run on this commit
  RUN_STATUS=$(gh run list \
    --repo "$REPO" \
    --commit "$COMMIT_SHA" \
    --workflow "ci-cd.yml" \
    --limit 1 \
    --json conclusion \
    --jq '.[0].conclusion' 2>/dev/null || echo "unknown")

  if [ "$RUN_STATUS" = "success" ]; then
    ok "GitHub Actions: CI passed (conclusion: $RUN_STATUS)."
  elif [ "$RUN_STATUS" = "unknown" ] || [ -z "$RUN_STATUS" ]; then
    warn "Could not retrieve Actions status — proceeding, but verify manually:"
    warn "https://github.com/$REPO/actions"
  else
    fail "GitHub Actions CI did not pass (conclusion: $RUN_STATUS). Fix errors before deploying. See: https://github.com/$REPO/actions"
  fi
else
  warn "GitHub CLI (gh) not installed — skipping Actions check."
  warn "Verify manually that CI is green: https://github.com/$REPO/actions"
  warn "Install gh: https://cli.github.com"
fi

# =============================================================================
# 3. TESTS  (Unit → Integration → Smoke)
# =============================================================================
step 3 "Running tests..."

source api/venv/bin/activate

# ── Unit & Integration (pytest) ──────────────────────────────────────────────
echo "  → Running Python unit + integration tests..."
if [ -d "api/tests" ]; then
  pip install pytest pytest-cov --quiet
  python -m pytest api/tests/ -v --tb=short \
    --cov=api --cov-report=term-missing \
    || fail "Python tests failed."
  ok "Python tests passed."
else
  warn "No api/tests/ directory found — skipping Python tests."
fi

deactivate

# ── Smoke test: Vite production build ────────────────────────────────────────
echo "  → Running frontend smoke test (vite build)..."
npm run build \
  || fail "Frontend build (smoke test) failed."
ok "Frontend smoke test passed — build succeeded."

# =============================================================================
# 4. PACKAGE INTO DOCKER IMAGE
# =============================================================================
step 4 "Building Docker image..."

if ! command -v docker &>/dev/null; then
  fail "Docker is not installed or not in PATH. Please install Docker first."
fi

IMAGE_TAG="cyberdeckcss360:latest"
docker build -t "$IMAGE_TAG" . \
  || fail "Docker build failed."
ok "Docker image '$IMAGE_TAG' built successfully."

# =============================================================================
# 5. DEPLOY TO PRODUCTION (docker-compose)
# =============================================================================
step 5 "Deploying to production..."

if ! command -v docker compose &>/dev/null; then
  # Fall back to docker-compose v1 if v2 plugin not available
  COMPOSE_CMD="docker-compose"
else
  COMPOSE_CMD="docker compose"
fi

echo "  → Stopping existing containers..."
$COMPOSE_CMD down 2>/dev/null || true

echo "  → Starting new containers..."
$COMPOSE_CMD up -d \
  || fail "docker-compose up failed."
ok "Containers started."

# =============================================================================
# 6. VERIFY DEPLOYMENT
# =============================================================================
step 6 "Verifying deployment..."

HEALTH_URL="http://localhost:5000/health"
MAX_RETRIES=10
RETRY_DELAY=3

echo "  → Waiting for server at $HEALTH_URL ..."
for i in $(seq 1 $MAX_RETRIES); do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "000")
  if [ "$HTTP_STATUS" -eq 200 ]; then
    break
  fi
  echo "    Attempt $i/$MAX_RETRIES — got HTTP $HTTP_STATUS, retrying in ${RETRY_DELAY}s..."
  sleep "$RETRY_DELAY"
done

if [ "$HTTP_STATUS" -eq 200 ]; then
  ok "Deployment verified! Server responded HTTP 200 at $HEALTH_URL"
else
  fail "Deployment verification failed after $MAX_RETRIES attempts (last status: $HTTP_STATUS). Check 'docker compose logs'."
fi

# =============================================================================
echo -e "\n${GREEN}${BOLD}================================================"
echo "   🚀  Deploy complete!"
echo "================================================${NC}"
echo -e "   App:    http://localhost:5173"
echo -e "   API:    http://localhost:5000"
echo -e "   Health: $HEALTH_URL\n"
