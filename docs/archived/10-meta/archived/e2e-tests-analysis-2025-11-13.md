# Análise Técnica: E2E Tests Quebrados

- **Data:** 13 de novembro de 2025
- **Tipo:** Análise Técnica + Plano de Correção
- **Status:** [ATIVO]

---

## 1. PROBLEMA IDENTIFICADO

### 1.1 Sintomas

Durante implementação do Scenario 3 (Event Creation), descobrimos que:

1. **Testes E2E existentes estão falhando** (2 de 2)
2. **Comando `init` retorna exit code 1** em ambiente de teste
3. **Fixture `isolated_db` não está sendo utilizada** corretamente
4. **Comandos CLI mudaram** mas testes não foram atualizados

### 1.2 Evidências

#### **Teste 1: test_br_habit_complete_daily_workflow**

```bash
AssertionError: Sistema deve inicializar com sucesso
assert 1 == 0
 +  where 1 = <Result SystemExit(1)>.exit_code
```

#### **Teste 2: test_br_event_conflict_detection_and_resolution**

```bash
AssertionError: missing option '--end' / '-e'.
```

#### **Causa Raiz Identificada:**

- `isolated_db` fixture definida mas nunca usada
- Banco de dados não isolado entre testes
- Comandos CLI esperam parâmetros diferentes

---

## 2. ANÁLISE DE CAUSA RAIZ

### 2.1 Problema do Banco de Dados

**Código Atual (Incorreto):**

```python
@pytest.fixture
def isolated_db(tmp_path: Path) -> Path:
    """Cria banco de dados temporário isolado para E2E tests."""
    db_path = tmp_path / "test.db"
    return db_path  # <- Retorna mas nunca é usado!

def test_br_habit_complete_daily_workflow(self, isolated_db: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["init"])  # <- Não usa isolated_db!
```

**Solução Necessária:**

```python
def test_br_habit_complete_daily_workflow(
    self, isolated_db: Path, monkeypatch: MonkeyPatch
) -> None:
    # Configurar variável de ambiente ANTES de invocar CLI
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))

    runner = CliRunner()
    result = runner.invoke(app, ["init"])  # Agora usa banco isolado!
```

### 2.2 Problema da Assinatura de Comandos

**Comando `habit create` - Atual:**

```python
def create_habit(
    title: str = typer.Option(..., "--title", "-t"),
    start: str = typer.Option(..., "--start", "-s"),
    end: str = typer.Option(..., "--end", "-e"),      # <- end, não duration
    repeat: str = typer.Option(..., "--repeat", "-r"), # <- repeat, não recurrence
    ...
)
```

**Testes Usam (Incorreto):**

```python
result = runner.invoke(app, [
    "habit", "create", "Meditação",
    "--start", "06:00",
    "--duration", "20",      # <- Opção inexistente!
    "--recurrence", "EVERYDAY"  # <- Opção inexistente!
])
```

**Correção Necessária:**

```python
result = runner.invoke(app, [
    "habit", "create",
    "--title", "Meditação",  # <- Sempre usar --title explícito
    "--start", "06:00",
    "--end", "06:20",        # <- Usar --end ao invés de --duration
    "--repeat", "EVERYDAY"   # <- Usar --repeat ao invés de --recurrence
])
```

### 2.3 Problema do `RoutineService`

**Erro:**

```bash
AttributeError: 'RoutineService' object has no attribute 'get_active_routine'
```

**Métodos Disponíveis:**

```python
# src/timeblock/services/routine_service.py
def create_routine(self, name: str) -> Routine
def get_routine(self, routine_id: int) -> Routine | None
def list_routines(self, active_only: bool = True) -> list[Routine]
def activate_routine(self, routine_id: int) -> None
def deactivate_routine(self, routine_id: int) -> None
def delete_routine(self, routine_id: int) -> None
```

**Solução:**
O método `get_active_routine()` não existe. Código em `habit.py` está errado e precisa ser corrigido.

---

## 3. IMPACTO E SEVERIDADE

### 3.1 Impacto Funcional

**CRÍTICO:** E2E tests são a última linha de defesa

- Validam workflows completos de usuário
- Detectam quebras de integração entre componentes
- Garantem que CLI funciona end-to-end

**Situação Atual:**

- 0 de 2 E2E tests passando (0%)
- Não temos garantia de que workflows funcionam
- Bugs podem chegar em produção

### 3.2 Impacto no Desenvolvimento

**BLOQUEANTE para Fase 1:**

- Não podemos adicionar novos E2E tests sem corrigir a base
- Testes quebrados geram ruído (falsos positivos)
- Desenvolvedores param de confiar nos testes

### 3.3 Severidade

**ALTA:** Deve ser corrigido IMEDIATAMENTE antes de qualquer novo desenvolvimento

---

## 4. PLANO DE CORREÇÃO

### 4.1 Fase 0: Correção de E2E Tests Existentes (NOVO)

**Objetivo:** Fazer 2 testes E2E existentes passarem

**Tarefas:**

