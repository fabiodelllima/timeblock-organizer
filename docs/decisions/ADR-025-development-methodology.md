# ADR-025: Processo de Desenvolvimento

**Status:** Aceito
**Data:** 2025-12-22

## Contexto

O projeto necessita de um processo de desenvolvimento documentado que:

1. Garanta rastreabilidade entre requisitos, testes e código
2. Minimize retrabalho através de feedback imediato
3. Mantenha qualidade consistente (99%+ cobertura)
4. Seja reproduzível em qualquer sessão de desenvolvimento
5. Combine práticas comprovadas da indústria

## Decisão

Adotamos um processo baseado em **Vertical Slicing** combinando práticas de:

| Prática          | Origem                   | Aplicação                       |
| ---------------- | ------------------------ | ------------------------------- |
| Vertical Slicing | Agile                    | Uma BR completa por vez         |
| Docs-First       | Specification by Example | BR documentada antes de tudo    |
| BDD              | Dan North (2006)         | Cenários Gherkin com pytest-bdd |
| Strict TDD       | Robert Martin (2003)     | 3 Leis rigorosas                |
| Sprints          | Scrum                    | Iterações de 1-2 semanas        |
| WIP Limits       | Kanban/Lean              | Máximo de itens em progresso    |

### Hierarquia de Desenvolvimento

```
DOCS ──> BDD ──> TDD ──> CODE
```

Cada etapa é pré-requisito da próxima. Não se avança sem completar a anterior.

### Fluxo por Business Rule (Vertical Slice)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERTICAL SLICE (1 BR)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. DOCUMENTAR BR                                               │
│     Arquivo: docs/core/business-rules.md                        │
│     Formato: BR-DOMAIN-XXX                                      │
│     Conteúdo: Regra, exemplos, casos de borda                   │
│                                                                 │
│  2. ESCREVER CENÁRIO BDD                                        │
│     Arquivo: tests/bdd/features/<domain>.feature                │
│     Formato: Gherkin (DADO/QUANDO/ENTÃO)                        │
│     Ferramenta: pytest-bdd                                      │
│                                                                 │
│  3. IMPLEMENTAR STEPS                                           │
│     Arquivo: tests/bdd/steps/<domain>_steps.py                  │
│     Conecta Gherkin ao código de teste                          │
│                                                                 │
│  4. CRIAR TESTE UNITÁRIO (RED)                                  │
│     Arquivo: tests/unit/test_<domain>/test_br_<domain>_xxx.py   │
│     Classe: TestBRDomainXXX                                     │
│     Método: test_br_domain_xxx_<scenario>                       │
│     Estado: DEVE FALHAR                                         │
│                                                                 │
│  5. IMPLEMENTAR (GREEN)                                         │
│     Código mínimo para passar o teste                           │
│     Estado: DEVE PASSAR                                         │
│                                                                 │
│  6. REFATORAR                                                   │
│     Melhorar código mantendo testes verdes                      │
│                                                                 │
│  7. COMMIT                                                      │
│     Formato: feat(scope): Implementa BR-DOMAIN-XXX              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [OK] BR COMPLETA ──> Iniciar próxima BR                        │
└─────────────────────────────────────────────────────────────────┘
```

### As 3 Leis do Strict TDD (Robert Martin)

1. **Não escreva código de produção** exceto para passar um teste que falha
2. **Não escreva mais de um teste** que seja suficiente para falhar
3. **Não escreva mais código** do que o suficiente para passar o teste

**Implicações práticas:**

```python
# Um teste por vez, um comportamento por teste
class TestBRHabit001TitleValidation:
    def test_br_habit_001_empty_title_raises_error(self): ...
    # Só escreva o próximo APÓS este passar:
    def test_br_habit_001_whitespace_only_raises_error(self): ...
