# Métricas de Sucesso - Critérios de Release

**Data:** 31 de Outubro de 2025

**Propósito:** Definir critérios claros e mensuráveis de sucesso para cada release

## Princípios Gerais

Todos releases devem atender critérios baseline:

1. **Zero Bugs Críticos** - Sem bugs P0/P1 bloqueando funcionalidade core
2. **Testes Passando** - 100% dos testes existentes passando
3. **Documentação Atualizada** - Changelog e README atualizados
4. **Performance Aceitável** - Sem regressão da versão anterior
5. **Segurança Validada** - Dependências atualizadas, sem vulnerabilidades conhecidas

---

## v1.0.0 - Baseline (LANÇADO)

**Data Release:** 16 de Outubro de 2025

**Status:** ATENDEU TODOS CRITÉRIOS [OK]

### Critérios de Aceitação (ATENDIDOS)

- [x] Inicialização banco funcionando
- [x] CRUD de eventos funcional
- [x] Comando list com filtros
- [x] 140+ testes passando
- [x] 99%+ cobertura
- [x] Suporte formato brasileiro de tempo
- [x] Regras validação aplicadas
- [x] Sem bugs críticos conhecidos

---

## v1.1.0 - Event Reordering

**Data Alvo:** 15 de Novembro de 2025

**Status:** EM PROGRESSO (75% completo)

### Requisitos de Funcionalidade Core

**MUST HAVE (Bloqueadores):**

- [ ] Sprint 1.4: 100% completo
- [ ] Todos testes Fase 1 passando (100%)
- [ ] detect_conflicts() funcionando corretamente
- [ ] calculate_priorities() com regras claras
- [ ] propose_reordering() gerando propostas válidas
- [ ] Integração Fase 2 completa (3 services)
- [ ] Comandos CLI funcionais:
  - [ ] `timeblock reorder preview`
  - [ ] `timeblock reorder apply`
  - [ ] Flag: `--auto-reorder`

### Requisitos de Teste

**MUST HAVE:**

- [ ] Fase 1 Event Reordering: completa
- [ ] Fase 1: 90%+ cobertura
- [ ] Fase 2: Testes integração para 3 services
- [ ] Mínimo 2 cenários E2E:
  1. [ ] Workflow completo de rotina
  2. [ ] Detecção e resolução de conflito

### Benchmarks de Performance

**MUST MEET:**

- [ ] detect_conflicts(): < 100ms para 100 eventos
- [ ] propose_reordering(): < 200ms para 100 eventos
- [ ] apply_reordering(): < 150ms para 100 eventos
- [ ] Sem memory leaks

### Checklist de Release

- [ ] Todas features MUST HAVE completas
- [ ] Todos testes MUST HAVE passando
- [ ] Todos quality gates MUST PASS atendidos
- [ ] Documentação atualizada
- [ ] Versão incrementada (1.0.0 -> 1.1.0)
- [ ] Git tag criada
- [ ] Release notes escritas
- [ ] Issues conhecidas documentadas

**DECISÃO DE SHIP:** GO / NO-GO baseado apenas em critérios MUST.

---

## Definição de "Done"

Um release está done quando:

1. Todos critérios MUST HAVE atendidos
2. Todos quality gates MUST PASS passaram
3. Checklist de release completo
4. Sign-off de:
   - Tech lead (qualidade código)
   - QA lead (testes completos)
   - Product owner (features corretas)
   - Documentation lead (docs atualizadas)

**Para projeto solo:** Todos papéis são mesma pessoa, mas checklist deve ser verificado.

---

**Cadência de Revisão:** Antes de cada planejamento de release

**Processo de Atualização:** Adicionar novas métricas conforme projeto evolui

**Responsável:** Release manager (ou dono do projeto)

**Relacionado:** [Status do Projeto](project-status.md) | [Roadmap](detailed-roadmap.md)
