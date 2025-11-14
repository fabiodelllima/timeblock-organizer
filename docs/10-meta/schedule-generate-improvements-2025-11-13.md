# Melhorias no Comando `schedule generate`

- **Data:** 13 de novembro de 2025
- **Tipo:** Análise Técnica + Plano de Implementação
- **Status:** [PLANEJAMENTO]
- **Prioridade:** ALTA (bloqueia E2E tests)

---

## 1. PROBLEMA ATUAL

### 1.1 Sintomas

O comando `schedule generate` está **subotimizado**:

1. **Falta flags abreviadas:** `--from/--to` sem `-f/-t`
2. **Parser rígido:** Só aceita `YYYY-MM-DD`, ignora helpers existentes e formatos locais
3. **UX verbosa:** Requer `--from/--to` sempre, não tem shortcuts
4. **Falta períodos longos:** Sem opções para trimestre, semestre, ano
5. **Inconsistência:** Outros comandos têm `-s/-e/-r`, mas este não tem

### 1.2 Impacto

**Planejamento de longo prazo é difícil:**

```bash
# Usuário quer planejar ano inteiro (tem que calcular datas)
schedule generate 1 --from 2025-01-01 --to 2025-12-31

# Trimestre (tem que lembrar quantos dias)
schedule generate 1 --from 2025-01-01 --to 2025-03-31

# Deveria ser simples:
schedule generate 1 --years 1
schedule generate 1 --quarters 1
```

---

## 3. SOLUÇÃO PROPOSTA

### 3.1 Nova Assinatura do Comando

```python
@app.command("generate")
def generate_instances(
    habit_id: int = typer.Argument(..., help="ID do hábito"),

    # Opção 1: Período explícito (atual melhorado)
    start: str = typer.Option(None, "--from", "-f", help="Data início"),
    end: str = typer.Option(None, "--to", "-t", help="Data fim"),

    # Opção 2: Shortcuts de período CURTO
    days: int = typer.Option(None, "--days", "-d", help="Próximos N dias"),
    weeks: int = typer.Option(None, "--weeks", "-w", help="Próximas N semanas"),

    # Opção 3: Shortcuts de período LONGO (NOVO)
    months: int = typer.Option(None, "--months", "-m", help="Próximos N meses"),
    quarters: int = typer.Option(None, "--quarters", "-q", help="Próximos N trimestres"),
    semesters: int = typer.Option(None, "--semesters", "-s", help="Próximos N semestres"),
    years: int = typer.Option(None, "--years", "-y", help="Próximos N anos"),
):
    """
    Gera instâncias de um hábito para período.

    Exemplos:
        # Curto prazo
        schedule generate 1 --days 7
        schedule generate 1 -w 2

        # Médio prazo
        schedule generate 1 --months 3
        schedule generate 1 -m 6

        # Longo prazo (NOVO)
        schedule generate 1 --quarters 2    # Próximos 6 meses
        schedule generate 1 -q 4            # Ano inteiro (4 trimestres)
        schedule generate 1 --semesters 1   # Próximos 6 meses
        schedule generate 1 --years 1       # Ano inteiro
        schedule generate 1 -y 2            # Próximos 2 anos
    """
```

### 3.2 Formatos de Data Aceitos

**Todos os comandos devem aceitar:**

| Categoria      | Formato         | Exemplo      | Parser                    |
| -------------- | --------------- | ------------ | ------------------------- |
| **ISO 8601**   | YYYY-MM-DD      | `2025-11-13` | `date.fromisoformat()`    |
| **Brasileiro** | DD/MM/YYYY      | `13/11/2025` | `parse_brazilian_date()`  |
| **Brasileiro** | DD-MM-YYYY      | `13-11-2025` | `parse_brazilian_date()`  |
| **Americano**  | MM/DD/YYYY      | `11/13/2025` | `parse_american_date()`   |
| **Americano**  | MM-DD-YYYY      | `11-13-2025` | `parse_american_date()`   |
| **Japonês**    | YYYY/MM/DD      | `2025/11/13` | `parse_japanese_date()`   |
| **Shortcuts**  | today, tomorrow | `today`      | `parse_date_shortcut()`   |
| **Offsets**    | +7days, +1week  | `+7days`     | `parse_relative_offset()` |