```

### Estrutura BDD com pytest-bdd

```
tests/
├── bdd/
│   ├── features/           # Arquivos .feature (Gherkin)
│   │   ├── habit.feature
│   │   ├── routine.feature
│   │   └── timer.feature
│   ├── steps/              # Step definitions
│   │   ├── habit_steps.py
│   │   ├── routine_steps.py
│   │   └── timer_steps.py
│   └── conftest.py         # Fixtures BDD
├── unit/                   # Testes unitários
├── integration/            # Testes de integração
└── e2e/                    # Testes end-to-end
```

### Sprints

| Aspecto      | Definição                                       |
| ------------ | ----------------------------------------------- |
| Duração      | 1-2 semanas                                     |
| Planejamento | Início da sprint: selecionar BRs do backlog     |
| Daily        | Check-in diário (mesmo solo: revisar progresso) |
| Review       | Fim da sprint: validar entregas                 |
| Retro        | Fim da sprint: identificar melhorias            |

### WIP Limits

| Coluna                 | Limite     |
| ---------------------- | ---------- |
| To Do (Sprint Backlog) | 5-10 itens |
| In Progress            | 1-2 itens  |
| Code Review            | 2-3 itens  |
| Done                   | Sem limite |

**Regra:** Não iniciar novo item se In Progress estiver no limite.

### Princípio Single-Piece Flow

```
[CORRETO] Vertical Slicing
BR1 ──> Test1 ──> Code1 ──> [OK] ──> BR2 ──> Test2 ──> Code2 ──> [OK]

[ERRADO] Desenvolvimento em Lotes
BR1, BR2, BR3 ──> Test1, Test2, Test3 ──> Code1, Code2, Code3
```

### Pirâmide de Testes

```
        ┌───────┐
        │  E2E  │       5-10%  (Fluxos completos CLI)
       ─┴───────┴─
      ┌─────────────┐
      │ Integration │   20-25%  (Service + DB)
     ─┴─────────────┴─
    ┌───────────────┐
    │     Unit      │   70-75%  (BR isolada)
    └───────────────┘
```

## Terminologia

| Termo                      | Definição                                                          |
| -------------------------- | ------------------------------------------------------------------ |
| **Vertical Slicing**       | Completar uma feature através de todas as camadas antes da próxima |
| **WIP (Work In Progress)** | Trabalho em andamento                                              |
| **WIP Limit**              | Número máximo de itens permitidos em uma coluna                    |
| **Lead Time**              | Tempo desde solicitação até entrega                                |
| **Cycle Time**             | Tempo de trabalho ativo (exclui espera)                            |
| **Sprint**                 | Iteração com duração fixa                                          |
| **Backlog**                | Lista priorizada de todo trabalho futuro                           |
| **Sprint Backlog**         | Itens selecionados para a sprint atual                             |
| **On Hold**                | Item pausado temporariamente                                       |

## Alternativas Consideradas

### 1. TDD Puro (sem documentação prévia)

- **Rejeitado:** Falta rastreabilidade, BRs implícitas

### 2. Waterfall (toda doc, depois todo código)

- **Rejeitado:** Feedback tardio, alto retrabalho

### 3. Desenvolvimento Ad-hoc (sem processo)

- **Rejeitado:** Inconsistência, débito técnico, não reproduzível

### 4. BDD sem TDD

- **Rejeitado:** Cenários muito alto nível, falta granularidade

## Consequências

### Positivas

- Rastreabilidade 100% (BR → BDD → Teste → Código)
- Feedback imediato (erros detectados na hora)
- Commits atômicos e reversíveis
- Documentação sempre atualizada
- Métricas de progresso claras (BRs completas)
- Facilita onboarding de contribuidores

### Negativas

- Overhead inicial (setup BDD, sprints)
- Requer disciplina constante
- Mais lento para features triviais

### Neutras

- Requer tooling (pytest-bdd, board com WIP)
- Commits mais frequentes e menores

## Métricas de Sucesso

| Métrica             | Meta    |
| ------------------- | ------- |
| Cobertura de testes | > 95%   |
| BRs com teste       | 100%    |
| BRs com cenário BDD | 100%    |
| WIP In Progress     | <= 2    |
| Lead Time por BR    | < 1 dia |

## Ferramentas

| Função        | Ferramenta                      |
| ------------- | ------------------------------- |
| Board/Sprints | GitHub Projects ou Azure Boards |
| BDD           | pytest-bdd                      |
| Testes        | pytest + pytest-cov             |
| Linting       | ruff                            |
| CI            | GitHub Actions                  |

## Referências

- Vertical Slicing: <https://www.agilealliance.org/glossary/vertical-slice/>
- Strict TDD (3 Leis): <https://www.butunclebob.com/ArticleS.UncleBob.TheThreeRulesOfTdd>
- BDD: <https://dannorth.net/introducing-bdd/>
- Specification by Example: Gojko Adzic (2011)
- Lean Software: Mary & Tom Poppendieck (2003)
- pytest-bdd: <https://pytest-bdd.readthedocs.io/>

## Relacionados

- ADR-018: Language Standards
- ADR-019: Test Naming Convention
- ADR-020: Business Rules Nomenclature
