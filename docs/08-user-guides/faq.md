# Perguntas Frequentes

## Como funciona o Event Reordering?

Detecta conflitos automaticamente e propõe mudanças baseadas em prioridades.

## Posso ter múltiplos timers?

Não. Apenas 1 timer ativo por vez.

## RRULE suporta quais recorrências?

Todas do RFC 5545: diário, semanal, mensal, customizado.

## Como desfazer uma reordenação?

Use `timeblock schedule undo` ou edite manualmente os horários.

## O sistema funciona offline?

Sim. Todos os dados são armazenados localmente em SQLite.
