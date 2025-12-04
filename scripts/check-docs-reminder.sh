#!/bin/bash
# Reminder para atualizar documentação após mudanças em código

# Detectar mudanças em código core
if git diff --cached --name-only | grep -qE "src/timeblock/(models|services|commands)/"; then
    echo ""
    echo "[INFO] Mudanças em código detectadas."
    echo "       Após commit, considere atualizar:"
    echo "       - Business Rules (docs/core/business-rules.md)"
    echo "       - ADRs (docs/decisions/) se decisão arquitetural"
    echo "       - CHANGELOG.md para mudanças notáveis"
    echo ""
fi
