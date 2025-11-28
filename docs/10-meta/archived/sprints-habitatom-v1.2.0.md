# Sprints v1.2.0 - Refatoração HabitAtom

- **Data:** 02 de Novembro de 2025
- **Status:** PLANEJADO
- **Estimativa Total:** 44h (~1-2 semanas)

## Contexto

Renomear HabitInstance → HabitAtom em todo o sistema para refletir a filosofia de "Atomic Habits" de James Clear. Esta mudança posiciona o sistema filosoficamente e melhora a semântica do código.

**Motivação:**

- HabitAtom representa unidade atômica de execução
- Pequeno o suficiente para ser executável
- Grande o suficiente para fazer diferença
- Composição ao longo do tempo resulta em transformação

**Escopo:**

- 56 referências no código a serem atualizadas
- Migration do banco de dados
- Atualização de todos os testes
- Documentação completa

---

## Sprint 1.1: Preparação e Análise de Impacto

**Duração:** 4h
**Status:** PLANEJADO

### Objetivos

1. Mapear todas as ocorrências de HabitInstance no código
2. Identificar dependências externas (imports, type hints)
3. Criar checklist de arquivos a modificar
4. Planejar estratégia de migration do banco
5. Definir ordem de refatoração

### Entregas

- [ ] Documento de análise de impacto
- [ ] Checklist de arquivos (modelos, services, comandos, testes)
- [ ] Script de migration SQL
- [ ] Plano de rollback

### Arquivos a Analisar

```bash
# Encontrar todas as referências
grep -r "HabitInstance" cli/src/ --include="*.py"
grep -r "habit_instance" cli/src/ --include="*.py"
grep -r "habitinstance" cli/src/ --include="*.py"
```

---

## Sprint 1.2: Migration do Banco de Dados

**Duração:** 3h
**Status:** PLANEJADO

### Objetivos

1. Criar migration Alembic para renomear tabela
2. Testar migration em banco de desenvolvimento
3. Criar script de rollback
4. Documentar processo

### Entregas

- [ ] Migration file: `versions/XXX_rename_habitinstance_to_habitatom.py`
- [ ] Script de teste de migration
- [ ] Documentação de rollback
- [ ] Backup procedure documentado

### Migration SQL

```sql
-- Renomear tabela
ALTER TABLE habitinstance RENAME TO habitatom;

-- Atualizar índices se necessário
-- Verificar foreign keys
-- Testar queries existentes
```

---

## Sprint 1.3: Refatoração do Modelo

**Duração:** 4h
**Status:** PLANEJADO

### Objetivos

1. Renomear classe HabitInstance → HabitAtom
2. Renomear HabitInstanceStatus → HabitAtomStatus
3. Atualizar `__tablename__`
4. Atualizar todos os imports no módulo models
5. Verificar type hints e relationships

### Entregas

- [ ] `models/habit_atom.py` (renomeado de habit_instance.py)
- [ ] HabitAtomStatus enum
- [ ] Atualizar `models/__init__.py`
- [ ] Atualizar relacionamentos em Habit

### Arquivos a Modificar

```
cli/src/timeblock/models/habit_instance.py → habit_atom.py
cli/src/timeblock/models/__init__.py
cli/src/timeblock/models/habit.py (relationships)
```

---

## Sprint 1.4: Refatoração do Service

**Duração:** 6h
**Status:** PLANEJADO

### Objetivos

1. Renomear HabitInstanceService → HabitAtomService
2. Atualizar todos os métodos
3. Atualizar docstrings e comentários
4. Atualizar type hints
5. Manter compatibilidade com Event Reordering

### Entregas

- [ ] `services/habit_atom_service.py`
- [ ] Atualizar `services/__init__.py`
- [ ] Verificar integração com EventReorderingService
- [ ] Atualizar imports em todos os services

### Métodos a Atualizar

```python
# Antes
class HabitInstanceService:
    def generate_instances(...)
    def adjust_instance_time(...)
    def get_instance(...)

# Depois
class HabitAtomService:
    def generate_atoms(...)
    def adjust_atom_time(...)
    def get_atom(...)
```

---

## Sprint 1.5: Refatoração dos Comandos CLI

**Duração:** 5h
**Status:** PLANEJADO

### Objetivos

1. Atualizar comando `habit adjust`
2. Atualizar comando `schedule`
3. Atualizar mensagens de usuário
4. Atualizar help texts
5. Manter backward compatibility onde possível

### Entregas

- [ ] Atualizar `commands/habit.py`
- [ ] Atualizar `commands/schedule.py`
- [ ] Atualizar textos de ajuda
- [ ] Atualizar mensagens de erro/sucesso

### Comandos Afetados

```bash
timeblock habit adjust <id>     # Mensagens usam "atom" agora
timeblock schedule generate     # Gera atoms, não instances
timeblock schedule list         # Lista atoms
```

---

## Sprint 1.6: Atualização de Testes Unitários

