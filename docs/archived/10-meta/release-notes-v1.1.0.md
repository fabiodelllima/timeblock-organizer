# Notas de Lançamento - v1.1.0

- **Data de Lançamento:** 01 de Novembro de 2025
- **Tag:** v1.1.0
- **Branch:** main
- **Commit:** 360aa48cc8a94bfcf6a43c7a4e71b901fd33cbbf

## Visão Geral

O release v1.1.0 adiciona o sistema completo de Event Reordering ao TimeBlock Organizer, permitindo detecção automática de conflitos de agendamento e reorganização inteligente de eventos baseada em prioridades.

## Funcionalidades Principais

### Sistema de Reordenamento de Eventos

Sistema completo de detecção e resolução de conflitos:

**Detecção Automática:**

- Identifica sobreposições entre eventos ao criar ou modificar agendamentos
- Analisa eventos em intervalo de data específico
- Classifica conflitos por tipo (OVERLAP, SEQUENTIAL)

**Cálculo de Prioridades:**

- CRITICAL: Eventos em progresso ou com prazo < 24h
- HIGH: Eventos pausados
- NORMAL: Eventos planejados com início < 1h
- LOW: Eventos planejados com início > 1h

**Reordenamento Inteligente:**

- Algoritmo sequencial que respeita prioridades
- Eventos de alta prioridade não são movidos
- Eventos de baixa prioridade são empilhados sequencialmente
- Calcula atraso total estimado

**Confirmação Interativa:**

- Preview formatado com tabelas Rich
- Opção de aplicar ou cancelar mudanças
- Flag --auto-approve para automação

### Novos Comandos CLI

```bash
# Detectar conflitos e aplicar com confirmação
timeblock reschedule <event_id>

# Apenas visualizar proposta
timeblock reschedule preview <event_id>

# Aplicar automaticamente
timeblock reschedule <event_id> --auto-approve

# Especificar tipo de evento
timeblock reschedule <event_id> --event-type habit_instance
```

### Integrações com Services

**TaskService:**

- `update_task()` retorna tuple[Task, ReorderingProposal | None]
- Detecta conflitos automaticamente quando datetime muda

**HabitInstanceService:**

- `adjust_instance_time()` retorna tuple[HabitInstance, ReorderingProposal | None]
- Integração completa com sistema de reordenamento

**TimerService:**

- `start_timer()` retorna tuple[TimeLog, ReorderingProposal | None]
- Detecta conflitos ao iniciar timer

## Estatísticas

**Código:**

- 4 novos arquivos em src/
- 6 novos arquivos de teste
- ~400 linhas de código de produção
- ~800 linhas de código de teste
- Proporção 1:2 (excelente)

**Testes:**

- 78 testes novos
- 219 testes totais (+55%)
- 100% passando
- 0 falhando

**Cobertura:**

```terminal
event_reordering_models.py       100%
event_reordering_service.py       90%
reschedule.py                     64%
```

**Commits:**

- 9 commits principais
- 3 fases implementadas
- 9 sprints concluídos

## Exemplo de Uso

```bash
# Cenário: Mover tarefa para horário conflitante
$ timeblock task update 5 --scheduled-datetime "2025-11-01 10:00"

[AVISO] 2 conflitos detectados

Conflitos Detectados:
+----------------+-----------------+------------+
| Evento         | Horário         | Prioridade |
+----------------+-----------------+------------+
| Deep Work      | 10:00 - 12:00   | LOW        |
| Code Review    | 11:00 - 11:30   | NORMAL     |
+----------------+-----------------+------------+

Mudanças Propostas:
+----------------+----------------+----------------+
| Evento         | Atual          | Proposto       |
+----------------+----------------+----------------+
| Deep Work      | 10:00 - 12:00  | 10:30 - 12:30  |
| Code Review    | 11:00 - 11:30  | 12:30 - 13:00  |
+----------------+----------------+----------------+

Atraso total estimado: 30 minutos

Aplicar reordenamento? [Y/n]: y
[OK] Reordenamento aplicado!
```

## Mudanças Incompatíveis

Nenhuma. Release 100% retrocompatível.

## Migração

Não requer migração. Todas as mudanças são aditivas.

## Documentação

**Novos Documentos:**

- `docs/10-meta/event-reordering-completed.md` - Conclusão técnica
- `docs/10-meta/sprints-v2.md` - Retrospectiva de sprints
- `CHANGELOG.md` - Histórico de mudanças

**Atualizados:**

- `docs/10-meta/project-status.md`
- `docs/10-meta/detailed-roadmap.md`
- `docs/01-architecture/` - Diagramas atualizados

## Problemas Conhecidos

Nenhum. Release estável e testado.

## Melhorias Futuras

Identificadas para próximas versões:

1. **Regras de Priorização Customizáveis**

   - Arquivo de configuração com regras personalizadas
   - Usuário define prioridades

2. **Histórico de Reordenamentos**

   - Tabela audit_log
   - Comando para visualizar histórico

3. **Sugestões de Horários Alternativos**

   - IA para sugerir melhor momento
   - Análise de padrões

4. **Preview Visual em TUI**
   - Timeline gráfica antes/depois
   - Interface Textual interativa

## Agradecimentos

Desenvolvimento completo por Fábio de Lima.

Ferramentas utilizadas:

- SQLAlchemy/SQLModel para ORM
- Rich para CLI formatada
- Pytest para testes
- Python 3.13

## Links

- [GitHub Release](https://github.com/fabiodelllima/timeblock-organizer/releases/tag/v1.1.0)
- [Documentação Completa](../README.md)
- [Conclusão Técnica](event-reordering-completed.md)
- [CHANGELOG](../../CHANGELOG.md)

---

**Próximo Release:** v1.2.0 - Refatoração HabitAtom (ETA: 2 semanas)
