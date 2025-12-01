# Sprint 1.1 - Análise de Impacto HabitAtom

- **Data:** 02 de Novembro de 2025
- **Duração:** 4h
- **Status:** EM ANDAMENTO

## Resumo Executivo

**Escopo Total:**

- 56 referências em código fonte (cli/src/)
- 85 referências em testes (cli/tests/)
- 33 referências snake_case (habit_instance)
- 2 referências lowercase (habitinstance - tablename)
- **26 arquivos únicos afetados**

## Categorização de Arquivos

### Categoria 1: Modelo e Database (CRÍTICO)

**Prioridade:** MÁXIMA - Base da refatoração

| Arquivo                    | Referências | Tipo de Mudança                    |
| -------------------------- | ----------- | ---------------------------------- |
| `models/habit_instance.py` | 7           | Renomear arquivo → `habit_atom.py` |
| `models/__init__.py`       | 3           | Atualizar exports                  |
| `models/habit.py`          | 2           | Atualizar relationship             |
| `database/migrations.py`   | 3           | Criar nova migration               |

**Mudanças:**

- Classe: `HabitInstance` → `HabitAtom`
- Enum: `HabitInstanceStatus` → `HabitAtomStatus`
- Tabela: `habitinstance` → `habitatom`
- Arquivo: `habit_instance.py` → `habit_atom.py`

### Categoria 2: Service Layer (CRÍTICO)

**Prioridade:** MÁXIMA - Lógica de negócio

| Arquivo                                | Referências | Tipo de Mudança                    |
| -------------------------------------- | ----------- | ---------------------------------- |
| `services/habit_instance_service.py`   | 15          | Renomear → `habit_atom_service.py` |
| `services/event_reordering_service.py` | 13          | Atualizar imports e type hints     |
| `services/__init__.py`                 | 2           | Atualizar exports                  |

**Mudanças:**

- Classe: `HabitInstanceService` → `HabitAtomService`
- Métodos: Manter nomes (generate_instances → generate_atoms é opcional)
- Type hints: `HabitInstance` → `HabitAtom`

### Categoria 3: CLI Commands (ALTA)

**Prioridade:** ALTA - Interface do usuário

| Arquivo                | Referências | Impacto Usuário |
| ---------------------- | ----------- | --------------- |
| `commands/habit.py`    | 4           | Imports e calls |
| `commands/schedule.py` | 6           | Imports e calls |
| `commands/report.py`   | 6           | Imports e calls |
| `commands/timer.py`    | 5           | Imports e calls |

**Mudanças:**

- Imports: `HabitInstanceService` → `HabitAtomService`
- Variáveis locais: `instance` → `atom` (opcional)
- Mensagens ao usuário: Considerar manter "instância" ou mudar para "átomo"

### Categoria 4: Testes Unitários (ALTA)

**Prioridade:** ALTA - Garantir qualidade

| Arquivo                                            | Referências | Tipo              |
| -------------------------------------------------- | ----------- | ----------------- |
| `test_models/test_habit_instance.py`               | 3           | Renomear arquivo  |
| `test_models/test_habit_instance_overdue.py`       | 14          | Renomear arquivo  |
| `test_models/test_habit_instance_user_override.py` | 3           | Renomear arquivo  |
| `test_services/test_habit_instance_service.py`     | 16          | Renomear arquivo  |
| `test_services/test_event_reordering_*.py`         | 6           | Atualizar imports |
| `test_services/test_timer_service.py`              | 1           | Atualizar import  |
| `test_commands/test_habit_adjust.py`               | 6           | Atualizar imports |

**Total:** 7 arquivos de teste a renomear/atualizar

### Categoria 5: Testes de Integração (MÉDIA)

**Prioridade:** MÉDIA - Validação E2E

| Arquivo                                                   | Referências | Tipo                       |
| --------------------------------------------------------- | ----------- | -------------------------- |
| `integration/services/test_habit_instance_integration.py` | 15          | Renomear arquivo           |
| `integration/services/test_task_integration.py`           | 2           | Atualizar imports          |
| `integration/services/test_timer_integration.py`          | 2           | Atualizar imports          |
| `integration/database/test_migrations.py`                 | 3           | Atualizar testes de tabela |
| `integration/workflows/conftest.py`                       | 2           | Atualizar fixtures         |

**Total:** 5 arquivos de integração

### Categoria 6: Fixtures e Conftest (BAIXA)

**Prioridade:** BAIXA - Infraestrutura de teste

| Arquivo                         | Referências | Tipo             |
| ------------------------------- | ----------- | ---------------- |
| `tests/conftest.py`             | 1           | Atualizar import |
| `tests/integration/conftest.py` | 1           | Atualizar import |

## Estratégia de Migration SQL

### Migration Alembic

```python
# versions/XXXX_rename_habitinstance_to_habitatom.py
"""Rename HabitInstance to HabitAtom

Revision ID: XXXX
Revises: YYYY
Create Date: 2025-11-02
"""
from alembic import op

def upgrade():
    # Renomear tabela
    op.rename_table('habitinstance', 'habitatom')

    # Verificar e atualizar constraints se necessário
    # Foreign keys são automaticamente mantidas no SQLite

def downgrade():
    # Rollback
    op.rename_table('habitatom', 'habitinstance')
```

### SQL Direto (Alternativa)