1. Criar BDD scenarios para testes existentes
2. Corrigir fixture `isolated_db` + `monkeypatch`
3. Atualizar comandos CLI para assinatura correta
4. Investigar e corrigir `get_active_routine()` em `habit.py`
5. Executar testes até passarem 100%
6. Commit de correção

**Estimativa:** 1h

**BRs Cobertas:**

- BR-HABIT-001: Criação de hábitos
- BR-HABIT-002: Geração de instâncias
- BR-HABIT-003: Completar hábito
- BR-EVENT-001: Detecção de conflitos
- BR-EVENT-002: Proposta de reorganização

### 4.2 Fase 1: Novos E2E Tests (Após Fase 0)

**Objetivo:** Adicionar 3 novos scenarios E2E

**Tarefas:**

1. Scenario 3: Event Creation Workflow
2. Scenario 4: Timer Lifecycle Workflow
3. Scenario 5: Event Reordering Workflow

**Estimativa:** 2.5h (45min + 45min + 60min)

---

## 5. CENÁRIOS BDD (Gherkin)

### 5.1 Scenario Existente 1: Habit Lifecycle

```gherkin
Feature: Workflow Completo de Hábitos
  Como usuário do TimeBlock
  Quero criar, gerar e completar hábitos
  Para gerenciar minha rotina diária

  Background:
    Given sistema TimeBlock inicializado
    And banco de dados limpo e isolado

  Scenario: Criar hábito diário e marcar como completo
    Given uma rotina ativa existe
    When eu crio hábito "Meditação" às 06:00-06:20 repetindo EVERYDAY
    And eu gero instâncias para 7 dias
    And eu listo agenda de hoje
    Then devo ver hábito "Meditação" às 06:00
    When eu marco instância #1 como completa
    And eu listo agenda de hoje novamente
    Then devo ver indicador visual de conclusão

  BRs Validadas:
    - BR-HABIT-001: Criação de hábitos em rotinas
    - BR-HABIT-002: Geração de instâncias de hábitos
    - BR-HABIT-003: Completar instância de hábito
```

### 5.2 Scenario Existente 2: Conflict Detection

```gherkin
Feature: Detecção e Resolução de Conflitos
  Como usuário do TimeBlock
  Quero que o sistema detecte conflitos de horário
  Para reorganizar minha agenda automaticamente

  Background:
    Given sistema TimeBlock inicializado
    And banco de dados limpo e isolado

  Scenario: Sistema detecta conflito e propõe reorganização
    Given uma rotina ativa existe
    When eu crio hábito "Exercício" às 09:00-10:00
    And eu crio hábito "Leitura" às 09:30-10:30
    And eu gero instâncias para 1 dia
    And eu ajusto hábito #1 para 09:00-10:00
    Then sistema deve avisar sobre conflito detectado
    And sistema deve propor reorganização automática

  BRs Validadas:
    - BR-EVENT-001: Detecção de conflitos de horário
    - BR-EVENT-002: Proposta de reorganização automática
```

---

## 6. CHECKLIST DE CORREÇÃO

### 6.1 Documentação

- [x] Análise técnica completa
- [ ] BDD scenarios documentados
- [ ] Comandos CLI documentados

### 6.2 Código

- [ ] Fixture `isolated_db` corrigida
- [ ] Comando `habit create` corrigido nos testes
- [ ] Método `get_active_routine()` investigado
- [ ] 2 testes E2E existentes passando

### 6.3 Validação

- [ ] pytest tests/e2e/test_habit_lifecycle.py -v (2/2 passando)
- [ ] Banco isolado funcionando (verificar tmp_path)
- [ ] Sem side effects entre testes

---

## 7. LIÇÕES APRENDIDAS

### 7.1 Problema de Processo

**O que aconteceu:**

- Testes E2E foram criados mas nunca executados regularmente
- Comandos CLI mudaram mas testes não foram atualizados
- Fixture foi criada mas implementação ficou incompleta

**Prevenção Futura:**

- Executar suite E2E completa antes de cada release
- CI/CD deve bloquear merge se E2E tests falharem
- Code review deve verificar atualização de testes

### 7.2 Importância de TDD

**Filosofia Violada:**

- Código mudou sem testes acompanharem
- Testes se tornaram "documentação desatualizada"

**Reforço da Filosofia:**

- DOCUMENTATION > BDD > TESTS > CODE
- Testes são IMUTÁVEIS
- Se teste quebra, código está errado (ou teste precisa ser atualizado COM justificativa documentada)

---

## 8. PRÓXIMOS PASSOS

### Imediato (Hoje)

1. Criar documento BDD completo
2. Corrigir fixture isolated_db
3. Atualizar comandos nos testes
4. Fazer 2 testes passarem

### Curto Prazo (Esta Semana)

1. Adicionar 3 novos scenarios E2E
2. Garantir 5/5 E2E tests passando
3. Merge para develop

### Médio Prazo (Próximo Sprint)

1. Configurar CI/CD para executar E2E tests
2. Adicionar pre-commit hook para E2E tests
3. Criar guia de "Como Escrever E2E Tests"

---

**Data:** 13 de novembro de 2025

**Versão:** 1.0

**Status:** [ATIVO - Correção em andamento]

**Última atualização:** 2025-11-13 09:00 BRT
