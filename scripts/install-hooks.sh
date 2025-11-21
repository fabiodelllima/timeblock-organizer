#!/usr/bin/env bash
set -euo pipefail

# ========================================
# install-hooks.sh - Instalar Git Hooks
# ========================================
#
# OBJETIVO  :
#   Copia git hooks do repositório para .git/hooks/
#   Necessário após clonar repositório.
#
# USO:
#   ./scripts/install-hooks.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "[INFO] Instalando git hooks..."

if [ -f "$SCRIPT_DIR/pre-commit.template" ]; then
    cp "$SCRIPT_DIR/pre-commit.template" "$PROJECT_ROOT/.git/hooks/pre-commit"
    chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"
    echo "[OK] Pre-commit hook instalado"
else
    echo "[ERROR] pre-commit.template não encontrado"
    exit 1
fi

echo ""
echo "[OK] Git hooks instalados com sucesso!"
