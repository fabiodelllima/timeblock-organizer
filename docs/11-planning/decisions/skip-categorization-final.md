# Decisão: Skip com Justificativas Categorizadas

- **Status:** Decidido
- **Data:** 14 de Novembro de 2025
- **Contexto:** Sessão de planejamento MVP
- **Impacto:** HabitInstance model, reports, CLI

---

## Problema

Como implementar sistema de skip de habits que permita:

1. Usuário pular habit quando necessário
2. Sistema diferenciar skips justificados de não justificados
3. Gerar estatísticas úteis sobre padrões de skip
4. Evitar texto livre (dificulta análise)

---

## Decisão

### Skip Categorizado com 8 Opções

Implementar enum `SkipReason` com categorias pré-definidas:

```python
class SkipReason(str, Enum):
    HEALTH = "saude"           # Consultas médicas, dentistas, exames
    WORK = "trabalho"          # Reuniões, hora extra, viagens
    FAMILY = "familia"         # Eventos familiares, emergências
    PERSONAL = "pessoal"       # Compromissos pessoais
    WEATHER = "clima"          # Condições climáticas adversas
    FATIGUE = "cansaco"        # Esgotamento físico/mental
    EMERGENCY = "emergencia"   # Emergências não categorizadas
    OTHER = "outro"            # Outros motivos
```

### Campo Opcional + Nota Livre

```python
class HabitInstance(SQLModel, table=True):
    # ... campos existentes
    skip_reason: SkipReason | None = None
    skip_note: str | None = None  # Opcional, max 200 chars
```

### Prazo: 24 Horas

- User executa `habit skip 42` → skip registrado SEM reason
- Dia seguinte: sistema questiona em QUALQUER comando CLI
- Após 24h: skip permanece sem justificativa (definitivo)

---

## Alternativas Consideradas

### A) String Livre

- [x] Dificulta análise
- [x] Inconsistências (typos, variações)
- [x] Impossível gerar estatísticas

### B) Tags/Labels

- [OK] Flexível
- [x] Usuário precisa criar tags primeiro
- [x] Complexidade desnecessária para MVP

### C) Binário (justificado/não justificado)

- [OK] Simples
- [x] Perde contexto (WHY skip?)
- [x] Estatísticas limitadas

**Escolhido:** Categorias pré-definidas (balanço simplicidade vs utilidade)

---

## Justificativa

### Por que Categorizado?

1. **Análise Estatística:** Sistema identifica padrões

   - "40% dos skips são por trabalho" → usuário sobrecarregado?
   - "60% dos skips são segunda-feira" → horário inadequado?

2. **UX Simples:** SELECT é mais rápido que digitar

   - CLI: menu numerado (1-8)
   - Mobile futuro: dropdown

3. **Dados Estruturados:** Facilita reports e visualizações

   - Gráficos por categoria
   - Comparação entre habits
   - Tendências ao longo do tempo

4. **Balanço:** Categorias cobrem 95% dos casos reais
   - Opção "outro" + nota livre cobre edge cases

### Por que 24h?

1. **Memória Recente:** Usuário lembra motivo real
2. **Não Invasivo:** Sistema pergunta apenas 1x/dia
3. **Balanceado:** Não é imediato (permite reflexão) nem tardio (perda contexto)

---

## Impacto

### Modelo de Dados

```python
# Adicionar campos
skip_reason: SkipReason | None = None
skip_note: str | None = Field(None, max_length=200)
```

### CLI

```bash
# Skip imediato (sem reason)
timeblock habit skip 42

# Próximo comando (dia seguinte)
timeblock habit list
> Hábitos sem justificativa:
> 1. Academia (14/11)
>
> Justificar agora? [Y/n]: y
>
> Motivo:
> 1. Saúde
> 2. Trabalho
> 3. Família
> ...
> Escolha [1-8]: 2
>
> Nota adicional (opcional): Reunião urgente cliente X
> [OK] Justificativa registrada
```

### Reports

```bash
timeblock report habit 42 --period 30

+------------------------------------+
| Skips Detalhados:                  |
| +-- Justificados:      5 (17%)     |
| |  +-- Saúde:          2           |
| |  +-- Trabalho:       2           |
| |  +-- Clima:          1           |
| +-- Sem Justificativa: 3 (10%)     |
+------------------------------------+
```

### Service Layer

```python
class HabitInstanceService:
    @staticmethod
    def skip_habit(instance_id: int, reason: SkipReason | None = None,
                   note: str | None = None) -> HabitInstance:
        """Marca habit como skipped com reason opcional."""

    @staticmethod
    def get_pending_justifications() -> list[HabitInstance]:
        """Retorna skips sem justificativa < 24h."""
        cutoff = datetime.now() - timedelta(hours=24)
        return [
            i for i in session.query(HabitInstance)
            .filter(HabitInstance.status == "skipped")
            .filter(HabitInstance.skip_reason == None)
            .filter(HabitInstance.updated_at >= cutoff)
        ]
```

---

## Regra de Negócio Relacionada

**BR-HABIT-SKIP-001:** Skip Registration
**BR-HABIT-SKIP-002:** Justification Deadline (24h)
**BR-HABIT-SKIP-003:** Skip Statistics
**BR-HABIT-SKIP-004:** Streak Breaking (skip sempre quebra)

Ver: `docs/04-specifications/business-rules/habit-skip.md` (a criar)

---

## Validação

### Critérios de Aceite

- [ ] Enum SkipReason com 8 categorias
- [ ] Campo skip_reason opcional em HabitInstance
- [ ] Campo skip_note opcional (max 200 chars)
- [ ] CLI pergunta justificativa no próximo uso
- [ ] Reports mostram breakdown por categoria
- [ ] Testes: skip com/sem reason, prazo 24h

### Métricas de Sucesso

- 70%+ dos skips justificados (após 30 dias de uso)
- Reports úteis para identificar padrões
- Usuário consegue justificar em < 30s

---

## Evolução Futura

### v1.5+

- [ ] Reminder via notificação sistema operacional
- [ ] Sugerir category baseado em histórico
- [ ] "Smart categories" (ML identifica padrões)

### v2.0+

- [ ] Categorias customizáveis por usuário
- [ ] Sub-categorias (ex: Saúde → Médico, Dentista, Exame)
- [ ] Integração calendário (detecta conflitos)

---

## Referências

- Sessão: `sessions/2025-11-14-skip-states-cli-discussion.md`
- Modelo: `src/timeblock/models/habit_instance.py`
- Service: `src/timeblock/services/habit_instance_service.py`
- CLI: `src/timeblock/commands/habit.py`

---

**Próxima Revisão:** Após 30 dias de uso real

**Status:** Ready para implementação