### 3.3 Definição de Períodos Longos

| Período   | Duração  | Flag Curta | Flag Longa      |
| --------- | -------- | ---------- | --------------- |
| Trimestre | 3 meses  | `-q N`     | `--quarters N`  |
| Semestre  | 6 meses  | `-s N`     | `--semesters N` |
| Ano       | 12 meses | `-y N`     | `--years N`     |

**Observações:**

- 1 trimestre = 3 meses (Q1: jan-mar, Q2: abr-jun, Q3: jul-set, Q4: out-dez)
- 1 semestre = 6 meses (S1: jan-jun, S2: jul-dez)
- 1 ano = 12 meses
- Cálculo sempre a partir de `date.today()`

### 3.4 Parser Unificado

_(mesmo conteúdo do parser anterior)_

---

## 4. LÓGICA DE RESOLUÇÃO DE PERÍODO

```python
def resolve_period(
    start: str | None,
    end: str | None,
    days: int | None,
    weeks: int | None,
    months: int | None,
    quarters: int | None,
    semesters: int | None,
    years: int | None,
    locale: str = "BR",
) -> tuple[date, date]:
    """
    Resolve período de geração baseado em parâmetros mutuamente exclusivos.

    Prioridade:
    1. --from/--to (se ambos fornecidos)
    2. --days, --weeks (curto prazo)
    3. --months (médio prazo)
    4. --quarters, --semesters, --years (longo prazo)

    Args:
        start, end: Datas explícitas (strings flexíveis)
        days, weeks: Períodos curtos
        months: Período médio
        quarters, semesters, years: Períodos longos
        locale: Código do país para priorizar formato de data

    Returns:
        (start_date, end_date) tuple

    Raises:
        ValueError: Se nenhum período ou múltiplos períodos fornecidos

    Examples:
        >>> resolve_period(days=7, weeks=None, months=None, quarters=None, semesters=None, years=None)
        (date(2025, 11, 13), date(2025, 11, 20))

        >>> resolve_period(quarters=1, ...)
        (date(2025, 11, 13), date(2026, 2, 12))  # 3 meses

        >>> resolve_period(years=1, ...)
        (date(2025, 11, 13), date(2026, 11, 12))  # 12 meses
    """
    from dateutil.relativedelta import relativedelta

    options_count = sum([
        start is not None and end is not None,
        days is not None,
        weeks is not None,
        months is not None,
        quarters is not None,
        semesters is not None,
        years is not None,
    ])

    if options_count == 0:
        raise ValueError(
            "Especifique período: --from/--to, --days, --weeks, --months, "
            "--quarters, --semesters ou --years"
        )

    if options_count > 1:
        raise ValueError(
            "Especifique apenas UMA forma de período"
        )

    today = date.today()

    # Opção 1: --from/--to
    if start and end:
        return (
            parse_flexible_date(start, locale=locale),
            parse_flexible_date(end, locale=locale)
        )

    # Opção 2: --days
    if days:
        return (today, today + timedelta(days=days - 1))

    # Opção 3: --weeks
    if weeks:
        return (today, today + timedelta(weeks=weeks) - timedelta(days=1))

    # Opção 4: --months
    if months:
        end = today + relativedelta(months=months) - timedelta(days=1)
        return (today, end)

    # Opção 5: --quarters (trimestres = 3 meses cada)
    if quarters:
        months_total = quarters * 3
        end = today + relativedelta(months=months_total) - timedelta(days=1)
        return (today, end)

    # Opção 6: --semesters (semestres = 6 meses cada)
    if semesters:
        months_total = semesters * 6
        end = today + relativedelta(months=months_total) - timedelta(days=1)
        return (today, end)

    # Opção 7: --years (anos = 12 meses cada)
    if years:
        end = today + relativedelta(years=years) - timedelta(days=1)
        return (today, end)
```

---

## 5. EXEMPLOS DE USO

### 5.1 Curto Prazo (dias, semanas)

```bash
# Próximos 7 dias
schedule generate 1 -d 7

# Próximas 2 semanas
schedule generate 1 -w 2

# Hoje apenas
schedule generate 1 -d 1
```

### 5.2 Médio Prazo (meses)

