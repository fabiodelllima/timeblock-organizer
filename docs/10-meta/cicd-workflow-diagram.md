# Diagramas Workflow CI/CD Dual Repository

**Data:** 2025-11-20

**Documento:** 3/5 da série CI/CD Strategy

---

## [DIAGRAMA 1] ARQUITETURA GERAL

```terminal
┌───────────────────────────────────────────────────────────┐
│                    DESENVOLVIMENTO LOCAL                  │
│  /timeblock-organizer/                                    │
│                                                           │
│  ┌────────────────────────────────────────────────────┐   │
│  │  WORKSPACE                                         │   │
│  │  ├─ cli/src/        (código Python)                │   │
│  │  ├─ cli/tests/      (testes)                       │   │
│  │  ├─ docs/           (documentação completa)        │   │
│  │  └─ scripts/        (automação CI/CD)              │   │
│  └────────────────────────────────────────────────────┘   │
│                           │                               │
│                           ▼                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │  PRE-COMMIT HOOKS                                  │   │
│  │  [1] ruff format                                   │   │
│  │  [2] ruff check --fix                              │   │
│  │  [3] mypy (warning)                                │   │
│  │  [4] pytest tests/unit (bloqueante)                │   │
│  │                                                    │   │
│  │  [BLOQUEIA COMMIT SE FALHAR]                       │   │
│  └────────────────────────────────────────────────────┘   │
│                           │                               │
│                           ▼                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │  GIT COMMIT (PT-BR)                                │   │
│  │  feat(scope): Adiciona funcionalidade              │   │
│  │  Hash: abc123                                      │   │
│  │                                                    │   │
│  │  Código + Comentários + Docstrings + docs/         │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────┬────────────────────┬───────────────────┘
                   │                    │
                   │                    │
      ┌────────────▼─────────┐  ┌───────▼──────────┐
      │   git push origin    │  │ ./scripts/       │
      │   develop            │  │ push-github.sh   │
      └────────────┬─────────┘  └───────┬──────────┘
                   │                    │
                   │                    │
┌──────────────────▼────────────┐  ┌────▼───────────────────┐
│    GITLAB (origin)            │  │  TRANSFORMAÇÃO         │
│    git@gitlab.com/...         │  │                        │
│                               │  │  1. Branch temp        │
│ [CÓDIGO COMPLETO]             │  │  2. Remove docs/       │
│ ├─ Comentários inline         │  │  3. Strip comentários  │
│ ├─ Docstrings                 │  │  4. Push github        │
│ ├─ docs/ (189 arquivos)       │  │  5. Cleanup            │
│ └─ Commits PT-BR (abc123)     │  └───┬────────────────────┘
│                               │      │
│ ┌───────────────────────────┐ │      │
│ │  .gitlab-ci.yml           │ │      │
│ │                           │ │      │
│ │  [STAGE 1] TEST           │ │  ┌───▼───────────────────────┐
│ │  ├─ test:unit             │ │  │  GITHUB (secondary)       │
│ │  ├─ test:integration      │ │  │  git@github.com/...       │
│ │  ├─ test:bdd              │ │  │                           │
│ │  ├─ lint:ruff             │ │  │ [CÓDIGO LIMPO]            │
│ │  └─ typecheck:mypy        │ │  │ ├─ SEM comentários        │
│ │                           │ │  │ ├─ COM docstrings         │
│ │  [STAGE 2] BUILD          │ │  │ ├─ SEM docs/              │
│ │  └─ build:docs            │ │  │ └─ Commits PT-BR          │
│ │                           │ │  │    (abc123 - MESMO)       │
│ │  [STAGE 3] DEPLOY         │ │  │                           │
│ │  └─ deploy:pages          │ │  │ ┌──────────────────┐      │
│ └───────────────────────────┘ │  │ │ .github/         │      │
│                               │  │ │ workflows/ci.yml │      │
│ [PIPELINES]                   │  │ │                  │      │
│ ├─ All tests must pass        │  │ │ [JOBS]           │      │
│ ├─ Coverage report            │  │ │ ├─ lint          │      │
│ ├─ Build docs                 │  │ │ ├─ typecheck     │      │
│ └─ Deploy GitLab Pages        │  │ │ ├─ test          │      │
│                               │  │ │ └─ coverage      │      │
│ [DESENVOLVIMENTO]             │  │ └──────────────────┘      │
│ └─ Time interno               │  │                           │
│                               │  │ [SHOWCASE PÚBLICO]        │
└───────────────────────────────┘  │ └─ Portfolio/Recrutadores │
                                   └───────────────────────────┘
```

