# Documentação Arquivada

Este diretório contém documentação que não reflete mais o estado atual do projeto,
mas é preservada para referência histórica e contexto de decisões passadas.

## Princípio

> "Documentação de recursos históricos são, na melhor hipótese, distrações.
> Em geral, deve-se arquivar ou deletar conteúdo de recursos históricos."
> - ddbeck.com/deprecated-pattern

## Conteúdo

| Arquivo | Data Arquivo | Descrição |
|---------|--------------|-----------|
| `schedule-generate-improvements-2025-11-13.md` | 27-11-2025 | Proposta de melhorias para schedule generate (não implementada, API mudou para --generate) |
| `sprint-e2e-and-test-refactoring-2025-11-12.md` | 27-11-2025 | Planejamento de sprint já concluída |

## Quando Arquivar

Documentos são arquivados quando:

1. **API mudou:** Documento descreve API que não existe mais
2. **Sprint concluída:** Planejamento de sprint já executada
3. **Contexto de sessão:** Documento específico para uma sessão de desenvolvimento
4. **Proposta rejeitada:** Proposta que não foi implementada

## Quando NÃO Arquivar

- **ADRs:** Decisões arquiteturais são imutáveis (histórico de decisões)
- **Business Rules:** Devem ser atualizadas, não arquivadas
- **BDD Scenarios:** Devem refletir API atual

## Referência

Ver `docs/10-meta/deprecation-notices.md` para lista completa de APIs depreciadas.
