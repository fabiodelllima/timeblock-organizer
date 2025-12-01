# Sprint 1.3 - Logging Básico

**Duração:** 4h

**Objetivo:** Implementar sistema de logging estruturado

---

## Fase 1: Análise e Design (30min)

### Objetivos

- Mapear pontos críticos para logging
- Definir estrutura de logs
- Escolher biblioteca (Python logging padrão)

### Pontos Críticos Identificados

**Services (Alta prioridade):**

- `HabitInstanceService` - operações CRUD
- `EventReorderingService` - detecção de conflitos
- `TaskService` - criação de tarefas

**Database (Média prioridade):**

- `engine.py` - conexões
- Migrations - aplicação de schemas

**Commands (Baixa prioridade - v1.3.0):**

- CLI commands - ações do usuário

### Estrutura de Logs

```python
# Níveis:
DEBUG   - Detalhes internos (desenvolvimento)
INFO    - Operações normais (produção)
WARNING - Comportamentos inesperados mas não críticos
ERROR   - Erros que impedem operação

# Formato:
[2025-11-03 14:30:45] [INFO] [HabitInstanceService] generate_instances: Created 7 instances for habit_id=1
[2025-11-03 14:30:46] [ERROR] [HabitInstanceService] mark_completed: Instance 999 not found
```

---

## Fase 2: Implementação Core (2h)

### Tarefa 1: Módulo de Logging (30min)

**Arquivo:** `cli/src/timeblock/utils/logger.py`

```python
"""Sistema de logging estruturado para TimeBlock."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Path | None = None,
    max_bytes: int = 10_000_000,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Configura logger com formato estruturado.

    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        level: Nível mínimo (DEBUG, INFO, WARNING, ERROR)
        log_file: Caminho do arquivo de log (None = console only)
        max_bytes: Tamanho máximo antes de rotação
        backup_count: Número de backups mantidos

    Returns:
        Logger configurado
    """
```

### Tarefa 2: Adicionar Logs em HabitInstanceService (45min)

**Operações a logar:**

- `generate_instances()` - início, fim, quantos criados
- `adjust_instance_time()` - ajuste, conflitos detectados
- `mark_completed()` - sucesso, falha (not found)
- `mark_skipped()` - sucesso, falha (not found)

**Exemplo:**

```python
logger = setup_logger(__name__)

def generate_instances(...):
    logger.info(f"Generating instances for habit_id={habit_id}, period={start_date} to {end_date}")
    # ... código existente ...
    logger.info(f"Created {len(instances)} instances for habit_id={habit_id}")
```

### Tarefa 3: Adicionar Logs em EventReorderingService (45min)

**Operações a logar:**

- `detect_conflicts()` - início, conflitos encontrados
- `propose_reordering()` - propostas geradas
- Erros de validação

---

## Fase 3: Testes (1h)

### Tarefa 4: Testes Unitários de Logger (30min)

**Arquivo:** `cli/tests/unit/test_utils/test_logger.py`

**Testes:**

1. `test_setup_logger_console_only` - logger sem arquivo
2. `test_setup_logger_with_file` - logger com arquivo
3. `test_log_rotation` - verifica criação de backups
4. `test_log_levels` - DEBUG, INFO, WARNING, ERROR

### Tarefa 5: Testes de Integração (30min)

**Arquivo:** `cli/tests/integration/test_logging_integration.py`

**Testes:**

1. `test_service_logs_creation` - verifica logs em operações
2. `test_service_logs_errors` - verifica logs de erro
3. `test_log_file_created` - arquivo criado no lugar certo

---

## Fase 4: Documentação (30min)

### Tarefa 6: Atualizar Documentação

**Arquivos:**

- `docs/04-specifications/logging-strategy.md` (novo)
- `README.md` - seção sobre logs
- Docstrings completas

---

## Critérios de Sucesso

- [ ] Módulo logger.py implementado e testado
- [ ] Logs adicionados em HabitInstanceService
- [ ] Logs adicionados em EventReorderingService
- [ ] 6+ testes de logging (100% passando)
- [ ] Documentação completa
- [ ] Log rotation funcional

---

## Riscos

**Baixo Risco:**

- Logging é feature isolada
- Não afeta funcionalidade existente
- Fácil reverter se necessário

**Mitigação:**

- Usar Python logging (padrão, confiável)
- Testes garantem não quebrar nada
- Logs desabilitados por padrão em testes

---

## Deliverables Esperados

1. `cli/src/timeblock/utils/logger.py` (novo)
2. Logs em 2 services principais
3. 6+ testes de logging
4. `docs/04-specifications/logging-strategy.md`
5. README atualizado

**Próximo:** Sprint 1.4 - Documentação Showcase
