# Sprint 1.1 - Decisões Tomadas

**Data:** 03 de Novembro de 2025

**Duração Real:** 6h (previsto: 4h)

## Decisões Críticas

### 1. NÃO Renomear Código

- Manter `HabitInstance` no código
- Usar "Hábitos Atômicos" apenas em docs/UX/marketing
- **ADR:** 006-habitinstance-naming.md

### 2. Adiar Alembic para v1.3.0

- v1.2.0 usa script Python simples
- Alembic junto com ambientes formalizados
- **ADR:** 007-alembic-timing.md

### 3. Ambientes em v1.3.0

- 3 ambientes: dev/test/prod
- Admin é role, não ambiente
- Sync Linux/Termux planejado para v2.0
- **ADR:** 008-environment-strategy.md

### 4. Foco v1.2.0: Qualidade

- Corrigir testes falhando
- Aumentar cobertura 69% → 90%
- Logging básico
- Documentação showcase

## Análise Completa

- 26 arquivos mapeados
- 141 referências identificadas
- 4 riscos catalogados
- Estimativa: 44h → 16h (foco em qualidade)

## Próximo

**Sprint 1.2** - Correção de Testes (6h)
