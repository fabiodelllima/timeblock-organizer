# TimeBlock Organizer - Estado Atual e Estratégia CI/CD

- **Data:** 2025-11-20
- **Versão:** v1.4.0-dev (após Sprint 3)
- **Branch:** develop

---

## [RESUMO EXECUTIVO]

### Estado Atual

- 14/17 BRs implementadas (82% MVP)
- Sprints 1-3 completos
- 93 testes quebrados (débito técnico)
- Coverage: 59%

### Estratégia CI/CD

- **Commits idênticos** em GitHub e GitLab (PT-BR)
- GitHub: código limpo (sem comentários, sem docs/)
- GitLab: código completo (com comentários, com docs/)
- Mesmo histórico git, conteúdo diferente

### Roadmap

```terminal
Sprint 3.1: Docs        [1-2h] ← AGORA
Sprint 3.2: Scripts     [2-3h]
Sprint 3.3: Pipelines   [2-3h]
Sprint 3.4: Debt Fix    [2-3h] P0
Sprint 4:   STREAK      [2-3d]
Sprint 5:   E2E Tests   [1-2d]
Sprint 6:   Release     [1d]
```

---

## [PARTE 1] PROGRESSO MVP

### Sprints Completos

**Sprint 1 (16-Nov): ROUTINE** ✓

- 4 BRs implementadas
- 18/18 testes GREEN

**Sprint 2 (19-Nov): TIMER + SKIP** ✓

- 6 BRs implementadas (incluiu Sprint 5)
- 56/56 testes GREEN

**Sprint 3 (19-Nov): HABIT-INSTANCE** ✓

- 4 BRs implementadas (Status+Substatus)
- 14/14 testes GREEN

**TOTAL:** 14/17 BRs (82%)

### Falta Implementar

**Sprint 4: STREAK** (BLOQUEADO)

- BR-STREAK-001: Algorithm
- BR-STREAK-002: Break conditions
- BR-STREAK-003: Maintain conditions

**Bloqueio:** 93 testes quebrados (Sprint 1)

---

## [PARTE 2] ESTRATÉGIA CI/CD (CORRIGIDA)

### Princípio Fundamental

**Commits IDÊNTICOS, conteúdo DIFERENTE**

```terminal
LOCAL → GitHub (limpo, commits PT-BR)
      → GitLab (completo, commits PT-BR)
```

### Como Funciona

```terminal
[VOCÊ ESCREVE]
git commit -m "feat(cicd): Adiciona pipeline"
Hash: abc123

[PUSH GITHUB]
./scripts/push-github.sh
  - Transforma arquivos (remove comentários, docs/)
  - Mantém commit abc123 (MESMO HASH)

[PUSH GITLAB]
git push origin develop
  - Mantém arquivos originais
  - Mantém commit abc123 (MESMO HASH)
```

**Resultado:** Mesmo histórico, conteúdo diferente

### Diferenças

| Aspecto     | GitHub            | GitLab              |
| ----------- | ----------------- | ------------------- |
| Commits     | PT-BR (idênticos) | PT-BR (idênticos)   |
| Comentários | Removidos         | Mantidos            |
| docs/       | Excluído          | Presente            |
| CI/CD       | Actions (básico)  | Pipeline (completo) |
| Propósito   | Showcase público  | Desenvolvimento     |

### Por Que Funciona

Git rastreia:

- **Commit** (mensagem + metadata) → Mesmo hash
- **Tree** (conteúdo arquivos) → Hashes diferentes

Podemos ter:

```terminal
Commit abc123
├─ GitHub: tree def456 (sem comentários)
└─ GitLab: tree ghi789 (com comentários)
```

---

## [PARTE 3] NOVO ROADMAP

### Sprint 3.1: Documentação (1-2h) ← AGORA

**Branch:** feature/cicd-docs

**Deliverables:**

- 5 documentos estratégicos
- Um commit por documento
- Todos em docs/10-meta/

**Arquivos:**

1. current-state-and-cicd-strategy.md ✓
2. cicd-quickstart-guide.md ✓
3. cicd-workflow-diagram.md [ ]
4. cicd-implementation-checklist.md [ ]
5. cicd-files-index.md [ ]

### Sprint 3.2: Scripts (2-3h)

**Branch:** feature/cicd-scripts

**Deliverables:**

- scripts/push-github.sh (transforma e push)
- scripts/push-gitlab.sh (push direto)
- scripts/strip-comments.py (remove comentários)
- .git/hooks/pre-commit (validações)

**SEM tradução de commits** (commits idênticos!)

### Sprint 3.3: Pipelines (2-3h)

**Branch:** feature/cicd-pipelines

**Deliverables:**

- .gitlab-ci.yml (completo)
- .github/workflows/ci.yml (básico)
- Configurar remotes

### Sprint 3.4: Débito Técnico (2-3h) [P0]

**Branch:** fix/sprint1-test-debt

**Deliverables:**

- 93 testes corrigidos
- 487/487 testes GREEN
- Coverage > 95%

---

## [PARTE 4] ADRS PROPOSTOS

### ADR-022: Dual Repository Strategy

- **Status:** PROPOSTO
- **Data:** 2025-11-20

**Decisão:**

- GitHub = showcase (código limpo)
- GitLab = desenvolvimento (código completo)
- Commits IDÊNTICOS em ambos
- Conteúdo de arquivos diferente

**Consequências:**

- [✓] Mesmo histórico git (sincroniza fácil)
- [✓] GitHub limpo para portfolio
- [✓] GitLab completo para dev
- [-] Scripts de transformação necessários
- [-] Dois pipelines CI/CD

### ADR-023: Pre-commit Hooks

- **Status:** PROPOSTO
- **Data:** 2025-11-20

**Decisão:**

- Ruff format/check obrigatório
- Mypy warning only
- Pytest unit bloqueante

**Consequências:**

- [✓] Qualidade garantida
- [✓] Feedback imediato
- [-] Commits ~10s mais lentos

### ADR-024: Portuguese Commits

- **Status:** PROPOSTO
- **Data:** 2025-11-20

**Decisão:**

- Commits em PT-BR para ambos repos
- SEM tradução (commits idênticos)
- type(scope) sempre em inglês
- Descrição em português

**Consequências:**

- [✓] Natural para dev brasileiro
- [✓] Histórico idêntico (sincroniza fácil)
- [✓] Sem complexidade de tradução
- [-] GitHub não é internacional
- [-] GitLab em português (ok para time BR)

---

## [PARTE 5] MÉTRICAS

| Métrica           | Atual   | Meta    | Delta |
| ----------------- | ------- | ------- | ----- |
| BRs implementadas | 14/17   | 17/17   | 3     |
| Testes passando   | 394/487 | 487/487 | 93    |
| Coverage          | 59%     | 95%+    | +36%  |
| CI/CD funcional   | NÃO     | SIM     | Setup |