```bash
# Próximo mês
schedule generate 1 -m 1

# Próximos 3 meses
schedule generate 1 --months 3

# Próximos 6 meses
schedule generate 1 -m 6
```

### 5.3 Longo Prazo (trimestres, semestres, anos) **NOVO**

```bash
# Próximo trimestre (3 meses)
schedule generate 1 -q 1
schedule generate 1 --quarters 1

# Próximo semestre (6 meses)
schedule generate 1 -s 1
schedule generate 1 --semesters 1

# Ano inteiro (12 meses)
schedule generate 1 -y 1
schedule generate 1 --years 1

# 4 trimestres = 1 ano
schedule generate 1 -q 4

# 2 semestres = 1 ano
schedule generate 1 -s 2

# Próximos 2 anos
schedule generate 1 --years 2
```

### 5.4 Casos de Uso Reais

```bash
# Planejamento anual de hábito diário (ex: meditação)
schedule generate 1 -y 1

# Review trimestral de metas (gerar para Q1 2025)
schedule generate 1 -q 1

# Hábito semestral (ex: check-up médico)
schedule generate 1 -s 1

# Planejamento bienal
schedule generate 1 -y 2
```

---

## 6. PLANO DE IMPLEMENTAÇÃO

### Fase 1: Documentação (30min)

- [x] Análise técnica (este documento)
- [ ] Atualizar BR-HABIT-002
- [ ] Criar scenarios BDD

### Fase 2: Parser Flexível (60min)

- [ ] Implementar `parse_brazilian_date()`
- [ ] Implementar `parse_american_date()`
- [ ] Implementar `parse_japanese_date()`
- [ ] Implementar `parse_relative_offset()`
- [ ] Implementar `parse_flexible_date()` com locale
- [ ] Testes unitários do parser (15+ testes)
- [ ] Commit: "feat(utils): Parser flexível de datas multi-formato"

### Fase 3: Lógica de Resolução (40min) ← AUMENTOU de 30min

- [ ] Implementar `resolve_period()` com todos os períodos
- [ ] Adicionar lógica para quarters, semesters, years
- [ ] Testes unitários de resolução (20+ testes)
- [ ] Commit: "feat(schedule): Resolver período incluindo longo prazo"

### Fase 4: Comando CLI (35min) ← AUMENTOU de 30min

- [ ] Atualizar assinatura `generate_instances()`
- [ ] Adicionar flags `-f/-t/-d/-w/-m/-q/-s/-y`
- [ ] Integrar parser e resolver
- [ ] Detectar locale do sistema (padrão BR)
- [ ] Commit: "feat(schedule): Melhorar UX com períodos longos"

### Fase 5: Testes E2E (35min) ← AUMENTOU de 30min

- [ ] Atualizar testes existentes
- [ ] Adicionar testes de shortcuts
- [ ] Adicionar testes de formatos brasileiros
- [ ] Adicionar testes de períodos longos
- [ ] Garantir 100% passando
- [ ] Commit: "test(e2e): Atualizar para nova API de schedule"

### Fase 6: Documentação Final (15min)

- [ ] Atualizar help do comando
- [ ] Atualizar README com exemplos
- [ ] Commit: "docs: Exemplos de schedule generate"

**Tempo Total Estimado:** 3h35min (aumentou 20min devido a períodos longos)

---

## 7. TESTES OBRIGATÓRIOS

### 7.1 Testes Unitários (Resolução de Período)