---

## [DIAGRAMA 2] FLUXO DE COMMITS

```terminal
┌──────────────────────────────────────────────────────────┐
│  LOCAL                                                   │
│                                                          │
│  git commit -m "feat(cicd): Adiciona pipeline"           │
│  Commit: abc123                                          │
│  Tree:   xyz789 (código + comentários + docs/)           │
└───────────────────┬──────────────┬───────────────────────┘
                    │              │
        ┌───────────▼──┐      ┌────▼──────────┐
        │ Push GitLab  │      │ Push GitHub   │
        │ (direto)     │      │ (transformado)│
        └───────────┬──┘      └────┬──────────┘
                    │              │
                    ▼              ▼
┌───────────────────────────────────────────────────────┐
│  GITLAB                    GITHUB                     │
│                                                       │
│  Commit: abc123            Commit: abc123             │
│  Tree:   xyz789            Tree:   def456             │
│  (MESMO HASH)              (MESMO HASH)               │
│                                                       │
│  Arquivos:                 Arquivos:                  │
│  ├─ habit.py               ├─ habit.py                │
│  │   """Docstring"""       │   """Docstring"""        │
│  │   # Comentário          │   def method():          │
│  │   def method():         │       pass               │
│  │       pass              │                          │
│  │                         │                          │
│  ├─ docs/                  ├─ (docs/ AUSENTE)         │
│  │   ├─ 01-architecture/   │                          │
│  │   ├─ 02-diagrams/       │                          │
│  │   └─ ... (189 files)    │                          │
│  │                         │                          │
│  └─ README.md              └─ README.md               │
│      (com badges GitLab)       (com badges GitHub)    │
└───────────────────────────────────────────────────────┘

RESULTADO:
├─ Mesmo histórico git (ambos têm abc123)
├─ git pull/push funciona entre eles
├─ git log --oneline idêntico
└─ git diff mostra diferenças de conteúdo
```

---

## [DIAGRAMA 3] WORKFLOW DESENVOLVIMENTO

```terminal
[INÍCIO] NOVA FEATURE
    │
    ├─ 1. Pull GitLab (código completo)
    │    git pull origin develop
    │
    ├─ 2. Criar branch
    │    git checkout -b feature/nome
    │
    ├─ 3. Desenvolver
    │    [editar código]
    │    [adicionar comentários]
    │    [atualizar docs/]
    │
    ├─ 4. Commit (PT-BR)
    │    git add .
    │    git commit -m "feat(scope): Adiciona X"
    │    │
    │    ├─ Pre-commit executa automaticamente
    │    │   ├─ [1/4] ruff format
    │    │   ├─ [2/4] ruff check
    │    │   ├─ [3/4] mypy
    │    │   └─ [4/4] pytest unit
    │    │
    │    ├─ [PASS] → Commit criado
    │    └─ [FAIL] → Commit bloqueado
    │
    ├─ 5. Push GitLab
    │    git push origin feature/nome
    │
    ├─ 6. Merge Request (GitLab)
    │    ┌─────────────────────────┐
    │    │  CI/CD Pipeline         │
    │    │  ├─ test:unit    [PASS] │
    │    │  ├─ test:integ   [PASS] │
    │    │  ├─ test:bdd     [PASS] │
    │    │  ├─ lint:ruff    [PASS] │
    │    │  └─ typecheck    [PASS] │
    │    └─────────────────────────┘
    │    │
    │    ├─ Code Review
    │    └─ Merge --no-ff para develop
    │
    ├─ 7. Sincronizar GitHub
    │    git checkout develop
    │    git pull origin develop
    │    ./scripts/push-github.sh
    │
    └─ [FIM] Feature completa em ambos repos
```

