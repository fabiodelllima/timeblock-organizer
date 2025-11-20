# Checklist Implementação CI/CD Dual Repository

- **Data:** 2025-11-20
- **Documento:** 4/5 da série CI/CD Strategy
- **Tempo estimado:** 6-8 horas (dividido em 4 sprints)

---

## [VISÃO GERAL]

```terminal
Sprint 3.1: Documentação    [1-2h] ← CONCLUÍDO
Sprint 3.2: Scripts         [2-3h] ← PRÓXIMO
Sprint 3.3: Pipelines       [2-3h]
Sprint 3.4: Débito Técnico  [2-3h] [P0]
```

---

## [SPRINT 3.1] DOCUMENTAÇÃO ✓

### Status: CONCLUÍDO

- [x] Criar branch feature/cicd-docs
- [x] Documento 1/5: current-state-and-cicd-strategy.md
- [x] Documento 2/5: cicd-quickstart-guide.md
- [x] Documento 3/5: cicd-workflow-diagram.md
- [x] Configuração: .ruff.toml
- [x] Documento 4/5: cicd-implementation-checklist.md
- [ ] Documento 5/5: cicd-files-index.md (próximo)
- [ ] Merge para develop

### Próximo Passo

Criar documento 5/5, então merge:

```bash
git checkout develop
git merge --no-ff feature/cicd-docs
```

---

## [SPRINT 3.2] SCRIPTS

### Objetivo

Criar 5 scripts de automação CI/CD.

### Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/cicd-scripts
```

### Arquivos

#### 1. scripts/strip-comments.py

**Propósito:** Remove comentários inline, preserva docstrings, compacta código

**Funcionalidades:**

- Remove linhas começando com #
- Remove # inline (após código)
- Preserva docstrings (""" ou ''')
- Mantém linha entre métodos/classes
- Remove linhas em branco extras

**Estratégia GitLab vs GitHub:**

- GitLab: comentários para separar blocos (ao invés de linhas)
- GitHub: sem comentários, compacto

**Exemplo Transformação:**

GitLab:

```python
def create_habit(self, title: str) -> Habit:
    """Cria novo hábito."""
    if not title:
        raise ValueError("Título obrigatório")
    # Criar e persistir
    habit = Habit(title=title)
    self.session.add(habit)
    return habit
```

GitHub (após strip):

```python
def create_habit(self, title: str) -> Habit:
    """Cria novo hábito."""
    if not title:
        raise ValueError("Título obrigatório")
    habit = Habit(title=title)
    self.session.add(habit)
    return habit
```

**Criar arquivo:** Ver Sprint 3.2 detalhado em quickstart-guide.md

**Commit:**

```bash
git add scripts/strip-comments.py
git commit -m "feat(cicd): Adiciona script remoção comentários

Funcionalidades:
- Remove comentários inline
- Preserva docstrings
- Compacta código
- Mantém estrutura classes/métodos

Sprint: 3.2 CI/CD Scripts
"
```

#### 2. scripts/push-github.sh

**Propósito:** Transforma código e push para GitHub

**Processo:**

1. Cria branch temporária
2. Remove docs/ do git
3. Executa strip-comments.py
4. Commit transformações
5. Push force para GitHub
6. Cleanup

**Importante:** Mantém commits idênticos (mesmo hash)

**Commit:**

```bash
git add scripts/push-github.sh
git commit -m "feat(cicd): Adiciona script push GitHub

Transforma código para GitHub:
- Remove docs/
- Strip comentários
- Mantém commits idênticos

Sprint: 3.2 CI/CD Scripts
"
```

#### 3. scripts/push-gitlab.sh

**Propósito:** Push direto para GitLab (código completo)

**Simples:** `git push origin <branch>`

**Commit:**

```bash
git add scripts/push-gitlab.sh
git commit -m "feat(cicd): Adiciona script push GitLab

Push direto mantendo código completo.

Sprint: 3.2 CI/CD Scripts
"
```

#### 4. .git/hooks/pre-commit

**Propósito:** Validações automáticas antes de commit

**Validações:**

- [1/4] ruff format
- [2/4] ruff check --fix
- [3/4] mypy (warning only)
- [4/4] pytest unit tests (bloqueante)

**Commit:**

```bash
git add .git/hooks/pre-commit
git commit -m "feat(cicd): Adiciona pre-commit hooks

Validações automáticas antes de commit.

Sprint: 3.2 CI/CD Scripts
"
```

#### 5. scripts/test-cicd.sh

**Propósito:** Validar instalação scripts CI/CD

**Testa:**

- Existência de arquivos
- Permissões execução
- Pre-commit instalado

**Commit:**

```bash
git add scripts/test-cicd.sh
git commit -m "test(cicd): Adiciona script validação CI/CD

Valida instalação completa scripts.

Sprint: 3.2 CI/CD Scripts
"
```

### Merge Sprint 3.2

```bash
git checkout develop
git merge --no-ff feature/cicd-scripts -m "feat(cicd): Merge Sprint 3.2 - Scripts

5 scripts criados e testados.

Sprint: 3.2 CI/CD Scripts completo
"
```

---

## [SPRINT 3.3] PIPELINES

### Objetivo

Configurar CI/CD GitLab e GitHub.

### Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/cicd-pipelines
```

### Configurar Remotes

#### 1. Verificar atual

```bash
git remote -v
```

#### 2. Configurar GitLab como origin

