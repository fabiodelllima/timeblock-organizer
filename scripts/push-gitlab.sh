#!/usr/bin/env bash
set -euo pipefail

# ========================================
# push-gitlab.sh - Push para GitLab
# ========================================
#
# OBJETIVO:
#   Push simples para GitLab sem transformações.
#   GitLab contém código na íntegra com comentários e docs/.
#
# DIFERENÇA vs push-github.sh:
#   - GitLab: código completo (desenvolvimento)
#   - GitHub: código showcase (público)
#
# PROCESSO:
#   1. Valida remote 'origin'
#   2. Push direto para origin/branch
#
# USO:
#   ./scripts/push-gitlab.sh

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if ! git remote | grep -q "^origin$"; then
    log_error "Remote 'origin' não configurado"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    log_error "Não foi possível determinar branch atual"
    exit 1
fi

log_info "Branch atual: $CURRENT_BRANCH"
log_info "Pushing para origin/$CURRENT_BRANCH..."
git push origin "$CURRENT_BRANCH"

log_success "Push para GitLab completo!"
