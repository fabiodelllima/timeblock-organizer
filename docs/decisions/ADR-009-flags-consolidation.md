# ADR-009: Consolidação de Flags Override

**Status:** PROPOSTO
**Data:** 31 de Outubro de 2025
**Decisores:** Equipe Técnica
**Contexto Técnico:** Python, SQLModel, SQLite

---

## Contextoo

O modelo `HabitInstance` possui atualmente dois campos booleanos similares que causam confusão:

```python
class HabitInstance(SQLModel, table=True):
    manually_adjusted: bool = Field(default=False)
    user_override: bool = Field(default=False)
```

**Problemas identificados:**

1. **Semântica não clara:** Quando usar cada flag?
2. **Redundância potencial:** Ambos parecem indicar "usuário modificou"
3. **Inconsistência no código:** Setados em momentos diferentes sem critério claro
4. **Dificuldade de manutenção:** Desenvolvedor precisa decidir qual usar

**Exemplo da confusão:**

```python
# Código atual em diferentes pontos:
instance.manually_adjusted = True  # Ajuste de horário?
instance.user_override = True       # Decisão consciente?
# Quando usar qual? Diferença prática?
```

---

## Decisão

**Consolidar em um único campo: `user_override`**

Remover `manually_adjusted` e manter apenas `user_override` com semântica clara e bem documentada.

---

## Rationale

### Por que consolidar?

1. **Princípio YAGNI:** Não precisamos de dois flags para expressar a mesma informação
2. **Simplicidade:** Um campo é mais fácil de entender e manter
3. **Consistência:** Elimina ambiguidade no código
4. **Menor superfície de bugs:** Menos estado para sincronizar

### Por que manter `user_override`?

1. **Nome mais descritivo:** Expressa claramente que usuário sobrescreveu decisão do sistema
2. **Alinhamento com filosofia:** Sistema propõe, usuário decide (override)
3. **Já usado na documentação:** Documentação atual referencia `user_override`

### Por que não manter ambos?

Consideramos manter com semântica diferenciada:

- `manually_adjusted`: Horários ajustados (pode ser revertido)
- `user_override`: Decisão permanente de não seguir template

**Rejeitado porque:**

- Complexidade desnecessária para MVP
- Não há caso de uso real que requeira distinção
- Pode ser adicionado futuramente se necessário (YAGNI)

---

## Consequências

### Positivas

- **Código mais limpo:** Menos campos para gerenciar
- **Menos decisões:** Desenvolvedor sabe exatamente qual campo usar
- **Testes mais simples:** Menos combinações de estado para testar
- **Documentação mais clara:** Um conceito para explicar

### Negativas

- **Migration necessária:** Precisa consolidar dados existentes
- **Breaking change:** Código que usava `manually_adjusted` precisa atualização

### Neutras

- **Banco de dados:** Adicionar migration para remover coluna

---

## Implementação

### Passo 1: Migration SQL

```python
# cli/migrations/versions/xxx_remove_manually_adjusted.py
from alembic import op

def upgrade():
    # Consolidar flags: se qualquer um for True, user_override = True
    op.execute("""
        UPDATE habit_instance
        SET user_override = TRUE
        WHERE manually_adjusted = TRUE
    """)

    # Remover coluna
    op.drop_column('habit_instance', 'manually_adjusted')

def downgrade():
    # Recriar coluna
    op.add_column('habit_instance',
        sa.Column('manually_adjusted', sa.Boolean(),
                  server_default='false', nullable=False))
```

### Passo 2: Atualizar Model

```python
class HabitInstance(SQLModel, table=True):
    """Instância de hábito para data específica.

    Attributes:
        user_override: True se usuário modificou manualmente esta instância.
                      Indica que usuário tomou decisão consciente de não
                      seguir template do hábito. Mudanças via CLI ou ajustes
                      manuais de horário setam este flag.
    """
    # ... outros campos ...

    user_override: bool = Field(
        default=False,
        description="Indica se usuário modificou esta instância manualmente"
    )
    # [REMOVIDO] manually_adjusted: bool
```

### Passo 3: Atualizar Services

```python
# cli/src/timeblock/services/habit_instance_service.py

def adjust_instance(instance_id: int, new_start: time, new_end: time) -> HabitInstance:
    """Ajusta horários de instância e marca user_override."""
    instance = get_instance(instance_id)
    instance.scheduled_start = new_start
    instance.scheduled_end = new_end
    instance.user_override = True  # [ANTES: manually_adjusted = True]
    session.commit()
    return instance
```

### Passo 4: Atualizar Testes

```python
def test_adjust_marks_override():
    """Ajustar instância seta user_override."""
    instance = create_test_instance()
    adjusted = HabitInstanceService.adjust(instance.id, time(8,0), time(9,0))

    assert adjusted.user_override is True
    # [REMOVIDO] assert adjusted.manually_adjusted is True
```

---

## Impacto em Outros Componentes

### HabitInstanceService

- Atualizar `adjust_instance()` para usar `user_override`
- Remover referências a `manually_adjusted`

### RoutineService

- Sync de rotina verifica `user_override` antes de atualizar instâncias

### CLI Commands

- `timeblock habit adjust` continua funcionando igual
- Output pode mencionar "override marcado"

### Relatórios/Analytics

- TimeLog referencia `user_override` para distinguir planejado vs executado

---

## Alternativas Consideradas

### Alternativa A: Manter Ambos com Semântica Clara

```python
manually_adjusted: bool  # Horários ajustados (revertível)
user_override: bool      # Decisão permanente (não revertível)
```

**Rejeitado:** Complexidade não justificada para MVP. Pode ser adicionado depois se surgir necessidade real.

### Alternativa B: Renomear para `modified_by_user`

**Rejeitado:** `user_override` é mais específico e alinha com filosofia do sistema.

### Alternativa C: Usar Enum de Estados

```python
modification_type: Literal["none", "adjusted", "overridden"]
```

**Rejeitado:** Over-engineering para caso simples. Boolean é suficiente.

---

## Notas de Implementação

### Timeline

- Sprint atual: Criar migration
- Próximo sprint: Aplicar migration em dev
- Release v1.2.0: Deploy para produção

### Riscos

**Baixo:** Migration é simples e direta. Consolidação é segura (OR lógico).

### Rollback

Migration possui `downgrade()` que recria coluna. Dados podem não ser recuperados perfeitamente mas sistema continua funcional.

---

## Referências

**Documentação:**

- [Modelo HabitInstance](../core/business-rules.md#habitinstance)
- [Filosofia de Conflitos](../core/architecture.md#filosofia-de-conflitos)

**Issues:**

- #P003: Flags Redundantes

**ADRs Relacionados:**

- ADR-004: Habit vs Instance Separation
- ADR-011: Filosofia de Conflitos

---

## Histórico

| Data       | Versão | Mudança                                          |
| ---------- | ------ | ------------------------------------------------ |
| 31/10/2025 | 1.0    | Proposta inicial - consolidação em user_override |

---

**Status:** PROPOSTO (aguardando aprovação para implementação)
**Próximo Revisor:** Tech Lead
**Implementação Estimada:** 3 horas (migration + testes + atualização de código)