---

## [DIAGRAMA 4] TRANSFORMAÇÃO ARQUIVOS

```terminal
ARQUIVO: cli/src/timeblock/services/habit_service.py

┌──────────────────────────────────────────────────────┐
│  GITLAB (código completo)                            │
├──────────────────────────────────────────────────────┤
│  """                                                 │
│  Service para gerenciar hábitos.                     │
│  """                                                 │
│  from timeblock.models import Habit                  │
│                                                      │
│  # TODO: Implementar cache para performance          │
│  # Complexidade: O(n) - pode melhorar                │
│                                                      │
│  class HabitService:                                 │
│      """Gerencia operações de hábitos."""            │
│                                                      │
│      def create_habit(self, title: str):             │
│          """                                         │
│          Cria novo hábito.                           │
│                                                      │
│          Args:                                       │
│              title: Título do hábito                 │
│          """                                         │
│          # Validar entrada                           │
│          if not title:                               │
│              raise ValueError("Título obrigatório")  │
│                                                      │
│          # Criar instância                           │
│          habit = Habit(title=title)                  │
│          return habit                                │
└──────────────────────────────────────────────────────┘
                    │
                    │ scripts/strip-comments.py
                    ▼
┌──────────────────────────────────────────────────────┐
│  GITHUB (código limpo)                               │
├──────────────────────────────────────────────────────┤
│  """                                                 │
│  Service para gerenciar hábitos.                     │
│  """                                                 │
│  from timeblock.models import Habit                  │
│                                                      │
│  class HabitService:                                 │
│      """Gerencia operações de hábitos."""            │
│                                                      │
│      def create_habit(self, title: str):             │
│          """                                         │
│          Cria novo hábito.                           │
│                                                      │
│          Args:                                       │
│              title: Título do hábito                 │
│          """                                         │
│          if not title:                               │
│              raise ValueError("Título obrigatório")  │
│                                                      │
│          habit = Habit(title=title)                  │
│          return habit                                │
└──────────────────────────────────────────────────────┘

REMOVIDO:
├─ # TODO: Implementar cache para performance
├─ # Complexidade: O(n) - pode melhorar
├─ # Validar entrada
└─ # Criar instância

MANTIDO:
├─ Docstrings completas (""")
├─ Código funcional
└─ Type hints
```

---

## [DIAGRAMA 5] COMPARAÇÃO REPOS

```terminal
┌────────────────────────────┬────────────────────────────┐
│        GITLAB              │         GITHUB             │
├────────────────────────────┼────────────────────────────┤
│ [COMMITS]                  │ [COMMITS]                  │
│ abc123 feat: Nova feature  │ abc123 feat: Nova feature  │
│ def456 fix: Corrige bug    │ def456 fix: Corrige bug    │
│ ghi789 docs: Atualiza      │ ghi789 docs: Atualiza      │
│        (IDÊNTICOS)         │        (IDÊNTICOS)         │
├────────────────────────────┼────────────────────────────┤
│ [CÓDIGO]                   │ [CÓDIGO]                   │
│ ├─ habit.py                │ ├─ habit.py                │
│ │   150 linhas             │ │   95 linhas              │
│ │   + comentários          │ │   - comentários          │
│ │   + docstrings           │ │   + docstrings           │
│ │                          │ │                          │
│ ├─ routine.py              │ ├─ routine.py              │
│ │   200 linhas             │ │   130 linhas             │
│ │   + comentários          │ │   - comentários          │
│ │                          │ │                          │
│ └─ timer.py                │ └─ timer.py                │
│     180 linhas             │     115 linhas             │
├────────────────────────────┼────────────────────────────┤
│ [DOCS]                     │ [DOCS]                     │
│ docs/                      │ (AUSENTE)                  │
│ ├─ 01-architecture/        │                            │
│ ├─ 02-diagrams/            │                            │
│ ├─ 03-decisions/           │                            │
│ ├─ 04-specifications/      │                            │
│ ├─ 05-testing/             │                            │
│ └─ ... (189 arquivos)      │                            │
│     ~15MB                  │     0 bytes                │
├────────────────────────────┼────────────────────────────┤
│ [CI/CD]                    │ [CI/CD]                    │
│ .gitlab-ci.yml             │ .github/workflows/ci.yml   │
│ ├─ 3 stages                │ ├─ 1 job                   │
│ ├─ 6 jobs                  │ ├─ 4 steps                 │
│ ├─ Coverage report         │ ├─ Coverage upload         │
│ └─ Deploy Pages            │ └─ Basic checks            │
├────────────────────────────┼────────────────────────────┤
│ [PROPÓSITO]                │ [PROPÓSITO]                │
│ Desenvolvimento interno    │ Showcase público           │
│ Time brasileiro            │ Portfolio/Recrutadores     │
│ Documentação completa      │ Código profissional        │
│ Commits PT-BR              │ Commits PT-BR              │
└────────────────────────────┴────────────────────────────┘
```

