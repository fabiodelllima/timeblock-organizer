# Roadmap Detalhado - Planejamento de Releases

- **Última Atualização:** 31 de Outubro de 2025
- **Horizonte de Planejamento:** 6 meses

Este documento fornece planejamento detalhado de releases com features específicas, timelines e critérios de sucesso para cada versão.

## Visão Geral das Versões

```terminal
v1.0.0 (ATUAL)      [OK] Baseline estável (16 Out 2025)
v1.1.0 (PRÓXIMO)     Event Reordering completo (ETA: +2 semanas)
v1.2.0 (MÉDIO)       HabitAtom + Relatórios (ETA: +4 semanas)
v1.3.0 (LONGO)       Living Documentation (ETA: +8 semanas)
v2.0.0 (FUTURO)      Sistema Completo (ETA: 6+ meses)
```

---

## v1.0.0 - Baseline (LANÇADO)

**Data de Release:** 16 de Outubro de 2025
**Status:** ESTÁVEL

### Features Entregues

**Funcionalidade Core:**

- Inicialização banco de dados SQLite
- Operações CRUD de eventos
- Listagem básica de eventos com filtros
- Suporte a formato brasileiro de tempo (7h, 14h30)
- Detecção de conflitos (warning apenas, não-bloqueante)
- Suporte a eventos que cruzam meia-noite

**Testes:**

- 141 testes passando
- 99% cobertura de código
- Regras de validação robustas

**Comandos CLI:**

```shell
timeblock init
timeblock add "Event" -s 9h -e 10h30
timeblock list [--day N] [--week N]
```

### Limitações Conhecidas

- Sem hábitos recorrentes
- Sem reordenação automática
- Sem relatórios ou analytics
- Sem gerenciamento de configuração
- CLI básica (sem TUI)

---

## v1.1.0 - Event Reordering (PRÓXIMO)

**Release Estimado:** 15 de Novembro de 2025 (2 semanas)
**Status:** 100% completo

### Escopo

**Conclusão Fase 1:**

- Sprint 1.4 resolvido
- Completar todos 4 sprints do Event Reordering Core
- 100% cobertura de testes para Fase 1

**Fase 2 - Integração:**

- Integrar reordenação com HabitInstanceService
- Integrar reordenação com TaskService
- Integrar reordenação com TimerService
- Comando CLI: `timeblock reorder preview`

**Fase 3 - Aplicação:**

- Implementar método `apply_reordering()`
- Confirmação interativa no CLI
- Rastreamento de histórico de reordenações
- Comandos CLI:
  - `timeblock reorder apply`
  - `timeblock reorder show-last`
  - Flag: `--auto-reorder` para aplicação automática

### Entregáveis

**Funcionalidade Core:**

```python
# Detecção automática de conflitos
$ timeblock task add "Reunião Emergencial" -s 10h30 -e 11h30
[AVISO] CONFLITO DETECTADO
A nova tarefa conflita com:
  - Deep Work (10:00-12:00, prioridade: BAIXA)

PROPOSTA DE REORDENAÇÃO:
  Mover "Deep Work" -> 11:30-13:30 (+1.5h atraso)

Aceitar? [S/n]: S
[OK] Reordenação aplicada!
```

**Conquistas Técnicas:**

- detect_conflicts() com 90%+ cobertura
- calculate_priorities() com regras claras
- propose_reordering() com soluções ótimas
- apply_reordering() com garantias de atomicidade
- Performance < 100ms para 500 eventos

### Critérios de Sucesso

- [ ] Sprint 1.4: 100% testes passando
- [ ] Fase 2: 3 services integrados
- [ ] CLI funcional (preview/apply)
- [ ] Mínimo 2 cenários E2E
- [ ] Benchmarks de performance atendidos
- [ ] Documentação atualizada
- [ ] Sem bugs críticos

### Estimativa de Esforço

- Correção Sprint 1.4: 2-3h
- Implementação Fase 2: 6-8h
- Implementação Fase 3: 6h
- Testes E2E: 5h (mínimo)
- Documentação: 2h
- **Total:** 21-24 horas (~3 dias úteis)

---

## v1.2.0 - HabitAtom + Relatórios (MÉDIO PRAZO)

**Release Estimado:** 15 de Dezembro de 2025 (4 semanas após v1.1)
**Status:** Planejado