```python
# tests/unit/test_utils/test_period_resolver.py

def test_resolve_period_quarters():
    """1 trimestre = 3 meses."""
    start, end = resolve_period(
        start=None, end=None,
        days=None, weeks=None, months=None,
        quarters=1, semesters=None, years=None
    )
    expected_end = date.today() + relativedelta(months=3) - timedelta(days=1)
    assert start == date.today()
    assert end == expected_end

def test_resolve_period_semesters():
    """1 semestre = 6 meses."""
    start, end = resolve_period(
        start=None, end=None,
        days=None, weeks=None, months=None,
        quarters=None, semesters=1, years=None
    )
    expected_end = date.today() + relativedelta(months=6) - timedelta(days=1)
    assert start == date.today()
    assert end == expected_end

def test_resolve_period_years():
    """1 ano = 12 meses."""
    start, end = resolve_period(
        start=None, end=None,
        days=None, weeks=None, months=None,
        quarters=None, semesters=None, years=1
    )
    expected_end = date.today() + relativedelta(years=1) - timedelta(days=1)
    assert start == date.today()
    assert end == expected_end

def test_resolve_period_multiple_quarters():
    """4 trimestres = 1 ano."""
    start, end = resolve_period(quarters=4, ...)
    expected_end = date.today() + relativedelta(months=12) - timedelta(days=1)
    assert end == expected_end

def test_resolve_period_rejects_multiple_options():
    """Deve rejeitar múltiplas opções."""
    with pytest.raises(ValueError, match="apenas UMA forma"):
        resolve_period(
            start=None, end=None,
            days=7, weeks=None, months=None,
            quarters=1, semesters=None, years=None
        )
```

### 7.2 Testes E2E (CLI)

```python
# tests/e2e/test_schedule_generate.py

def test_generate_with_quarters():
    """Testar geração por trimestres."""
    result = runner.invoke(app, ["schedule", "generate", "1", "-q", "1"])
    assert result.exit_code == 0

def test_generate_with_semesters():
    """Testar geração por semestres."""
    result = runner.invoke(app, ["schedule", "generate", "1", "-s", "1"])
    assert result.exit_code == 0

def test_generate_with_years():
    """Testar geração anual."""
    result = runner.invoke(app, ["schedule", "generate", "1", "-y", "1"])
    assert result.exit_code == 0
    # Verificar que gerou aproximadamente 365 instâncias (para hábito diário)

def test_generate_four_quarters_equals_one_year():
    """4 trimestres = 1 ano."""
    result_quarters = runner.invoke(app, ["schedule", "generate", "1", "-q", "4"])
    result_year = runner.invoke(app, ["schedule", "generate", "2", "-y", "1"])

    # Ambos devem gerar aproximadamente o mesmo número de instâncias
    # (assumindo hábitos diários idênticos)
```

---

## 8. RISCOS E MITIGAÇÃO

### Risco 1: Geração Muito Longa (1 ano = 365 instâncias)

**Mitigação:** Avisar usuário se período > 180 dias, confirmar antes de gerar

### Risco 2: Ambiguidade -s (--semesters vs --start?)

**Mitigação:** `-s` já usado em outros comandos para `--start`. Usar apenas `--semesters` (sem flag curta) OU usar `-S` (maiúscula)

**DECISÃO: Usar apenas `--semesters` (sem flag curta) para evitar conflito.**

---

## 9. MÉTRICAS DE SUCESSO

- [ ] 100% testes E2E passando
- [ ] Cobertura de parser >= 95%
- [ ] Suporta 8+ formatos de data
- [ ] Suporta 7 tipos de período (dias, semanas, meses, trimestres, semestres, anos, explícito)
- [ ] Tempo médio de comando reduzido 70%
- [ ] Zero quebra de compatibilidade

---

## 10. CORREÇÃO: FLAGS ABREVIADAS

**Conflito identificado:** `-s` já usado para `--start` em outros comandos.

**Solução:**

| Flag Longa    | Flag Curta | Observação                    |
| ------------- | ---------- | ----------------------------- |
| `--from`      | `-f`       | ✓ Disponível                  |
| `--to`        | `-t`       | ✓ Disponível                  |
| `--days`      | `-d`       | ✓ Disponível                  |
| `--weeks`     | `-w`       | ✓ Disponível                  |
| `--months`    | `-m`       | ✓ Disponível                  |
| `--quarters`  | `-q`       | ✓ Disponível                  |
| `--semesters` | _nenhuma_  | ✗ `-s` conflita com `--start` |
| `--years`     | `-y`       | ✓ Disponível                  |

**Uso final:**

```bash
schedule generate 1 --semesters 1  # Sem flag curta
schedule generate 1 -y 1           # Com flag curta
```

---

**Próxima Ação:** Commitar documento e começar implementação

**Data:** 2025-11-13 11:00 BRT

**Status:** [PLANEJAMENTO COMPLETO - PRONTO PARA IMPLEMENTAÇÃO]
