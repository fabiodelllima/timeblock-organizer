# Filosofia de Tratamento de Conflitos

- **Versão:** 1.0.0
- **Data:** 31 de Outubro de 2025
- **Status:** DECISÃO ARQUITETURAL FUNDAMENTAL

---

## 1. DECISÃO FUNDAMENTAL

O TimeBlock Organizer **não bloqueia** eventos sobrepostos intencionalmente. Esta é uma decisão de design fundamental que permeia todo o sistema.

---

## 2. TRÊS PRINCÍPIOS FUNDAMENTAIS

### 2.1 Princípio 1: Vida Real Tem Conflitos

**Premissa:**
A vida real é caótica e imprevisível. Reuniões de emergência surgem sem aviso, compromissos mudam de última hora, e prioridades se ajustam dinamicamente.

**Decisão de Design:**
O sistema deve refletir a realidade, não uma idealização dela. Forçar uma agenda perfeitamente organizada sem sobreposições cria frustração quando a realidade inevitavelmente diverge.

**Exemplo Prático:**

```terminal
Planejado:
7h-8h: Exercício (hábito diário)
8h-9h: Café da manhã

Realidade:
7h30: Reunião urgente com cliente (não pode recusar)

Sistema tradicional: Bloqueia criação da reunião
TimeBlock: Permite criar reunião, oferece reorganização OPCIONAL
```

### 2.2 Princípio 2: Autonomia do Usuário

**Premissa:**
O usuário é quem melhor conhece suas prioridades e contexto. Nenhum sistema, por mais inteligente que seja, pode tomar decisões melhores que o próprio usuário sobre o que fazer em momentos de conflito.

**Decisão de Design:**
O sistema detecta conflitos, propõe soluções, mas NUNCA impõe decisões. O usuário sempre tem a palavra final.

**Fluxo de Decisão:**

```terminal
1. Sistema detecta conflito
2. Sistema gera proposta de reorganização
3. Sistema EXIBE proposta ao usuário
4. Usuário decide:
   a) Aceitar proposta
   b) Ajustar manualmente
   c) Manter ambos (executar parcialmente)
   d) Ignorar e decidir na hora
```

### 2.3 Princípio 3: Flexibilidade > Rigidez

**Premissa:**
Sistemas rígidos quebram sob pressão. Sistemas flexíveis se adaptam.

**Decisão de Design:**
Preferimos um sistema que permite decisões contextuais a um que impõe estruturas artificiais. Melhor ter dois eventos sobrepostos e deixar o usuário decidir na hora do que bloquear um evento importante.

**Trade-offs Aceitos:**

**Perda aceita:**

- Agenda pode ter "conflitos visíveis"
- TimeLog pode mostrar execução não-ideal
- Relatórios podem mostrar desvios do planejado

**Ganho obtido:**

- Usuário nunca fica travado
- Sistema se adapta à realidade
- Menos frustração com bloqueios
- Mais controle para o usuário

---

## 3. IMPLEMENTAÇÃO TÉCNICA

### 3.1 Pattern de Retorno: Tupla (Entity, Proposal)

**Assinatura Padrão:**

```python
def create_task(...) -> tuple[Task, ReorderingProposal | None]:
    """
    Cria task e detecta conflitos, mas NÃO bloqueia criação.

    Returns:
        tuple[Task, ReorderingProposal | None]:
            - Task criada (SEMPRE retorna, mesmo com conflitos)
            - Proposal de reorganização (None se sem conflitos)
    """
    task = create_in_db(...)  # SEMPRE cria
    conflicts = detect_conflicts(task)

    if conflicts:
        proposal = generate_reordering_proposal(conflicts)
        return task, proposal

    return task, None
```

**Princípio:** A entidade é SEMPRE criada, independente de conflitos. A proposta é OPCIONAL.

### 3.2 Fluxo na CLI

```python
# Exemplo: timeblock task add "Reunião" -d 2025-10-31 -s 14h -e 15h

def handle_task_add(...):
    # Service cria task e detecta conflitos
    task, proposal = TaskService.create_task(...)

    # Task FOI CRIADA independente de conflitos
    console.print(f"[green]Task criada: {task.title}[/green]")

    # Se há conflitos, mostrar OPCIONALMENTE
    if proposal and proposal.has_conflicts:
        display_proposal(proposal)

        if click.confirm("Deseja aplicar reorganização?"):
            apply_reordering(proposal)
            console.print("[green]Agenda reorganizada[/green]")
        else:
            console.print("[yellow]Task mantida, conflitos persistem[/yellow]")

    return task
```

---

## 4. CENÁRIOS DE USO

### 4.1 Cenário A: Aceitar Proposta de Reorganização

```terminal
Situação:
- Hábito "Exercício" 7h-8h
- Task "Reunião" criada para 7h30-8h30

Sistema:
1. Cria task (SEMPRE cria)
2. Detecta conflito de 30min
3. Propõe: mover Exercício para 6h-7h

Usuário:
- Aceita proposta
- Sistema aplica mudanças

Resultado:
- 6h-7h: Exercício (ajustado)
- 7h30-8h30: Reunião (como criado)
```

