# Estratégia de Logging - TimeBlock Organizer

**Versão:** 1.0

**Data:** 03 de Novembro de 2025

**Status:** IMPLEMENTADO

---

## Visão Geral

Sistema de logging estruturado usando Python logging padrão com:

- Formato estruturado para análise
- Rotação automática de arquivos
- Configuração por nível (DEBUG, INFO, WARNING, ERROR)
- Suporte a console e arquivo

---

## Arquitetura

### Módulo Core

**Localização:** `cli/src/timeblock/utils/logger.py`

**Funções Principais:**

- `setup_logger()` - Configura novo logger
- `get_logger()` - Obtém logger existente
- `disable_logging()` - Silencia logs (testes)
- `enable_logging()` - Reabilita logs

### Formato de Log

```terminal
[timestamp] [level] [module] message
```

**Exemplo:**

```terminal
[2025-11-03 14:30:45] [INFO] [HabitInstanceService] Criadas 7 instâncias para habit_id=1
[2025-11-03 14:30:46] [ERROR] [HabitInstanceService] Hábito não encontrado: habit_id=999
```

---

## Níveis de Log

### DEBUG

**Uso:** Detalhes internos durante desenvolvimento
**Exemplo:** Parâmetros de entrada, estado intermediário

```python
logger.debug(f"Ajustando horário instance_id={id}, new_start={start}")
```

### INFO

**Uso:** Operações normais do sistema
**Exemplo:** Sucesso de operações, quantidades processadas

```python
logger.info(f"Criadas {len(instances)} instâncias para habit_id={id}")
```

### WARNING

**Uso:** Comportamentos inesperados mas não críticos
**Exemplo:** Operação em recurso inexistente (retorna None)

```python
logger.warning(f"Tentativa de completar instância inexistente: instance_id={id}")
```

### ERROR

**Uso:** Erros que impedem operação
**Exemplo:** Validação falhou, recurso não encontrado (levanta exceção)

```python
logger.error(f"Hábito não encontrado: habit_id={id}")
```

---

## Uso nos Services

### HabitInstanceService

**Operações Logadas:**

| Método                   | Nível   | Mensagem                    |
| ------------------------ | ------- | --------------------------- |
| `generate_instances()`   | INFO    | Início, quantidade criada   |
| `generate_instances()`   | ERROR   | Hábito não encontrado       |
| `adjust_instance_time()` | DEBUG   | Parâmetros de ajuste        |
| `adjust_instance_time()` | INFO    | Sucesso do ajuste           |
| `adjust_instance_time()` | WARNING | Horário inválido, conflitos |
| `mark_completed()`       | INFO    | Instância completada        |
| `mark_completed()`       | WARNING | Instância inexistente       |
| `mark_skipped()`         | INFO    | Instância pulada            |
| `mark_skipped()`         | WARNING | Instância inexistente       |

### Exemplo de Uso

```python
from src.timeblock.utils.logger import get_logger

logger = get_logger(__name__)

def my_function(param: int):
    """Função exemplo com logging."""
    logger.debug(f"Iniciando processamento: param={param}")

    try:
        result = process(param)
        logger.info(f"Processamento concluído: result={result}")
        return result
    except ValueError as e:
        logger.error(f"Erro de validação: {e}", exc_info=True)
        raise
```

---

## Configuração

### Desenvolvimento (Console)

```python
from src.timeblock.utils.logger import setup_logger

logger = setup_logger(
    __name__,
    level="DEBUG",
    console=True
)
```

### Produção (Arquivo com Rotação)

```python
from pathlib import Path
from src.timeblock.utils.logger import setup_logger

logger = setup_logger(
    __name__,
    level="INFO",
    log_file=Path("~/.timeblock/logs/timeblock.log"),
    max_bytes=10_000_000,  # 10MB
    backup_count=5,
    console=False
)
```

### Testes (Silenciado)

```python
from src.timeblock.utils.logger import disable_logging

def test_my_function():
    disable_logging()  # Silencia logs durante teste
    result = my_function()
    assert result == expected
```

---

## Rotação de Logs

**Configuração Padrão:**

- Tamanho máximo: 10MB por arquivo
- Backups mantidos: 5 arquivos
- Encoding: UTF-8

**Arquivos Gerados:**

```terminal
timeblock.log       # Atual
timeblock.log.1     # Backup mais recente
timeblock.log.2
timeblock.log.3
timeblock.log.4
timeblock.log.5     # Backup mais antigo
```

**Rotação Automática:**
Quando `timeblock.log` atinge 10MB:

1. `timeblock.log` → `timeblock.log.1`
2. `timeblock.log.1` → `timeblock.log.2`
3. ... (rotação em cascata)
4. `timeblock.log.5` → deletado
5. Novo `timeblock.log` criado

---

## Boas Práticas

### DO

**Logar operações críticas:**

```python
logger.info(f"Criadas {count} instâncias")  # Sucesso
logger.error(f"Falha ao criar instância: {e}")  # Erro
```

**Incluir contexto relevante:**

```python
logger.warning(f"Conflito detectado: instance_id={id}, task_id={task_id}")
```

**Usar níveis apropriados:**

```python
logger.debug("Detalhes para debug")  # Desenvolvimento
logger.info("Operação normal")       # Produção
logger.warning("Algo estranho")      # Atenção
logger.error("Falha crítica")        # Problema
```

### DON'T

**Não logar dados sensíveis:**

```python
# ERRADO
logger.info(f"Login: password={password}")

# CORRETO
logger.info(f"Login: user={username}")
```

**Não logar em loops apertados:**

```python
# ERRADO
for item in large_list:
    logger.debug(f"Processing {item}")  # Milhares de logs

# CORRETO
logger.debug(f"Processing {len(large_list)} items")
# ... processa ...
logger.debug(f"Processed {processed} items")
```

**Não usar print() em código:**

```python
# ERRADO
print(f"Debug: {value}")

# CORRETO
logger.debug(f"value={value}")
```

---

## Monitoramento

### Análise de Logs

**Buscar erros:**

```bash
grep ERROR timeblock.log
```

**Contar operações:**

```bash
grep "Criadas.*instâncias" timeblock.log | wc -l
```

**Ver logs recentes:**

```bash
tail -f timeblock.log
```

### Métricas Úteis

- Total de instâncias criadas (INFO grep)
- Taxa de erros (ERROR count / total operations)
- Operações mais lentas (timestamp diff analysis)
- Conflitos detectados (WARNING grep)

---

## Evolução Futura

### v1.3.0 (Ambientes Formalizados)

**Configuração por Ambiente:**

```python
# Development
LOG_LEVEL = "DEBUG"
LOG_TO_FILE = False

# Production
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_PATH = "~/.timeblock/logs/"
```

### v2.0 (Logging Avançado)

**Recursos Planejados:**

- Logging estruturado (JSON)
- Integração com serviços externos (Sentry, LogStash)
- Métricas e alertas automáticos
- Dashboard de logs

---

## Referências

- Python Logging: <https://docs.python.org/3/library/logging.html>
- Logging Best Practices: <https://docs.python-guide.org/writing/logging/>
- ADR-009: Language Standards (logs em português fase atual)

---

**Última Atualização:** 03 de Novembro de 2025

**Próxima Revisão:** v1.3.0 (ambientes formalizados)
