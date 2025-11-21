# Índice Completo Arquivos CI/CD

- **Data:** 2025-11-20
- **Documento:** 5/5 da série CI/CD Strategy
- **Status:** Referência rápida

---

## [DOCUMENTAÇÃO] docs/10-meta/

### 1. current-state-and-cicd-strategy.md

**Propósito:** Análise estado atual e estratégia dual repository

**Quando consultar:** Entender decisões arquiteturais

**Tamanho:** ~300 linhas

**Conteúdo:**

- Estado atual do projeto
- Motivação dual repository
- Estratégia GitLab vs GitHub
- Transformações de código
- Workflows detalhados

### 2. cicd-quickstart-guide.md

**Propósito:** Setup rápido CI/CD em 30 minutos

**Quando consultar:** Primeira configuração ou troubleshooting

**Tamanho:** ~200 linhas

**Conteúdo:**

- Configuração remotes
- Primeiro push dual
- Validação funcionamento
- Troubleshooting comum

### 3. cicd-workflow-diagram.md

**Propósito:** Diagramas visuais ASCII

**Quando consultar:** Entender fluxos visualmente

**Tamanho:** ~400 linhas

**Conteúdo:**

- 7 diagramas ASCII completos
- Arquitetura geral
- Fluxo de commits
- Transformação de arquivos
- Troubleshooting visual

### 4. cicd-implementation-checklist.md

**Propósito:** Checklist passo-a-passo 4 sprints

**Quando consultar:** Implementar CI/CD do zero

**Tamanho:** ~500 linhas

**Conteúdo:**

- Sprint 3.1: Docs (1-2h)
- Sprint 3.2: Scripts (2-3h)
- Sprint 3.3: Pipelines (2-3h)
- Sprint 3.4: Débito técnico (2-3h)
- Comandos exatos executar
- Validações intermediárias

### 5. cicd-files-index.md (este arquivo)

**Propósito:** Índice navegável todos arquivos

**Quando consultar:** Encontrar arquivo específico rapidamente

**Tamanho:** ~300 linhas

---

## [CONFIGURAÇÃO] Arquivos raiz

### cli/.ruff.toml

**Propósito:** Configuração linter/formatter

**Localização:** `cli/.ruff.toml`

**Quando modificar:** Ajustar regras lint

**Conteúdo:**

```toml
line-length = 100
[format]
indent-style = "space"
quote-style = "double"
[lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "RUF"]
ignore = ["B904", "W291", "W293", "E501", "RUF022"]
[lint.isort]
known-first-party = ["timeblock"]
```

**Regras ignoradas:**

- B904: `raise` em `except` (padrão typer)
- W291: Trailing whitespace SQL
- W293: Whitespace em docstrings
- E501: Linha muito longa
- RUF022: `__all__` não ordenado

---

## [SCRIPTS] scripts/ (Sprint 3.2)

### scripts/strip-comments.py

**Status:** [TODO] A criar Sprint 3.2

**Propósito:** Remove comentários inline, preserva docstrings

**Uso:** `python scripts/strip-comments.py`

**Funcionalidades:**

- Remove linhas começando com #
- Remove # inline (após código)
- Preserva docstrings completas
- Mantém linha entre métodos/classes
- Compacta código removendo linhas vazias extras

**Exemplo transformação:**

```python
# GitLab (antes):
def test():
    # Validação
    if True:
        pass
    # Processamento
    return 42

# GitHub (depois):
def test():
    if True:
        pass
    return 42
```

### scripts/push-github.sh

**Status:** [TODO] A criar Sprint 3.2

**Propósito:** Transforma e push para GitHub

**Uso:** `./scripts/push-github.sh`

**Processo:**

1. Cria branch temporária
2. Remove docs/ do git
3. Executa strip-comments.py
4. Commit transformações
5. Push force para GitHub
6. Cleanup (volta branch original)

**Importante:** Mantém commits idênticos (mesmo hash)

### scripts/push-gitlab.sh

**Status:** [TODO] A criar Sprint 3.2

