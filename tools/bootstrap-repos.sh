#!/usr/bin/env bash
# Creates the public GitHub repos for the PoC. Idempotent: existing repos are skipped.
# Local clones are NOT created here; each phase initializes its own repo directory.
set -euo pipefail
OWNER=khkim6040
REPOS=(insurance-platform-poc demo-a-platform demo-a-contract demo-b-platform demo-b-template demo-b-contract demo-c-platform demo-c-contract)
for repo in "${REPOS[@]}"; do
  if gh repo view "$OWNER/$repo" >/dev/null 2>&1; then
    echo "exists  $OWNER/$repo"
  else
    gh repo create "$OWNER/$repo" --public --description "Insurance platform PoC: $repo" >/dev/null
    echo "created $OWNER/$repo"
  fi
done
