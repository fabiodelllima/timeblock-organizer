# Filosofia de Testes - TimeBlock Organizer

## Princípio Fundamental

**Todo teste deve validar uma Regra de Negócio documentada.**

## Pirâmide de Testes

```terminal
        ╱╲
       ╱E2E╲         ← Poucos, lentos, alto nível
      ╱──────╲
     ╱ INTEG  ╲      ← Moderados, médios, interação entre componentes
    ╱──────────╲
   ╱   UNIT     ╲    ← Muitos, rápidos, regras de negócio isoladas
  ╱──────────────╲
```

### Testes Unitários (Unit Tests)

**Objetivo:** Validar regras de negócio de forma isolada

**Localização:** `cli/tests/unit/`

**Características:**

- Testam uma função/método específico
- Usam mocks para dependências externas
- Rápidos (< 100ms por teste)
- Isolados (não dependem de DB, rede, filesystem)
- Validam lógica de negócio pura

**Exemplo:**

```python
def test_rn_event_001_detecta_sobreposicao_total(self):
    """RN-EVENT-001: Sistema detecta sobreposição total."""
    # Mock do banco de dados
    # Testa apenas a lógica de detecção
```

### Testes de Integração (Integration Tests)

**Objetivo:** Validar interação entre componentes

**Localização:** `cli/tests/integration/`

**Características:**

- Testam múltiplos componentes juntos
- Usam banco de dados real (SQLite in-memory)
- Moderados (< 1s por teste)
- Validam fluxos completos
- Verificam integrações (Service ↔ Model ↔ DB)

**Exemplo:**

```python
def test_rn_event_001_fluxo_completo_deteccao_conflitos(self):
    """RN-EVENT-001: Fluxo completo de detecção de conflitos."""
    # Banco real em memória
    # Testa Service → Model → DB → retorno
```

### Testes End-to-End (E2E Tests)

**Objetivo:** Validar sistema completo do ponto de vista do usuário

**Localização:** `cli/tests/e2e/`

**Características:**

- Testam CLI completa
- Banco de dados persistente (temporário)
- Lentos (1-5s por teste)
- Simulam interação real do usuário
- Validam comandos CLI completos

**Exemplo:**

```python
def test_rn_event_002_usuario_visualiza_conflitos_via_cli(self):
    """RN-EVENT-002: Usuário executa comando e vê conflitos."""
    # Executa: timeblock reschedule conflicts --date 2025-11-08
    # Valida output formatado no terminal
```

## Metodologia: Documentation-Driven Development (DDD)

### Ciclo de Desenvolvimento

```terminal
┌─────────────────────────────────────────────────────────┐
│                   1. DOCUMENTAÇÃO                       │
│  docs/04-specifications/business-rules/                 │
│  Define TODAS as regras de negócio (RN-XXX-YYY)         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   2. TESTES                             │
│  tests/{unit,integration,e2e}/                          │
│  Valida cada regra em diferentes níveis                 │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   3. IMPLEMENTAÇÃO                      │
│  src/timeblock/*                                        │
│  Implementa código para passar nos testes               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   4. VALIDAÇÃO                          │
│  pytest + ruff + mypy                                   │
│  Garante qualidade e aderência às regras                │
└─────────────────────────────────────────────────────────┘
```

## Estrutura de Testes

### Nomenclatura Obrigatória

Testes DEVEM seguir o padrão:

```python
class TestRN<DOMINIO><NUMERO><NomeRegra>:
    """RN-<DOMINIO>-<NUMERO>: Descrição da Regra."""

    def test_rn_<dominio>_<numero>_<cenario_especifico>(self):
        """RN-<DOMINIO>-<NUMERO>: Validação de cenário específico."""
```

**Exemplo:**

```python
class TestRNEvent001DeteccaoConflitosTemporais:
    """RN-EVENT-001: Detecção de Conflitos Temporais."""

    def test_rn_event_001_detecta_sobreposicao_total(self):
        """RN-EVENT-001: Sistema detecta sobreposição total."""
```

### Cobertura por Tipo de Teste

Para cada Regra de Negócio:

- **Unit:** Testa lógica isolada (100% das regras)
- **Integration:** Testa fluxo completo (80% das regras)
- **E2E:** Testa principais fluxos de usuário (20% das regras)

### Mapeamento Regra → Teste

| Documento                   | Testes Unit                        | Testes Integration                     | Testes E2E                   |
| --------------------------- | ---------------------------------- | -------------------------------------- | ---------------------------- |
| `event-reordering-rules.md` | `test_event_reordering_service.py` | `test_event_reordering_integration.py` | `test_reschedule_command.py` |

## Validação de Qualidade

Antes de QUALQUER commit, executar:

```bash
# 1. Formatação
ruff check --fix cli/

# 2. Verificação de tipos
mypy cli/src/timeblock/

# 3. Testes unitários (rápido)
pytest cli/tests/unit/ -v

# 4. Testes de integração
pytest cli/tests/integration/ -v

# 5. Testes E2E (opcional localmente, obrigatório CI)
pytest cli/tests/e2e/ -v

# 6. Cobertura (deve ser > 90%)
pytest --cov=src/timeblock --cov-report=term-missing
```

## Regras para Testes

### 1. Rastreabilidade

- Todo teste referencia explicitamente a RN que valida
- Docstring do teste cita o ID da regra: `"""RN-EVENT-001: ..."""`
- Nome da classe e método incluem identificador da regra

### 2. Completude

- Toda regra de negócio documentada TEM testes
- Testes cobrem casos: normal, limite, exceção, erro

### 3. Isolamento

- Cada teste valida UMA regra específica
- Testes não dependem de ordem de execução
- Usar fixtures para setup/teardown

### 4. Clareza

- Nome do teste descreve o cenário
- Docstring explica o que está sendo validado
- Código do teste é auto-explicativo

## Princípios Fundamentais

1. **Docs First**: Regra de negócio é documentada ANTES do código
2. **Test-Driven**: Testes são escritos ANTES da implementação
3. **Test Pyramid**: Muitos unit, moderados integration, poucos e2e
4. **Traceability**: Cada linha de código rastreia para uma RN
5. **Quality Gates**: ruff + mypy + pytest antes de commit
6. **Living Documentation**: Docs e testes evoluem juntos

## Benefícios

- **Alinhamento**: Código sempre alinhado com regras de negócio
- **Prevenção**: Bugs detectados antes de implementação
- **Documentação**: Testes servem como documentação viva
- **Refatoração**: Segurança para mudanças estruturais
- **Onboarding**: Novos desenvolvedores entendem sistema pelos testes
- **Confiabilidade**: Diferentes níveis de teste garantem robustez
