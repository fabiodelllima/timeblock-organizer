#!/usr/bin/env bash
set -euo pipefail

# ========================================
# push-github.sh - Push para GitHub
# ========================================
#
# OBJETIVO:
#   Transforma código completo (GitLab) em código showcase (GitHub)
#   removendo docs/ e comentários inline antes do push.
#
# PROCESSO:
#   1. Valida remote 'github' e working tree limpo
#   2. Cria branch temporária para transformações
#   3. Remove docs/ do git (mantém no filesystem)
#   4. Executa strip-comments.py (remove comentários)
#   5. Commita transformações (--no-verify)
#   6. Push force para github/branch
#   7. Cleanup: volta branch original, deleta temporária
#
# IMPORTANTE:
#   - Commits mantêm mesmo hash (história idêntica)
#   - GitHub: código limpo (sem docs/, sem comentários)
#   - GitLab: código completo (não afetado)
#
# REQUISITOS:
#   - Remote 'github' configurado
#   - Working tree limpo
#   - Python e strip-comments.py disponíveis
#
# USO:
#   ./scripts/push-github.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMP_BRANCH="temp-github-push"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if ! git remote | grep -q "^github$"; then
    log_error "Remote 'github' não configurado"
    echo "Configure: git remote add github git@github.com:USER/REPO.git"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    log_error "Não foi possível determinar branch atual"
    exit 1
fi

log_info "Branch atual: $CURRENT_BRANCH"

if [ -n "$(git status --porcelain)" ]; then
    log_error "Working tree não está limpo. Commit ou stash suas mudanças."
    exit 1
fi

log_info "Criando branch temporária: $TEMP_BRANCH"
git checkout -b "$TEMP_BRANCH"

cleanup() {
    log_info "Executando cleanup..."
    git checkout "$CURRENT_BRANCH" 2>/dev/null || true
    git branch -D "$TEMP_BRANCH" 2>/dev/null || true
}
trap cleanup EXIT

log_info "Removendo docs/ do git..."
git rm -r --cached docs/ 2>/dev/null || true
git commit --no-verify -m "chore: Remove docs/ para GitHub showcase" --allow-empty

log_info "Executando strip-comments.py..."
cd "$PROJECT_ROOT"
python scripts/strip-comments.py

if [ -n "$(git status --porcelain)" ]; then
    log_info "Commitando código transformado..."
    git add cli/src/
    git commit --no-verify -m "chore: Remove comentários inline para GitHub showcase"
else
    log_warn "Nenhuma mudança após strip-comments.py"
fi

log_info "Pushing para github/$CURRENT_BRANCH (force)..."
git push github "$TEMP_BRANCH:$CURRENT_BRANCH" --force

log_success "Push para GitHub completo!"
log_info "Branch GitHub: $CURRENT_BRANCH"

# ========================================
# LEMBRETE PÓS-PUSH GITHUB
# ========================================
echo ""
echo "[LEMBRETE] GitHub showcase atualizado. Verifique:"
echo "  - README.md público está atualizado"
echo "  - Docs/ foram corretamente filtrados"
echo "  - Showcase está profissional e apresentável"
echo ""
