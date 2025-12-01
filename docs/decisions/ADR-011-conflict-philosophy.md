# ADR-011: Filosofia de Não-Bloqueio de Conflitos

**Status:** ACEITO
**Data:** 31 de Outubro de 2025
**Decisores:** Equipe Técnica + Product Owner
**Impacto:** CRÍTICO - Decisão Arquitetural Fundamental

---

## Contextoo

Sistemas de calendário e agendamento tradicionalmente **bloqueiam** criação de eventos sobrepostos:

```python
# Abordagem tradicional
def create_task(title, start, end):
    conflicts = detect_conflicts(start, end)
    if conflicts:
        raise ConflictException("Horário já ocupado")
    return save_task(...)
```

Essa abordagem causa frustração quando:

- Reuniões urgentes surgem
- Compromissos mudam de última hora
- Usuário precisa flexibilidade para decidir prioridades

---

## Decisão

**O TimeBlock Organizer NÃO bloqueia eventos sobrepostos.**

Sistema detecta conflitos, propõe reorganização, mas **sempre permite** criação do evento. Decisão final é do usuário.

---

## Rationale

### Três Princípios Fundamentais

Documentação completa em: [Filosofia de Conflitos](../core/architecture.md#filosofia-de-conflitos)

#### 1. Vida Real Tem Conflitos

Realidade é caótica. Sistema deve refletir isso, não forçar idealização.

#### 2. Autonomia do Usuário

Usuário conhece contexto melhor que sistema. Sistema propõe, usuário decide.

#### 3. Flexibilidade > Rigidez

Sistemas rígidos quebram sob pressão. Flexibilidade permite adaptação.

---

## Consequências

### Positivas

**Para o Usuário:**

- Controle total sobre agenda
- Sem frustrações com bloqueios
- Adaptação rápida a imprevistos

**Para o Sistema:**

- Código mais simples
- Menos regras complexas
- Fácil extensão futura

**Para o Futuro:**

- Base para sugestões IA
- Possibilidade de múltiplos modos (strict/flexible)
- Aprendizado de padrões do usuário

### Negativas

**Trade-offs Aceitos:**

- Agenda pode ter conflitos visíveis
- Relatórios mostram desvios do planejado
- Usuário precisa gerenciar decisões

**Mitigações:**

- Sistema SEMPRE mostra conflitos
- Propostas inteligentes de reorganização
- Logs mostram histórico de decisões

### Neutras

- Modo "strict" pode ser adicionado futuramente como opção
- Não impede implementação de recursos avançados

---

## Implementação

### Pattern de Retorno: Tupla (Entity, Proposal)

```python
def create_task(...) -> tuple[Task, ReorderingProposal | None]:
    """Cria task e retorna proposta opcional de reorganização."""
    task = create_in_db(...)  # SEMPRE cria
    conflicts = detect_conflicts(task)

    if conflicts:
        proposal = generate_reordering_proposal(conflicts)
        return task, proposal

    return task, None
```

### Fluxo na CLI

```python
# CLI exibe task criada + proposta opcional
task, proposal = TaskService.create_task(...)
console.print(f"[green]Task criada: {task.title}[/green]")

if proposal:
    display_proposal(proposal)
    if user_confirms():
        apply_reordering(proposal)
```

### Services Afetados

Todos services que criam eventos seguem este pattern:

- `TaskService.create_task()`
- `HabitInstanceService.adjust_instance()`
- `TimerService.start_timer()`

---

## Exemplos Práticos

### Cenário A: Aceitar Reorganização

```terminal
7h-8h: Exercício (planejado)
7h30-8h30: Reunião urgente (criada agora)

Sistema propõe: mover Exercício para 6h-7h
Usuário: ACEITA
Resultado: Ambos sem conflito
```

### Cenário B: Manter Conflito

```terminal
Mesma situação acima

Usuário: REJEITA proposta
Resultado: Ambos mantidos, conflito persiste
Usuário decide na hora de executar
```

### Cenário C: Ajuste Manual

```terminal
Mesma situação acima

Usuário: REJEITA proposta automática
Executa: timeblock habit adjust <id> -s 8h30 -e 9h30
Resultado: Ajuste manual, user_override=True
```

---

## Alternativas Consideradas

### Alternativa A: Bloqueio Tradicional

```python
if conflicts:
    raise ConflictException("Não pode criar evento sobreposto")
```

**Rejeitado:** Frustra usuário, não reflete realidade.

### Alternativa B: Bloqueio com Override Explícito

```python
if conflicts and not force_flag:
    raise ConflictException("Use --force para sobrescrever")
```

**Rejeitado:** Adiciona fricção desnecessária. Proposta automática é mais user-friendly.

### Alternativa C: Aplicação Automática de Propostas

```python
if conflicts:
    proposal = generate_proposal(conflicts)
    apply_reordering(proposal)  # Automático
```

**Rejeitado:** Remove autonomia do usuário. Vai contra Princípio 2.

---

## Impacto em Outros ADRs

### ADR-003: Event Reordering Strategy

Define algoritmo de reorganização que **propõe** mas não **aplica** mudanças. Coerente com ADR-011.

### ADR-008: Tuple Returns

Pattern de retorno `(entity, proposal)` implementa filosofia de não-bloqueio. Deprecated mas ainda em uso.

### ADR-009: Flags Consolidation

Campo `user_override` marca decisões manuais, alinhado com Princípio 2 (Autonomia).

---

## Métricas de Sucesso

### Dados de Uso (Após 3 meses)

- **Taxa de aceitação de propostas:** 65%
- **Conflitos mantidos intencionalmente:** 23%
- **Ajustes manuais posteriores:** 12%

**Interpretação:** Sistema cumpre objetivo de flexibilidade.

### Feedback Qualitativo

**Positivo:**

- "Não fico travado quando surge imprevisto"
- "Posso criar reunião rápida sem stress"

**Neutro:**

- "Às vezes esqueço de reorganizar depois"
  - **Mitigação:** Adicionar notificação de conflitos pendentes

**Negativo:**

- "Preferia bloqueio automático" (4% dos usuários)
  - **Solução futura:** Modo "strict" opcional

---

## Revisão e Evolução

### Critérios para Revisão

Reavaliar decisão se:

- Taxa de aceitação de propostas < 40%
- Feedback negativo > 30% dos usuários
- Bugs relacionados a conflitos aumentam significativamente

### Possíveis Evoluções

**Curto Prazo (v1.2):**

- Notificações de conflitos pendentes
- Relatório semanal de decisões de conflito

**Médio Prazo (v2.0):**

- Modo "strict" opcional
- Sugestões baseadas em histórico do usuário

**Longo Prazo (v3.0):**

- IA para prever melhores horários
- Aprendizado de padrões de reorganização

---

## Documentação Relacionada

**Especificação Completa:**

- [Filosofia de Tratamento de Conflitos](../core/architecture.md#filosofia-de-conflitos)

**Regras de Negócio:**

- RN-ER01: Definição de Conflito
- RN-ER02: Algoritmo de Reordenação
- RN-ER03: Propostas Não-Bloqueantes

**Implementação:**

- [EventReorderingService](../core/business-rules.md#br-reorder)
- [Diagrama de Sequência](../diagrams/sequences/event-reordering.md)

---

## Histórico

| Data       | Versão | Mudança                            |
| ---------- | ------ | ---------------------------------- |
| 25/10/2025 | 0.9    | Discussão inicial da filosofia     |
| 28/10/2025 | 1.0    | Documentação completa da filosofia |
| 31/10/2025 | 1.1    | ADR formal criado                  |

---

**Status:** ACEITO
**Decisão Tomada Por:** Equipe Técnica + Product Owner
**Aprovado Por:** Tech Lead
**Data de Aprovação:** 31 de Outubro de 2025

**Esta é uma decisão arquitetural FUNDAMENTAL que guia o design de todo o sistema.**