```sql
-- Renomear tabela
ALTER TABLE habitinstance RENAME TO habitatom;

-- Verificar estrutura
PRAGMA table_info(habitatom);

-- Testar queries
SELECT * FROM habitatom LIMIT 1;
```

### Teste de Migration

```bash
# Backup do banco
cp data/timeblock.db data/timeblock.db.backup

# Aplicar migration
alembic upgrade head

# Validar
sqlite3 data/timeblock.db ".tables"

# Rollback se necessário
alembic downgrade -1
```

## Ordem de Execução Proposta

### Fase 1: Preparação (Sprint 1.2)

1. Criar migration SQL
2. Testar migration em banco de dev
3. Criar script de rollback

### Fase 2: Modelos (Sprint 1.3)

1. Renomear `habit_instance.py` → `habit_atom.py`
2. Atualizar classe e enum
3. Atualizar `models/__init__.py`
4. Atualizar `models/habit.py` relationships

### Fase 3: Services (Sprint 1.4)

1. Renomear `habit_instance_service.py` → `habit_atom_service.py`
2. Atualizar classe HabitInstanceService
3. Atualizar `services/__init__.py`
4. Atualizar `event_reordering_service.py` type hints

### Fase 4: Commands (Sprint 1.5)

1. Atualizar `commands/habit.py`
2. Atualizar `commands/schedule.py`
3. Atualizar `commands/report.py`
4. Atualizar `commands/timer.py`

### Fase 5: Testes Unitários (Sprint 1.6)

1. Renomear arquivos de teste
2. Atualizar imports
3. Atualizar fixtures
4. Executar e validar

### Fase 6: Testes Integração (Sprint 1.7)

1. Renomear arquivos
2. Atualizar imports
3. Atualizar workflows
4. Validar E2E

## Riscos Identificados

### Risco 1: Quebra de Event Reordering

**Probabilidade:** MÉDIA
**Impacto:** ALTO

**Motivo:**

- `event_reordering_service.py` tem 13 referências a HabitInstance
- Type hints em múltiplas funções
- Testes de integração dependem do funcionamento

**Mitigação:**

- Executar TODOS os 78 testes de Event Reordering após mudança
- Verificar tuple returns funcionam
- Teste específico: `test_habit_instance_integration.py`

### Risco 2: Migration Falha em Produção

**Probabilidade:** BAIXA
**Impacto:** CRÍTICO

**Motivo:**

- SQLite pode ter comportamentos inesperados
- Dados de usuários podem ser perdidos

**Mitigação:**

- Testar migration em 3 bancos diferentes
- Script de rollback testado
- Backup obrigatório antes de migration
- Documentação clara de recovery

### Risco 3: Imports Circulares

**Probabilidade:** BAIXA
**Impacto:** MÉDIO

**Motivo:**

- Mudança de nome pode revelar imports circulares ocultos

**Mitigação:**

- Importar sempre por path completo
- Usar TYPE_CHECKING para type hints
- Executar `mypy` após cada mudança

### Risco 4: Testes Falhando

**Probabilidade:** MÉDIA
**Impacto:** MÉDIO

**Motivo:**

- 85 referências em testes
- Fixtures podem quebrar
- Mocks podem ficar inconsistentes

**Mitigação:**

- Executar testes após cada categoria
- Atualizar fixtures primeiro
- Usar buscar e substituir com cuidado

## Checklist de Validação

Após cada fase, validar:

- [ ] Imports funcionando (sem ImportError)
- [ ] Type hints corretos (mypy passa)
- [ ] Testes unitários passando (pytest unit)
- [ ] Testes integração passando (pytest integration)
- [ ] Migration reversível
- [ ] Nenhum TODO/FIXME adicionado

## Dependências Externas

**Nenhuma identificada.**

Todas as mudanças são internas ao projeto. Não há:

- APIs externas que usam HabitInstance
- Bibliotecas de terceiros
- Webhooks ou integrações

## Estimativas Revisadas

Com base na análise:

| Sprint                | Estimativa Original | Estimativa Revisada | Justificativa                   |
| --------------------- | ------------------- | ------------------- | ------------------------------- |
| 1.1 Análise           | 4h                  | 4h                  | ✓ Mantida                       |
| 1.2 Migration         | 3h                  | 3h                  | ✓ Mantida                       |
| 1.3 Modelos           | 4h                  | 4h                  | ✓ Mantida                       |
| 1.4 Services          | 6h                  | 7h                  | +1h (Event Reordering complexo) |
| 1.5 CLI               | 5h                  | 5h                  | ✓ Mantida                       |
| 1.6 Testes Unit       | 8h                  | 9h                  | +1h (85 refs em testes)         |
| 1.7 Testes Integração | 6h                  | 6h                  | ✓ Mantida                       |
| 1.8 Documentação      | 8h                  | 8h                  | ✓ Mantida                       |
| **TOTAL**             | **44h**             | **46h**             | +2h buffer                      |

## Arquivos de Referência Criados

Durante esta análise, foram criados:

1. `/tmp/habitinstance-src.txt` - Todas refs em src/
2. `/tmp/habitinstance-tests.txt` - Todas refs em tests/
3. `/tmp/habitinstance-files.txt` - Lista de arquivos únicos

**Manter para referência durante refatoração.**

---

**Conclusão Sprint 1.1:** Análise completa. 26 arquivos identificados, riscos mapeados, ordem de execução definida. Pronto para Sprint 1.2 (Migration).

**Próximo:** Sprint 1.2 - Criar e testar migration SQL
