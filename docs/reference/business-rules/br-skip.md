# Skip

O Skip é o mecanismo que transforma ausência em informação. Na maioria dos sistemas de rastreamento de hábitos, não fazer algo é simplesmente um vazio — um dia sem marcação que pode significar esquecimento, preguiça, doença ou uma decisão racional. O TimeBlock Planner distingue entre "não fiz porque escolhi não fazer" (Skip) e "não fiz porque ignorei" (Ignored), e dentro do Skip, diferencia _por que_ o usuário optou por pular.

As categorias de SkipReason cobrem os motivos mais comuns: saúde, trabalho, família, viagem, clima, falta de recursos, emergência e outros. Quando o usuário pula um hábito conscientemente e registra o motivo, está gerando dados que o sistema pode usar para identificar padrões. Se toda segunda-feira o hábito "Corrida" é skipado com motivo "Trabalho", talvez a segunda não seja o melhor dia para correr — e a rotina deveria ser ajustada. Uma nota opcional permite contexto adicional: "Reunião de emergência" ou "Gripe, repouso médico".

Essa filosofia se conecta diretamente com o princípio de transparência do sistema. Pular conscientemente não é falhar — é adaptar-se com honestidade. O registro de skips preserva a integridade da cadeia de hábitos: um skip com justificativa não quebra o streak (dependendo da configuração), enquanto uma instância ignorada (que expirou sem ação do usuário) quebra. Essa distinção incentiva o usuário a manter o sistema atualizado mesmo nos dias em que não consegue executar o plano, porque há uma recompensa tangível: a preservação do streak e a geração de dados úteis.

### BR-SKIP-001: Categorização de Skip

**Descrição:** Skip de habit deve ser categorizado usando enum SkipReason.

**Enum SkipReason:**

```python
class SkipReason(str, Enum):
    HEALTH = "saude"                   # Saude (doenca, consulta)
    WORK = "trabalho"                  # Trabalho (reuniao, deadline)
    FAMILY = "familia"                 # Familia (evento, emergencia)
    TRAVEL = "viagem"                  # Viagem/Deslocamento
    WEATHER = "clima"                  # Clima (chuva, frio)
    LACK_RESOURCES = "falta_recursos"  # Falta de recursos
    EMERGENCY = "emergencia"           # Emergencias
    OTHER = "outro"                    # Outros
```

**Comando:**

```bash
habit skip INSTANCE_ID --reason HEALTH --note "Consulta medica"
```

**Testes:**

- `test_br_skip_001_valid_reasons`
- `test_br_skip_001_with_note`

---

### BR-SKIP-002: Campos de Skip

**Descrição:** HabitInstance possui campos para rastrear skip.

**Campos:**

```python
skip_reason: SkipReason | None    # Categoria (obrigatório se justified)
skip_note: str | None             # Nota opcional (max 500 chars)
```

**Regras:**

1. SKIPPED_JUSTIFIED requer skip_reason
2. SKIPPED_UNJUSTIFIED não tem skip_reason
3. skip_note é sempre opcional

**Como cada estado é criado:**

- SKIPPED_JUSTIFIED — `habit skip <id> --reason <CATEGORIA>` no CLI, ou a seleção de categoria no modal (BR-TUI-024).
- SKIPPED_UNJUSTIFIED — `habit skip <id> --unjustified` no CLI, ou a opção "Sem justificativa" no modal (BR-TUI-024).

**Validação:**

```python
if self.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED:
    if self.skip_reason is None:
        raise ValueError("skip_reason obrigatório para SKIPPED_JUSTIFIED")
else:
    if self.skip_reason is not None:
        raise ValueError("skip_reason só permitido com SKIPPED_JUSTIFIED")
```

**Testes:**

- `test_br_skip_002_justified_requires_reason`
- `test_br_skip_002_unjustified_no_reason`
- `test_br_skip_002_note_optional`

---

### BR-SKIP-003: Prazo para Justificar

**Descrição:** Usuário tem 48h após horário planejado para justificar skip.

**Comportamento:**

- Dentro de 48h: pode adicionar/editar justificativa
- Apos 48h: instância marcada como IGNORED automaticamente
- IGNORED pode receber justificativa retroativa (recuperação)

**Nota:** Timeout automático documentado, implementação pendente.

**Testes:**

- `test_br_skip_003_within_deadline`
- `test_br_skip_003_after_deadline_ignored`

---

### BR-SKIP-004: CLI Prompt Interativo (DESCONTINUADO)

> **Substituída pelo ADR-058 e pela BR-TUI-024.** O prompt interativo `[1-9]` no CLI não foi adotado. A seleção interativa de motivo pertence ao TUI (modal da BR-TUI-024, com as 8 categorias e a opção "Sem justificativa"); o CLI recebe o motivo por flag — `--reason` para justificado, `--unjustified` para sem justificativa (ver BR-SKIP-001 e BR-SKIP-002).

**Descrição original (histórica):** o CLI ofereceria um prompt para categorizar, com as opções 1-8 mapeando para SKIPPED_JUSTIFIED e a opção 9 para SKIPPED_UNJUSTIFIED. A divisão acima a substitui.