**Propósito:** Push direto GitLab (código completo)

**Uso:** `./scripts/push-gitlab.sh`

**Simples:** `git push origin <branch>`

### scripts/test-cicd.sh

**Status:** [TODO] A criar Sprint 3.2

**Propósito:** Valida instalação scripts

**Uso:** `./scripts/test-cicd.sh`

**Testa:**

- Existência de arquivos
- Permissões execução
- Pre-commit instalado

---

## [HOOKS] .git/hooks/ (Sprint 3.2)

### .git/hooks/pre-commit

**Status:** [TODO] A criar Sprint 3.2

**Propósito:** Validações antes de commit

**Executável:** chmod +x necessário

**Validações:**

- [1/4] ruff format (auto-format)
- [2/4] ruff check --fix (lint)
- [3/4] mypy (warning only)
- [4/4] pytest unit tests (bloqueante)

**Importante:** Bloqueia commit se unit tests falharem

---

## [PIPELINES] CI/CD (Sprint 3.3)

### .gitlab-ci.yml

**Status:** [TODO] A criar Sprint 3.3

**Propósito:** Pipeline GitLab CI/CD

**Stages:**

1. TEST: unit, integration, bdd, lint, typecheck
2. BUILD: mkdocs docs (develop, main)
3. DEPLOY: GitLab Pages (main only)

**Triggers:**

- Push para qualquer branch
- Merge requests

**Artifacts:**

- Coverage reports (1 semana)
- Docs built (1 semana)
- GitLab Pages (permanente)

### .github/workflows/ci.yml

**Status:** [TODO] A criar Sprint 3.3

**Propósito:** GitHub Actions workflow

**Jobs:**

- Lint (ruff)
- Typecheck (mypy - warning)
- Test (pytest unit + integration)
- Coverage (codecov upload)

**Triggers:**

- Push para develop, main
- Pull requests

**Matrix:** Python 3.13

---

## [REMOTES] Configuração Git

### Remotes esperados

```bash
git remote -v
# origin (GitLab)  - código completo
# github (GitHub)  - código transformado
```

### Configuração branches

```bash
git config branch.develop.remote origin
git config branch.main.remote origin
```

### Default push

- **develop:** origin (GitLab)
- **main:** origin (GitLab)
- **GitHub:** manual via script

---

## [WORKFLOW] Desenvolvimento diário

### Fluxo normal

```bash
# 1. Trabalhar normalmente
git add .
git commit -m "feat: Nova feature"

# 2. Push GitLab (automático)
git push origin develop

# 3. Push GitHub (manual, quando necessário)
./scripts/push-github.sh
```

### Pre-commit automático

```
[INFO] Executando pre-commit hooks...
[1/4] Ruff format...
[2/4] Ruff check...
[3/4] Mypy...
[4/4] Pytest (unit tests)...
[OK] Pre-commit hooks passaram
```

---

## [DIFERENÇAS] GitLab vs GitHub

### GitLab (Privado - Desenvolvimento)

**Contém:**

- [OK] Código completo
- [OK] Comentários inline
- [OK] docs/ completo
- [OK] Histórico completo
- [OK] Scripts CI/CD
- [OK] Configurações

**Propósito:** Desenvolvimento ativo e colaboração

### GitHub (Público - Showcase)

**Contém:**

- [OK] Código compacto (sem comentários)
- [OK] cli/ apenas (sem docs/)
- [OK] Commits idênticos (mesmo hash)
- [OK] README básico
- [OK] CI básico

**Propósito:** Portfolio e showcase técnico

---

## [COMMITS] Formato padrão

### Formato

```terminal
type(scope): Descrição em Português

Detalhes opcionais:
- Métrica 1
- Métrica 2

Issue: #123
Sprint: X.Y Nome
```

### Types válidos

- feat: Nova feature
- fix: Correção bug
- refactor: Refatoração
- test: Adiciona/modifica testes
- docs: Documentação
- chore: Manutenção
- perf: Performance
- ci: CI/CD
- style: Formatação

### Exemplo completo

