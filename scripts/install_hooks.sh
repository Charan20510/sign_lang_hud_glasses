#!/bin/sh
# One-time setup: make git use the tracked hooks in scripts/githooks/.
cd "$(git rev-parse --show-toplevel)" && git config core.hooksPath scripts/githooks && echo "hooks installed: $(git config core.hooksPath)"
