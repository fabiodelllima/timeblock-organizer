# ADR-057: Archive Lifecycle para Habit

- **Status:** Aceito
- **Data:** 2026-05-01
- **Issue de origem:** #61
- **ADRs relacionados:** ADR-007 (Service Layer), ADR-022 (Pause Tracking Simplification), ADR-036 (Task Lifecycle)
- **BRs relacionadas:** BR-HABIT-005 (Deleção de Habit — reescrita), BR-HABIT-006 (Archive Lifecycle — nova), BR-ROUTINE-006 (Soft Delete e Purge — precedente), BR-TASK-009 (Task lifecycle — precedente)

---

## Contexto

A issue #61, originalmente classificada como bug crítico de cascade de FK, foi reescopada na Sessão 28 (2026-05-01) após investigação técnica revelar que a correção via cascade hard delete violaria a política de preservação de histórico que sustenta o produto. O ATOMVS é um sistema orientado a rastreabilidade longitudinal de hábitos: streaks, completude histórica, tempo gasto e padrões de adesão são exatamente os dados que `delete_habit` com cascade destruiria silenciosamente. Cascade preserva integridade referencial à custa do histórico que define o produto.

A inspeção do trio de domínios principais revela que `Habit` é o único sem suporte a arquivamento. `Routine` adota soft delete por padrão com `--purge` para hard delete (BR-ROUTINE-006). `Task` adota soft delete via `cancelled_datetime` com `task purge` planejado (BR-TASK-009). `Habit`, em contraste, hoje executa hard delete imediato em `HabitService.delete_habit`, com `cascade_delete=True` no relacionamento `Habit.instances`, o que apaga todas as `HabitInstance` associadas. As `TimeLog` que apontam para essas `HabitInstance` ficam órfãs — situação que motivou a issue #61 originalmente como bug de integridade referencial.

A divergência arquitetural é portanto pré-existente à issue, e a resolução correta é alinhar `Habit` ao padrão dos demais domínios, não corrigir o bug com mais cascade.

---

## Decisão

Adotamos **archive lifecycle** para `Habit` como padrão de "deleção" via campo `archived_at: datetime | None = None` no modelo. A semântica do método público `delete_habit` na camada de service muda: em vez de remover o registro, marca `archived_at = utcnow()`. Um novo método `purge_habit` é introduzido para hard delete administrativo, exposto via comando CLI dedicado (`habit purge <id>`), sem affordance no dashboard da TUI nesta fase.

Operações de listagem padrão (`list_habits`, queries do dashboard, geração de instâncias) **excluem hábitos arquivados**. Operações de leitura por ID (`get_habit`) **não filtram**, permitindo inspeção administrativa e exibição em telas de detalhe quando necessário. A geração de `HabitInstance` em `HabitInstanceService.generate_instances` é restrita a hábitos com `archived_at IS NULL` — hábitos arquivados não geram instâncias futuras.

`purge_habit` mantém o comportamento de cascade existente (`cascade_delete=True` em `Habit.instances`) para assegurar que o usuário que escolhe purgar saiba estar apagando tudo. O comando CLI exibe confirmação explícita listando contagens de instâncias e time logs que serão destruídos antes de executar.

A reativação de hábito arquivado ocorre via campo de comando explícito, não como side effect de qualquer operação. `restore_habit(habit_id)` zera `archived_at` e o hábito volta às listagens.

---

## Alternativas consideradas