### 4.2 Cenário B: Rejeitar e Manter Conflito

```terminal
Situação:
- Mesmo conflito acima

Usuário:
- Rejeita proposta
- Mantém ambos como estão

Resultado:
- 7h-8h: Exercício (original)
- 7h30-8h30: Reunião (como criado)
- Conflito visível na agenda
- Usuário decide na hora de executar
```

### 4.3 Cenário C: Ajuste Manual

```terminal
Situação:
- Mesmo conflito acima

Usuário:
- Rejeita proposta automática
- Executa: timeblock habit edit <id> -s 8h30 -e 9h30
- Sistema marca user_override=True

Resultado:
- 7h30-8h30: Reunião (como criado)
- 8h30-9h30: Exercício (ajustado manualmente)
- Sem conflitos
```

---

## 5. BENEFÍCIOS DESTA ABORDAGEM

### 5.1 Para o Usuário

- **Controle Total:** Usuário decide suas prioridades, não o sistema
- **Sem Frustrações:** Nunca fica travado por causa de bloqueios
- **Adaptação Rápida:** Pode ajustar agenda quando surgem imprevistos
- **Realismo:** Sistema reflete a realidade caótica da vida

### 5.2 Para o Sistema

- **Simplicidade:** Menos regras complexas para gerenciar
- **Manutenibilidade:** Código mais simples, menos bugs
- **Extensibilidade:** Fácil adicionar novos tipos de eventos
- **Testabilidade:** Menos estados impossíveis para testar

### 5.3 Para o Futuro

- **IA Amigável:** Fácil adicionar sugestões baseadas em IA
- **Múltiplos Modos:** Possível adicionar modo "strict" como opção
- **Personalização:** Usuários podem configurar nível de rigidez
- **Aprendizado:** Sistema pode aprender padrões do usuário

---

## 6. ANTI-PADRÕES A EVITAR

### 6.1 NÃO Bloquear Criação de Eventos

```python
# [ERRADO] Bloquear criação
def create_task(...):
    conflicts = detect_conflicts(...)
    if conflicts:
        raise ConflictException("Não pode criar task com conflitos")
    return create_in_db(...)

# [CORRETO] Criar e informar
def create_task(...):
    task = create_in_db(...)  # SEMPRE cria
    conflicts = detect_conflicts(task)
    proposal = generate_proposal(conflicts) if conflicts else None
    return task, proposal
```

### 6.2 NÃO Forçar Reorganização Automática

```python
# [ERRADO] Aplicar automaticamente
def create_task(...):
    task = create_in_db(...)
    conflicts = detect_conflicts(task)
    if conflicts:
        proposal = generate_proposal(conflicts)
        apply_reordering(proposal)  # NUNCA fazer isso!
    return task

# [CORRETO] Propor e deixar usuário decidir
def create_task(...):
    task = create_in_db(...)
    conflicts = detect_conflicts(task)
    proposal = generate_proposal(conflicts) if conflicts else None
    return task, proposal  # Usuário decide
```

---

## 7. DECISÕES RELACIONADAS

### 7.1 ADRs Relevantes

- **ADR-003:** Event Reordering Strategy
- **ADR-008:** Tuple Returns
- **ADR-011:** Esta filosofia de conflitos

### 7.2 Regras de Negócio Relacionadas

- **RN-ER01:** Definição de Conflito
- **RN-ER02:** Algoritmo de Reordenação
- **RN-ER03:** Propostas Não-Bloqueantes

### 7.3 Código-Fonte Relacionado

**Services:**

- `cli/src/timeblock/services/event_reordering_service.py`
- `cli/src/timeblock/services/task_service.py`
- `cli/src/timeblock/services/habit_instance_service.py`

**CLI:**

- `cli/src/timeblock/commands/task.py`
- `cli/src/timeblock/commands/habit.py`

---

## 8. PERGUNTAS FREQUENTES

**P: Por que não bloquear conflitos?**
R: Porque a vida real tem conflitos inevitáveis. Bloquear causa frustração.

**P: Isso não deixa a agenda bagunçada?**
R: Não necessariamente. O sistema OFERECE reorganização. Usuário decide se aceita.

**P: E se o usuário nunca reorganizar?**
R: Isso é escolha dele. Sistema mostra conflitos e oferece soluções, mas não força.

**P: Como isso afeta relatórios?**
R: Relatórios mostram realidade: tempo planejado vs executado. Isso é informação valiosa.

**P: Posso ter um modo "strict" que bloqueia?**
R: Futuramente sim. Mas o padrão sempre será "flexible" (não-bloqueante).

---

## 9. HISTÓRICO DE MUDANÇAS

| Data       | Versão | Mudança                      |
| ---------- | ------ | ---------------------------- |
| 31/10/2025 | 1.0.0  | Criação inicial do documento |

---

- **Documento:** conflict-philosophy.md
- **Localização:** `docs/04-specifications/philosophy/conflict-philosophy.md`
- **Referências:** master-integration-document.md, ADR-003, ADR-008