### Escopo

**Breaking Change: HabitInstance -> HabitAtom**

- Renomear em toda codebase (50+ arquivos)
- Atualizar schema do banco com migração Alembic
- Manter compatibilidade retroativa temporariamente
- Warnings de deprecação no CLI

**Integração de Filosofia:**

- Reformulação do README com tema "Atomic Habits"
- Criação do documento PHILOSOPHY.md
- Conectar à metodologia de James Clear
- Posicionamento claro como ferramenta habit-first

**Implementação ReportService:**

```python
# Métricas core:
- completion_rate(start, end) -> float
- time_variance_analysis(habit_id) -> dict
- daily_summary(date) -> DailySummary
- weekly_summary(start_date) -> WeeklySummary
- habit_streak(habit_id) -> int
```

**Comandos CLI:**

```shell
timeblock report daily
timeblock report week
timeblock report habit <id>
timeblock report completion --since YYYY-MM-DD
```

**Gerenciamento de Config:**

- Suporte a .timeblockrc ou config.json
- Configuração de rotina padrão
- Configuração de horário de trabalho
- Preferências de notificação
- Preferências de formato (data, hora)

### Entregáveis

**Mudanças Core:**

- Zero referências a "HabitInstance" no código
- README transmite filosofia no primeiro parágrafo
- PHILOSOPHY.md com conexão clara a atomic habits
- ReportService com 4+ métricas
- Suporte a arquivo de config com gerenciamento CLI

**Conquistas Técnicas:**

- Cobertura -> 90%+
- 50+ testes com docstrings ricas
- Scripts de migração testados
- Compatibilidade retroativa verificada

### Critérios de Sucesso

- [ ] 0 referências a "HabitInstance" na codebase
- [ ] README transmite filosofia claramente
- [ ] Documento PHILOSOPHY.md completo
- [ ] ReportService funcional com 4+ métricas
- [ ] Gerenciamento de config funcionando
- [ ] Cobertura acima de 90%
- [ ] Sem regressões na funcionalidade existente
- [ ] Migração de v1.1 suave

### Estimativa de Esforço

- Refatoração HabitAtom: 44h
- ReportService: IMPLEMENTADO
- Gerenciamento config: 4h
- Documentação: 6h
- Testes e correções: 8h
- **Total:** 70 horas (~2 semanas úteis)

---

## v1.3.0 - Living Documentation (LONGO PRAZO)

- **Release Estimado:** 15 de Fevereiro de 2026 (8 semanas após v1.2)
- **Status:** Planejado

### Escopo

**Site de Documentação (MkDocs):**

- Geração de site estático
- Tema Material
- Funcionalidade de busca
- Suporte multi-idioma (EN/PT-BR)
- Deploy no GitHub Pages

**Specs BDD/Gherkin:**

- Integração pytest-bdd
- 5+ arquivos de features com cenários
- Testes como documentação
- Regras de negócio rastreáveis às specs

**Docs Auto-Geradas:**

- BUSINESS_RULES.md de docstrings de teste
- Referência API de anotações de código
- Diagramas de arquitetura de PlantUML
- Changelog de commits convencionais

### Entregáveis

**Site de Documentação:**

```terminal
https://username.github.io/timeblock-organizer/

Estrutura:
+-- Primeiros Passos
+-- Guia do Usuário
|   +-- Workflows
|   +-- Referência CLI
|   +-- FAQ
+-- Técnico
|   +-- Arquitetura
|   +-- Regras de Negócio (auto)
|   +-- Referência API (auto)
+-- Desenvolvimento
    +-- Contribuindo
    +-- Testes
    +-- Roadmap
```

**Testes BDD:**

```gherkin
Feature: Event Reordering
  Scenario: Resolução de conflito
    Given ...
    When ...
    Then ...
```

### Critérios de Sucesso

- [ ] Site MkDocs deployado no GitHub Pages
- [ ] 5+ arquivos de features Gherkin
- [ ] BUSINESS_RULES.md auto-gerada
- [ ] Tempo de onboarding < 30min para contribuidores
- [ ] Funcionalidade de busca operacional
- [ ] Todos diagramas renderizando corretamente

### Estimativa de Esforço

