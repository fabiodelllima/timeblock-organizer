#!/usr/bin/env bash
set -euo pipefail

# ========================================
# test-cicd.sh - Validar Instalação CI/CD
# ========================================
#
# OBJETIVO:
#   Valida que scripts CI/CD estão corretamente instalados.
#
# TESTES:
#   1. Scripts existem (strip-comments.py, push-*.sh, test-cicd.sh)
#   2. Permissões de execução (chmod +x)
#   3. Pre-commit hook instalado (opcional Sprint 3.2)
#   4. Remotes Git (origin=GitLab, github=GitHub)
#   5. Python disponível no PATH
#   6. Ruff configurado (cli/.ruff.toml)
#
# USO:
#   ./scripts/test-cicd.sh
#
# EXIT CODE:
#   0 = todos testes passam
#   1 = algum teste falhou

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0

check_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

check_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

check_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo "========================================="
echo "TimeBlock CI/CD Scripts Validation"
echo "========================================="
echo ""

log_info "Verificando scripts..."
for script in strip-comments.py push-github.sh push-gitlab.sh test-cicd.sh; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        check_pass "Script existe: $script"
    else
        check_fail "Script não encontrado: $script"
    fi
done

log_info "Verificando permissões..."
for script in strip-comments.py push-github.sh push-gitlab.sh test-cicd.sh; do
    if [ -x "$SCRIPT_DIR/$script" ]; then
        check_pass "Executável: $script"
    else
        check_fail "Não executável: $script"
    fi
done

log_info "Verificando pre-commit hook..."
if [ -f "$PROJECT_ROOT/.git/hooks/pre-commit" ]; then
    if [ -x "$PROJECT_ROOT/.git/hooks/pre-commit" ]; then
        check_pass "Pre-commit hook instalado"
    else
        check_fail "Pre-commit existe mas não é executável"
    fi
else
    check_warn "Pre-commit hook não instalado (opcional Sprint 3.2)"
fi

log_info "Verificando remotes Git..."

if git remote | grep -q "^origin$"; then
    ORIGIN_URL=$(git remote get-url origin)
    if [[ "$ORIGIN_URL" == *"gitlab.com"* ]]; then
        check_pass "Remote 'origin' → GitLab: $ORIGIN_URL"
    elif [[ "$ORIGIN_URL" == *"github.com"* ]]; then
        check_warn "Remote 'origin' aponta para GitHub (deveria ser GitLab)"
        echo "         Atual: $ORIGIN_URL"
        echo "         Configure GitLab: git remote set-url origin git@gitlab.com:USER/REPO.git"
    else
        check_pass "Remote 'origin' configurado: $ORIGIN_URL"
    fi
else
    check_fail "Remote 'origin' não configurado"
fi

if git remote | grep -q "^github$"; then
    GITHUB_URL=$(git remote get-url github)
    if [[ "$GITHUB_URL" == *"github.com"* ]]; then
        check_pass "Remote 'github' → GitHub: $GITHUB_URL"
    else
        check_warn "Remote 'github' não aponta para GitHub: $GITHUB_URL"
    fi
else
    check_warn "Remote 'github' não configurado"
    echo "         Configure: git remote add github git@github.com:USER/REPO.git"
fi

log_info "Verificando Python..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    check_pass "Python disponível: $PYTHON_VERSION"
else
    check_fail "Python não encontrado"
fi

log_info "Verificando Ruff..."
if [ -f "$PROJECT_ROOT/cli/.ruff.toml" ]; then
    check_pass "cli/.ruff.toml configurado"
else
    check_fail "cli/.ruff.toml não encontrado"
fi

echo ""
echo "========================================="
echo "SUMMARY"
echo "========================================="
echo -e "${GREEN}Passed:${NC} $PASS_COUNT"
echo -e "${RED}Failed:${NC} $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}[OK] Todos testes críticos passaram!${NC}"
    if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        echo ""
        echo -e "${YELLOW}ATENÇÃO: Configuração remotes não ideal${NC}"
        echo "Origin deveria apontar para GitLab (código completo)"
        echo "Consulte docs/10-meta/cicd-quickstart-guide.md para configurar"
    fi
    exit 0
else
    echo -e "${RED}[FAIL] $FAIL_COUNT teste(s) falharam${NC}"
    exit 1
fi
