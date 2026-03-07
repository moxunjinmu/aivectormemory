#!/bin/bash
# Sync README files from dev branch to public repo (main branch)
# Usage: bash scripts/sync-readme.sh
set -e

CURRENT_BRANCH=$(git branch --show-current)

echo "=== Sync README to public repo ==="
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Ensure we're on dev or main
if [ "$CURRENT_BRANCH" != "dev" ] && [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Error: must be on dev or main branch"
    exit 1
fi

# Stash any uncommitted changes
STASHED=false
if [ -n "$(git status --porcelain)" ]; then
    git stash push -m "sync-readme: auto stash"
    STASHED=true
fi

# Switch to main
git checkout main

# Pull latest README files from dev
git checkout dev -- README.md
git checkout dev -- docs/README.de.md docs/README.en.md docs/README.es.md docs/README.fr.md docs/README.ja.md docs/README.zh-TW.md 2>/dev/null || true

# Stage only README files
git add README.md docs/README.*.md 2>/dev/null || true

# Check if there are staged changes
if [ -z "$(git diff --cached --name-only)" ]; then
    echo "No README changes to sync"
    git checkout "$CURRENT_BRANCH"
    if [ "$STASHED" = true ]; then git stash pop; fi
    exit 0
fi
git commit -m "docs: sync README from dev"
git push public main

echo ""
echo "README synced to public repo successfully!"

# Switch back
git checkout "$CURRENT_BRANCH"
if [ "$STASHED" = true ]; then git stash pop; fi