**Duração:** 8h
**Status:** PLANEJADO

### Objetivos

1. Atualizar testes de models
2. Atualizar testes de services
3. Atualizar fixtures
4. Garantir 100% dos testes passando
5. Adicionar testes de migration

### Entregas

- [ ] Atualizar `test_models/test_habit_atom.py`
- [ ] Atualizar `test_services/test_habit_atom_service.py`
- [ ] Atualizar fixtures que usam HabitInstance
- [ ] Testes de migration
- [ ] 100% testes passando

### Testes a Modificar

```terminal
tests/unit/test_models/test_habit_instance.py → test_habit_atom.py
tests/unit/test_services/test_habit_instance_service.py → test_habit_atom_service.py
tests/unit/test_services/test_event_reordering*.py (verificar integrações)
tests/unit/test_commands/test_habit.py
tests/unit/test_commands/test_schedule.py
```

---

## Sprint 1.7: Atualização de Testes de Integração

**Duração:** 6h
**Status:** PLANEJADO

### Objetivos

1. Atualizar testes de integração
2. Testar migration em ambiente real
3. Verificar Event Reordering ainda funciona
4. Testes end-to-end básicos

### Entregas

- [ ] Testes de integração atualizados
- [ ] Testes de migration executados
- [ ] Verificação de regressão do Event Reordering
- [ ] Documentação de casos de teste

---

## Sprint 1.8: Documentação e Finalização

**Duração:** 8h
**Status:** PLANEJADO

### Objetivos

1. Atualizar toda documentação técnica
2. Criar guia de migração para usuários
3. Atualizar filosofia Atomic Habits nos docs
4. Atualizar diagramas de arquitetura
5. Criar release notes

### Entregas

- [ ] Atualizar `docs/01-architecture/`
- [ ] Atualizar `docs/04-specifications/philosophy/atomic-habits.md`
- [ ] Criar `docs/10-meta/migration-guide-v1.2.0.md`
- [ ] Atualizar glossário
- [ ] Criar release notes v1.2.0
- [ ] Atualizar CHANGELOG.md

### Documentos a Atualizar

```terminal
docs/01-architecture/05-building-blocks.md
docs/01-architecture/12-glossary.md
docs/03-decisions/004-habit-vs-instance.md
docs/04-specifications/philosophy/atomic-habits.md
docs/05-api/services.md
docs/08-user-guides/ (todos os guias de usuário)
```

---

## Checklist de Validação Final

Antes de release v1.2.0, verificar:

- [ ] Todas as 56 referências a HabitInstance atualizadas
- [ ] Migration testada em banco real
- [ ] 100% dos testes passando (unitários + integração)
- [ ] Event Reordering ainda funciona (não houve regressão)
- [ ] Documentação completa atualizada
- [ ] Guia de migração para usuários
- [ ] CHANGELOG atualizado
- [ ] Release notes criadas
- [ ] Nenhum breaking change não documentado

---

## Riscos e Mitigações

### Risco 1: Regressão no Event Reordering

**Probabilidade:** MÉDIA
**Impacto:** ALTO

**Mitigação:**

- Executar todos os 78 testes de Event Reordering
- Testes de integração específicos
- Verificar tuple returns ainda funcionam

### Risco 2: Migration Falha

**Probabilidade:** BAIXA
**Impacto:** CRÍTICO

**Mitigação:**

- Testar migration em ambiente isolado
- Script de rollback testado
- Backup antes de migration
- Documentação clara de recovery

### Risco 3: Usuários com Código Dependente

**Probabilidade:** BAIXA (v1.1 é recente)
**Impacto:** MÉDIO

**Mitigação:**

- Guia de migração detalhado
- Breaking change bem documentado
- Período de deprecation warnings (considerar)

---

## Estimativa de Tempo

| Sprint                | Duração | Crítico |
| --------------------- | ------- | ------- |
| 1.1 Análise           | 4h      | SIM     |
| 1.2 Migration         | 3h      | SIM     |
| 1.3 Modelo            | 4h      | SIM     |
| 1.4 Service           | 6h      | SIM     |
| 1.5 CLI               | 5h      | SIM     |
| 1.6 Testes Unit       | 8h      | SIM     |
| 1.7 Testes Integração | 6h      | SIM     |
| 1.8 Documentação      | 8h      | MÉDIA   |
| **TOTAL**             | **44h** |         |

**Distribuição:**

- Semana 1 (20h): Sprints 1.1-1.4
- Semana 2 (24h): Sprints 1.5-1.8

---

## Critérios de Sucesso

- [ ] 0 referências a "HabitInstance" no código
- [ ] 100% dos testes passando
- [ ] Migration executada com sucesso
- [ ] Event Reordering sem regressões
- [ ] Documentação 100% atualizada
- [ ] Guia de migração claro
- [ ] Release v1.2.0 publicado

---

**Próxima Atualização:** Início da implementação (Sprint 1.1)