---

## [DIAGRAMA 6] SINCRONIZAÇÃO

```terminal
CENÁRIO: Desenvolvedor faz mudança e sincroniza ambos repos

[LOCAL]
├─ Branch: develop
├─ Commit: abc123 "feat: Nova funcionalidade"
└─ Arquivos: código + comentários + docs/

        │
        ├─────────────────┬──────────────────┐
        ▼                 ▼                  ▼
   [GITLAB]          [GITHUB]           [VALIDAÇÃO]
        │                 │                  │
        │ git push        │ ./scripts/       │
        │ origin develop  │ push-github.sh   │
        │                 │                  │
        ▼                 ▼                  │
   Pipeline GL       Actions GH              │
   ├─ test:unit     ├─ lint                  │
   ├─ test:integ    ├─ typecheck             │
   ├─ test:bdd      └─ test                  │
   ├─ lint                                   │
   └─ typecheck         │                    │
        │               │                    │
        ├───────────────┴────────────────────┤
        ▼                                    ▼
   [AMBOS PASSED]                      [VALIDAÇÃO OK]
        │
        └─────────────────────────────────────┐
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │  REPOS           │
                                    │  SINCRONIZADOS   │
                                    │                  │
                                    │  GitLab: abc123  │
                                    │  GitHub: abc123  │
                                    │                  │
                                    │  Histórico: OK   │
                                    │  Testes: OK      │
                                    │  Deploy: OK      │
                                    └──────────────────┘
```

---

## [DIAGRAMA 7] TROUBLESHOOTING

```terminal
[PROBLEMA] Pipeline falha
    │
    ├─ GitLab?
    │   ├─ Verificar logs: gitlab.com/.../pipelines
    │   ├─ Validar YAML: gitlab.com/.../ci/lint
    │   └─ Rodar local: gitlab-runner exec
    │
    └─ GitHub?
        ├─ Verificar logs: github.com/.../actions
        └─ Validar YAML: syntax checker

[PROBLEMA] Pre-commit falha
    │
    ├─ Corrigir erros
    │   ├─ ruff check --fix
    │   └─ pytest tests/unit
    │
    ├─ Skip temporário (emergência)
    │   └─ git commit --no-verify
    │
    └─ Verificar venv
        └─ source venv/bin/activate

[PROBLEMA] Push GitHub falha
    │
    ├─ Scripts existem?
    │   └─ ls -la scripts/*.sh scripts/*.py
    │
    ├─ Permissões OK?
    │   └─ chmod +x scripts/*.sh scripts/*.py
    │
    └─ Remote configurado?
        └─ git remote -v

[PROBLEMA] Histórico divergente
    │
    ├─ CRÍTICO: Commits diferentes!
    │   └─ Redesenhar estratégia
    │
    └─ Solução: Commits idênticos
        ├─ Mesmo hash em ambos
        └─ Apenas conteúdo diferente
```
