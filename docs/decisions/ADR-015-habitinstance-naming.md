# ADR-006: Manter HabitInstance no Código, "Hábitos Atômicos" no Marketing

**Status:** ACEITO

**Data:** 03 de Novembro de 2025

**Contexto:** v1.2.0 - Refatoração HabitAtom

## Contexto

Debate sobre renomear `HabitInstance` → `HabitAtom` em todo o código (26 arquivos, 141 referências) para alinhar com filosofia "Atomic Habits" de James Clear.

## Decisão

**NÃO renomear código. Usar "Hábitos Atômicos" apenas em docs/UX.**

### Código (Técnico)

```python
class HabitInstance(SQLModel):
    """Ocorrência específica de um hábito em uma data.

    Representa um 'hábito atômico' no sentido de Atomic Habits.
    Instância é o termo tecnicamente correto em OOP.
    """
```

### Documentação (Marketing)

- README: "Baseado em Hábitos Atômicos de James Clear"
- PHILOSOPHY.md: Explicação completa da filosofia
- CLI messages: "Hábito completado!" (sem mencionar instance/atom)

## Alternativas Consideradas

### **A) Renomear código completo (HabitInstance → HabitAtom)**

- Pros: Alinhamento filosófico, branding único
- Cons: 26 arquivos, 141 refs, risco de bugs, 10-15h trabalho

### **B) Híbrido (HabitAtom apenas em alguns lugares)**

- Pros: Meio-termo
- Cons: Inconsistência confusa

### **C) Manter Instance, marketing "atômico" (ESCOLHIDA)**

- Pros: Tecnicamente correto, baixo risco, separa concerns
- Cons: Leve desalinhamento termo técnico vs marketing

## Consequências

**Positivas:**

- Baixo risco de introduzir bugs
- Economiza 10-15h de refatoração
- "Instance" é OOP correto
- Marketing funciona independente

**Negativas:**

- Leve desalinhamento entre código e marketing
- Devs precisam saber que "instance" = "hábito atômico" conceitualmente

**Neutras:**

- Usuários não veem código interno
- Recrutadores verão documentação (marketing) E código (técnico)

## Compliance

- Objetivo showcase/portfolio: ATENDIDO (demonstra decisão técnica madura)
- Atomic Habits filosofia: ATENDIDO (via docs/UX)
- Padrões profissionais: ATENDIDO (OOP correto)

---

**Relacionado:** PHILOSOPHY.md, README.md, v1.2.0 Sprint 1.4