**Cascade hard delete (proposta original da issue #61).** Adicionar `ondelete="CASCADE"` em `TimeLog.habit_instance_id` e em `HabitInstance.habit_id` para resolver a violação de integridade referencial. Rejeitada porque destrói histórico de adesão, que é o produto. Não há cenário de uso em que destruir TimeLogs antigos seja o comportamento desejado de uma operação chamada "delete habit" pelo usuário comum.

**Cancelled_datetime ao estilo Task (BR-TASK-009).** Adotar exatamente a mesma nomenclatura usada em `Task` — campo `cancelled_datetime: datetime | None`. Rejeitada porque a semântica não casa: `Task.cancelled_datetime` significa "tarefa cancelada antes de executar", enquanto a operação proposta para `Habit` é "remover da rotina ativa preservando histórico". O termo "archived" reflete melhor a intenção e abre espaço para `cancelled` ter significado distinto se vier a ser modelado.

**Active flag boolean (`is_active: bool`).** Mais simples que `archived_at: datetime | None` porque não requer timestamp. Rejeitada porque perde informação de quando o arquivamento ocorreu — informação valiosa para análises do tipo "este hábito foi tentado por quanto tempo antes de ser abandonado". O custo de um `datetime` opcional vs um `bool` é mínimo (oito bytes por linha em SQLite) e o ganho informacional é substancial.

**Manter status quo (não fazer nada).** Rejeitada porque deixa a issue #61 como bug aberto e mantém divergência arquitetural com Routine e Task. Custo crescente conforme outros domínios futuros (eventos, projetos) precisem ser modelados.

---

## Consequências

### Positivas

A mudança preserva integralmente o histórico de adesão, que é o produto. Streaks calculados sobre `TimeLog` permanecem corretos mesmo após o usuário "deletar" um hábito da rotina ativa. Análises longitudinais (issue #49 — analytics temporal) ficam viáveis no longo prazo porque os dados não são destruídos.

A divergência arquitetural com `Routine` e `Task` é eliminada — os três domínios passam a seguir o mesmo padrão de archive-by-default, hard-delete-by-explicit-command. Code review, onboarding e documentação ficam mais consistentes.

`HabitService.delete_habit` mantém sua assinatura pública atual (assinatura `delete_habit(self, habit_id: int) -> bool`), o que minimiza ondas de mudança em chamadores. Apenas a semântica interna muda.

### Negativas

Toda query de listagem precisa adicionar filtro `WHERE archived_at IS NULL` ou equivalente Python sobre coleções já materializadas. O custo é distribuído por aproximadamente seis call sites em `services/habit_service.py`, `services/habit_instance_service.py` e `tui/screens/dashboard/loader.py`. Filtros esquecidos geram bug visível (hábitos arquivados aparecem em listas), o que é uma classe de bug fácil de detectar.

A migration adiciona uma coluna a uma tabela existente. SQLite versão 3.35+ suporta `ALTER TABLE ADD COLUMN`. Operação irreversível em SQLite < 3.35 (sem `DROP COLUMN`), mas isso não é regressão — o projeto já documenta esta limitação em outras migrations.

A descoberta de hábitos arquivados pelo usuário fica menos óbvia. A solução é UX-side: comando `habit list --archived` na CLI, e eventualmente uma seção colapsável na TUI (não nesta entrega).

### Neutras

`restore_habit` introduz um terceiro estado de operação ("ativo / arquivado / restaurado") que algumas equipes preferem evitar. Aqui é aceito porque o cenário de uso é claro: usuário arquiva por engano e quer reverter. Sem o restore, a única alternativa seria recriar manualmente, perdendo o histórico vinculado.

A relação `Habit.instances` mantém `cascade_delete=True` para suportar `purge_habit`. Isso significa que código que use `.delete(habit)` no SQLAlchemy diretamente (sem passar pelo service) ainda dispara o cascade — risco operacional de baixa relevância porque o projeto usa o pattern Service Layer (ADR-007), mas merece nota em revisões de código futuras.

---

## Plano de implementação resumido

Detalhamento completo em `docs/wiki/Session-29-Implementation-Plan-Habit-Archive.md` (rascunho local). Resumo:

1. **Schema:** adicionar `archived_at: datetime | None` em `Habit` (`src/timeblock/models/habit.py`).
2. **Migration:** `migration_004_habit_archive.py` segue o padrão das migrations 002 e 003 (PRAGMA table_info para idempotência, ALTER TABLE ADD COLUMN). Registro em `runner.py`.
3. **Service:** `delete_habit` muda semântica (set archived_at). Adicionar `purge_habit`, `restore_habit`, `list_active_habits`, `list_archived_habits`. Filtro `archived_at IS NULL` em queries de listagem padrão.
4. **HabitInstance generation:** `HabitInstanceService.generate_instances` filtra `Habit.archived_at IS NULL`.
5. **Dashboard loader:** `tui/screens/dashboard/loader.py` recebe filtro nas queries que listam hábitos.
6. **CLI:** comando `habit purge <id>` novo; `habit list --archived` opcional. Adapter de `habit delete` para refletir o novo comportamento (mensagem ao usuário muda de "deletado" para "arquivado").
7. **TUI:** sem mudanças visíveis nesta entrega. Mensagem de feedback ajusta de "Hábito deletado" para "Hábito arquivado" no dashboard.
8. **Testes:** classe `TestBRHabit006Archive` em `tests/unit/test_services/test_habit_service.py` cobrindo archive, purge, restore, listing semantics. BDD scenario novo em `tests/bdd/features/habit_archive.feature`. Integration test validando que `TimeLog` permanece intacto após archive.

A entrega é cabível em uma única MR para `develop` com ~12 commits atômicos. Estimativa: 2-3 dias de trabalho focado, distribuídos entre sessões.

---

## Errata de implementação (2026-06-05)

Durante a implementação na branch `feat/habit-archive-lifecycle`, o recon do código revelou duas imprecisões nas seções acima. Conforme o formato Nygard, o registro original é preservado e estas correções são anexadas.

1. **Timestamp (seção Decisão).** O texto menciona `archived_at = utcnow()`. A convenção real do projeto é `datetime.now()` (naive local), usada em `Task.cancelled_datetime`, `Task.completed_datetime` e `Routine.created_at`. A implementação adota `datetime.now()` por consistência com BR-TASK-009; "utcnow" deve ser lido como `datetime.now()`.

2. **Cascade do purge (seção Decisão).** O texto afirma que `purge_habit` "mantém o comportamento de cascade existente" para destruir os TimeLogs. Isso é incorreto: `cascade_delete=True` em `Habit.instances` alcança `HabitInstance`, mas não `TimeLog` — `TimeLog.habit_instance_id` é FK nullable sem `ondelete` e `HabitInstance` não declara relationship para `TimeLog`. Esse é precisamente o bug de integridade referencial que originou a issue #61 (TimeLogs órfãos). Portanto `purge_habit` remove explicitamente os TimeLogs das instâncias antes de deletar o Habit; sob `PRAGMA foreign_keys=ON`, sem essa remoção o purge falharia com FOREIGN KEY constraint failed.

---

## Referências

Fowler (2018) trata `archived_at` como caso canônico do padrão Soft Delete em capítulo sobre Database Patterns. Humble e Farley (2010) reforçam que migrações destrutivas de dados devem ser opt-in explícito do operador, não default — princípio aplicado aqui ao distinguir `delete_habit` (preserva) de `purge_habit` (destrói).

ADR-036 (Task Lifecycle) estabeleceu o precedente de campos `*_datetime: datetime | None` para marcar transições de estado. ADR-022 (Pause Tracking Simplification) estabeleceu o precedente de favorecer modelagem que preserva histórico em vez de modelagem que o resume.