- Setup e conteúdo MkDocs: 12h
- Testes BDD: 20h
- Scripts de auto-geração: 8h
- Criação de diagramas: 6h
- Revisão e polimento: 4h
- **Total:** 50 horas (~1.5 semanas úteis)

---

## v2.0.0 - Sistema Completo (FUTURO)

- **Release Estimado:** Junho 2026 (6+ meses)
- **Status:** Visão

### Escopo

**TUI (Textual):**

- UI terminal rica
- Painéis divididos (agenda, timer, stats)
- Atalhos de teclado
- Suporte a mouse
- Atualizações em tempo real
- Notificações visuais

**Sync Google Calendar:**

- Sincronização bidirecional
- Autenticação OAuth
- Resolução de conflitos
- Sync seletiva por tags
- Fila offline para sync

**Analytics Avançados:**

- Rastreamento de metas
- Insights de habit stacking
- Agendamento preditivo
- Sugestões de otimização de tempo
- Relatórios customizados

**Performance:**

- Otimizado para 5000+ eventos
- Cache de queries
- Operações em lote
- Sync em background

### Critérios de Sucesso

- [ ] TUI totalmente funcional
- [ ] Sync de calendário funcionando
- [ ] Benchmarks de performance para grandes datasets
- [ ] Analytics avançados implementados
- [ ] Mobile-friendly (consideração para futuro)

### Estimativa de Esforço

- TUI: 20h
- Google Calendar: 30h
- Analytics avançados: 15h
- Otimização de performance: 10h
- Testes e polimento: 15h
- **Total:** 90 horas (~3 semanas úteis)

---

## Timeline de Breaking Changes

### v1.2.0 (Breaking)

- HabitInstance -> HabitAtom
- Migração de banco necessária
- Camada de compatibilidade retroativa para CLI (temporária)

### v2.0.0 (Breaking)

- Event -> Task (migração completa)
- Tuple returns removidos (ADR-008)
- Formato arquivo config v1 -> v2
- Versão mínima Python pode aumentar

---

## Dependências Entre Releases

```terminal
v1.0.0 (baseline)
   |
v1.1.0 (Event Reordering)
   | (requer reordenação estável)
v1.2.0 (Relatórios dependem de modelo de dados completo)
   | (requer funcionalidade sólida)
v1.3.0 (Documentação de sistema estável)
   | (requer arquitetura provada)
v2.0.0 (Features avançadas em fundação sólida)
```

---

## Fatores de Risco

### Riscos v1.1.0

- Correção Sprint 1.4 mais complexa que estimado
- Problemas de integração entre services
- Degradação de performance com reordenação

**Mitigação:** Estimativas conservadoras de tempo, testes minuciosos.

### Riscos v1.2.0

- Refatoração HabitAtom toca muitos arquivos (risco de regressão)
- Confusão de usuário com breaking changes
- Bugs em script de migração

**Mitigação:** Suite de testes abrangente, guia claro de migração, warnings de deprecação.

### Riscos v1.3.0

- Overhead de BDD sem benefício claro
- Peso de manutenção da documentação
- Scripts de auto-geração frágeis

**Mitigação:** Começar pequeno, validar valor, automatizar completamente ou não fazer.

### Riscos v2.0.0

- Scope creep (TUI + sync é ambicioso)
- Mudanças na API do Google
- Problemas de performance em escala

**Mitigação:** Abordagem modular, feature flags, testes extensivos de performance.

---

## Janelas de Manutenção

**Entre Releases:**

- Correções de bugs: Contínuas
- Atualizações de segurança: Imediatas
- Atualizações de dependências: Mensais
- Atualizações de documentação: Com cada release

**Suporte de Longo Prazo:**

- v1.0.0: Correções de segurança até v1.2.0
- v1.1.0: Correções de segurança até v1.3.0
- v1.2.0: LTS por 1 ano após v2.0.0

---

## Comunidade e Contribuições

**Timeline Open Source:**

- v1.1.0: Primeiras contribuições externas bem-vindas
- v1.2.0: CONTRIBUTING.md completo
- v1.3.0: Onboarding de contribuidor otimizado
- v2.0.0: Processo de contribuição maduro

---

- **Próxima Revisão:** Após release v1.1.0
- **Responsável:** Mantenedor do projeto
- **Relacionado:** [Débito Técnico](technical-debt.md) | [Status do Projeto](project-status.md)
