# Development Workflow

## Gitflow

```shell
git checkout develop
git checkout -b feat/feature-name
# code
git commit -m "feat(scope): Description"
git checkout develop
git merge --no-ff feat/feature-name
```

## Commits

```terminal
feat(models): Adiciona campo user_override
fix(services): Corrige validação de RRULE
docs(adr): Cria ADR-009
test(habit): Adiciona cenário de skip
```