```terminal
feat(habit): Adiciona comando skip com categorização

Implementa BR-HABIT-SKIP-001:
- 3 categorias de skip (justified, unjustified, external)
- Validação nota (max 500 chars)
- 18 scenarios BDD
- 14 unit tests
- Coverage 99%

Closes #42
Sprint: 2.0 Skip Categorization
```

---

## [TESTES] Estrutura

### Hierarquia

```terminal
cli/tests/
├── unit/           # 70-75% (fast, isolated)
├── integration/    # 20%    (medium, service+DB)
└── e2e/            # 5-10%  (slow, full CLI)
```

### Naming convention

```python
# Arquivo
tests/unit/test_services/test_habit_service.py

# Classe
class TestBRHabit001:
    """BR-HABIT-001: Validação título obrigatório."""

# Método
def test_br_habit_001_rejects_empty_title(self):
    """BR-HABIT-001: Deve rejeitar título vazio."""
```

### Coverage target

- **Unit:** > 95%
- **Integration:** > 80%
- **Global:** > 90%

---

## [MÉTRICAS] Quality gates

### Ruff (linter)

- [OK] All checks passed
- [OK] Ignores configurados apropriadamente
- [OK] Imports organizados
- [OK] Sem código não usado

### Mypy (type check)

- [WARN] Warning only (não bloqueia)
- [OK] Cobertura tipos > 80%

### Pytest (tests)

- [OK] 100% passing (bloqueante)
- [OK] Coverage > 90%
- [OK] Tempo < 30s (unit)

### Git (commits)

- [OK] Mensagens em PT-BR
- [OK] Conventional commits
- [OK] Commits atômicos
- [OK] Branch gitflow

---

## [TROUBLESHOOTING] Problemas comuns

### Ruff não encontra .ruff.toml

**Sintoma:** Ignores não funcionam

**Solução:** Arquivo deve estar em `cli/.ruff.toml`

**Comando:** `cd cli && ruff check src/timeblock`

### Pre-commit hook não executa

**Sintoma:** Commit passa sem validações

**Solução:** Verificar permissões

**Comando:** `chmod +x .git/hooks/pre-commit`

### Push GitHub falha

**Sintoma:** Remote not found

**Solução:** Configurar remote

**Comando:** `git remote add github git@github.com:USER/repo.git`

### Commits diferentes em GitLab e GitHub

**Sintoma:** Histórico diverge

**Solução:** Usar `push-github.sh` sempre

**Comando:** `./scripts/push-github.sh`

### Pipeline GitLab falha

**Sintoma:** Tests passam local, falham CI

**Solução:** Verificar requirements.txt atualizado

**Comando:** `pip freeze > cli/requirements.txt`

---

## [ROADMAP] Próximas features CI/CD

### Sprint 4+: Melhorias

- [ ] Automatic release notes
- [ ] Version bump automation
- [ ] Deploy preview environments
- [ ] Performance benchmarks
- [ ] Security scanning (Bandit)
- [ ] Dependency updates (Dependabot)

### v2.0: Sync offline-first

- [ ] Queue-based sync
- [ ] Conflict resolution
- [ ] Migration offline-first
- [ ] Android/Termux CI

---

## [REFERÊNCIAS] Links úteis

### Documentação oficial

- Ruff: <https://docs.astral.sh/ruff/>
- GitLab CI: <https://docs.gitlab.com/ee/ci/>
- GitHub Actions: <https://docs.github.com/actions>
- Pytest: <https://docs.pytest.org/>

### TimeBlock docs

- [ROADMAP](../ROADMAP.md)
- [Architecture](../03-architecture/)
- [Business Rules](../04-specifications/business-rules/)
- [Testing](../05-testing/)

---

**Navegação série CI/CD:**

1. [Estado Atual](current-state-and-cicd-strategy.md)
2. [Quickstart](cicd-quickstart-guide.md)
3. [Diagramas](cicd-workflow-diagram.md)
4. [Checklist](cicd-implementation-checklist.md)
5. [Índice](cicd-files-index.md)