Se atual é GitHub:

```bash
git remote rename origin github
git remote add origin git@gitlab.com:USER/timeblock-organizer.git
```

Se não tem remote:

```bash
git remote add origin git@gitlab.com:USER/timeblock-organizer.git
git remote add github git@github.com:USER/timeblock-organizer.git
```

#### 3. Configurar default pull

```bash
git config branch.develop.remote origin
git config branch.main.remote origin
```

#### 4. Validar

```bash
git remote -v
# Deve mostrar origin (GitLab) e github (GitHub)
```

### Arquivos

#### 5. .gitlab-ci.yml

**Pipeline 3 stages:**

- TEST: unit, integration, bdd, lint, typecheck
- BUILD: mkdocs docs
- DEPLOY: GitLab Pages

**Commit:**

```bash
git add .gitlab-ci.yml
git commit -m "ci(gitlab): Adiciona pipeline completo

Pipeline com testes, build docs, deploy Pages.

Sprint: 3.3 CI/CD Pipelines
"
```

#### 6. .github/workflows/ci.yml

**Workflow básico:**

- Lint (ruff)
- Typecheck (mypy)
- Test (pytest)
- Coverage (codecov)

**Commit:**

```bash
git add .github/workflows/ci.yml
git commit -m "ci(github): Adiciona GitHub Actions

Workflow básico validação.

Sprint: 3.3 CI/CD Pipelines
"
```

### Primeiro Push

```bash
# GitLab
git push -u origin feature/cicd-pipelines

# GitHub (teste)
./scripts/push-github.sh
```

### Validação

- [ ] Pipeline GitLab passou
- [ ] GitHub Actions passou
- [ ] Commits idênticos
- [ ] Arquivos diferentes (docs/)

```bash
# Verificar diferenças
git fetch github
git diff origin/feature/cicd-pipelines github/feature/cicd-pipelines
```

### Merge Sprint 3.3

```bash
git checkout develop
git merge --no-ff feature/cicd-pipelines -m "ci: Merge Sprint 3.3 - Pipelines

Configurado CI/CD em ambos repositórios.

Sprint: 3.3 CI/CD Pipelines completo
"
```

---

## [SPRINT 3.4] DÉBITO TÉCNICO [P0]

### Objetivo

Corrigir 93 testes quebrados Sprint 1.

### Branch

```bash
git checkout develop
git pull origin develop
git checkout -b fix/sprint1-test-debt
```

### Correções

#### P0 - Import Crítico (5 min)

Adicionar em `cli/src/timeblock/commands/habit.py`:

```python
from timeblock.models import HabitInstance
```

**Commit:**

```bash
git add cli/src/timeblock/commands/habit.py
git commit -m "fix(commands): Adiciona import HabitInstance

Corrige NameError.

Issue: Sprint 1 Technical Debt (P0)
"
```

#### P1 - Status.PLANNED → Status.PENDING (30 min)

```bash
find cli/tests -name "*.py" -exec sed -i 's/Status\.PLANNED/Status.PENDING/g' {} \;

git add cli/tests/
git commit -m "fix(tests): Atualiza Status.PLANNED para PENDING

Atualiza 60+ testes.

Issue: Sprint 1 Technical Debt (P1)
"
```

#### P1 - Routine.is_active default (10 min)

```bash
# Ajustar fixtures conforme necessário

git add cli/tests/
git commit -m "fix(tests): Ajusta default is_active

Default mudou para False.

Issue: Sprint 1 Technical Debt (P1)
"
```

#### P2 - Remover Obsoletos (5 min)

```bash
rm cli/tests/unit/test_models/test_habit_instance_user_override.py
rm cli/tests/unit/test_commands/test_habit_adjust.py

git add -A
git commit -m "refactor(tests): Remove testes obsoletos

Campos não existem mais.

Issue: Sprint 1 Technical Debt (P2)
"
```

### Validação

```bash
cd cli
source venv/bin/activate
pytest tests/ -v

# Esperado: 487/487 PASSED
```

### Merge

```bash
git checkout develop
git merge --no-ff fix/sprint1-test-debt -m "fix(tests): Resolve débito técnico Sprint 1

487/487 testes passando.

Sprint: 3.4 Débito Técnico completo
"

# Push ambos
git push origin develop
./scripts/push-github.sh
```

---

## [VALIDAÇÃO FINAL]

### Checklist

- [ ] 5 documentos criados
- [ ] 5 scripts funcionais
- [ ] 2 pipelines ativos
- [ ] 487/487 testes passando
- [ ] Coverage > 95%
- [ ] Commits idênticos
- [ ] Arquivos diferentes
- [ ] Remotes configurados

### Comandos

```bash
# Testes
cd cli && pytest tests/ -v

# Coverage
pytest tests/ --cov=src/timeblock

# Remotes
git remote -v

# Commits
git log origin/develop --oneline -10
git log github/develop --oneline -10

# Diferenças
git diff origin/develop github/develop
```

---

## [PRÓXIMOS PASSOS]

### Sprint 4: STREAK (2-3 dias)

Implementar 3 BRs:

- BR-STREAK-001: Algorithm
- BR-STREAK-002: Break Conditions
- BR-STREAK-003: Maintain Conditions

### Sprint 5: E2E Tests (1-2 dias)

Criar 4 testes workflow completo.

### Sprint 6: Release v1.4.0 (1 dia)

Preparar release MVP.
