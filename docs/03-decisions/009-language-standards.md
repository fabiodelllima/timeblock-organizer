# ADR-009: Padrões de Idioma no Projeto

**Status:** ACEITO

**Data:** 03 de Novembro de 2025

**Contexto:** v1.2.0 Sprint 1.2

## Contexto

Projeto brasileiro em desenvolvimento com objetivos de:

- Uso pessoal (desenvolvedor brasileiro)
- Portfolio profissional (recrutadores internacionais)
- Possível abertura open source (futuro)

Necessidade de pragmatismo: desenvolvimento rápido agora, internacionalização depois.

## Decisão

### FASE ATUAL (v1.2.0 - v1.3.0): Português

**Tudo em português, exceto:**

- Nomes de variáveis/funções/classes (inglês - padrão de código)
- Tipos em conventional commits (inglês - padrão)

```python
# CORRETO (fase atual)
def generate_instances(habit_id: int) -> list[HabitInstance]:
    """Gera instâncias de hábito para período dado.

    DADO: habit_id válido
    QUANDO: Chamado com datas de início e fim
    ENTÃO: Cria instâncias seguindo padrão de recorrência

    Regra de Negócio: Respeita configuração de recorrência do hábito.

    Args:
        habit_id: ID do hábito
        start_date: Data inicial
        end_date: Data final

    Returns:
        Lista de instâncias criadas
    """
    pass
```

**Documentação:**

```markdown
# CORRETO (fase atual)

# ADR-006: Manter HabitInstance no Código

## Contexto

Debate sobre renomear HabitInstance → HabitAtom...

## Decisão

NÃO renomear código. Manter Instance tecnicamente, usar "atômico" em marketing.
```

**Testes:**

```python
# CORRETO (fase atual)
def test_generate_everyday_habit(self, everyday_habit):
    """Testa geração de instâncias para hábito EVERYDAY em 7 dias.

    DADO: Hábito com recorrência EVERYDAY
    QUANDO: Gerar instâncias para período de 7 dias
    ENTÃO: Deve criar exatamente 7 instâncias

    Regra de Negócio: Hábitos EVERYDAY geram uma instância por dia.
    """
    # Preparação: Define intervalo de datas
    start = date.today()
    end = start + timedelta(days=6)

    # Ação: Gera instâncias
    instances = HabitInstanceService.generate_instances(
        everyday_habit.id, start, end
    )

    # Verificação: Deve criar 7 instâncias
    assert len(instances) == 7
```

### FASE FUTURA (v2.0+): Internacionalização

**Quando projeto estiver maduro:**

- Traduzir docstrings para inglês
- Traduzir docs/ para inglês
- Manter commits bilíngues
- Implementar i18n para CLI

**Ferramentas:**

- sphinx-intl para docs
- gettext para CLI
- Manter docstrings duplicadas (PT/EN) ou apenas EN

## Resumo por Artefato - FASE ATUAL

| Artefato                            | Idioma        | Tradução Futura   |
| ----------------------------------- | ------------- | ----------------- |
| Nomes (variáveis, funções, classes) | Inglês        | -                 |
| Docstrings                          | **Português** | v2.0+ → Inglês    |
| Comentários inline                  | **Português** | v2.0+ → Inglês    |
| Testes (docstrings)                 | **Português** | v2.0+ → Inglês    |
| Commits (tipo)                      | Inglês        | -                 |
| Commits (descrição)                 | Português     | -                 |
| Documentação (docs/)                | **Português** | v2.0+ → Inglês    |
| ADRs                                | Português     | v2.0+ → Bilíngue  |
| README.md                           | **Português** | v1.3.0 → Bilíngue |
| CLI/Mensagens                       | Português     | v2.0+ → i18n      |

## Razão da Decisão

**Por que português agora:**

1. **Velocidade:** Time brasileiro desenvolve mais rápido em português
2. **Clareza:** Regras de negócio mais claras em idioma nativo
3. **Pragmatismo:** Tradução é refactoring, pode ser feito depois
4. **Onboarding:** Facilita entrada de desenvolvedores brasileiros

**Por que traduzir depois:**

1. **Portfolio:** Recrutadores internacionais esperam inglês
2. **Open Source:** Facilita contribuições globais
3. **Padrão:** Projetos maduros têm documentação em inglês

## Consequências

**Positivas:**

- Desenvolvimento mais rápido (sem overhead de tradução)
- Documentação clara para time atual
- Decisão reversível (tradução é refactoring)

**Negativas:**

- Portfolio temporariamente menos acessível internacionalmente
- Trabalho de tradução adiado para v2.0

**Mitigação:**

- README bilíngue desde v1.3.0
- Código (nomes) já em inglês (facilita leitura internacional)

---

**Relacionado:** README.md, CONTRIBUTING.md

**Revisão:** Após v1.3.0 (avaliar quando iniciar tradução)
