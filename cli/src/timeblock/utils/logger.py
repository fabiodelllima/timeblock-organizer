"""Sistema de logging estruturado para TimeBlock.

Este módulo fornece logging padronizado com:
- Formato estruturado com timestamp, nível, módulo
- Suporte a console e arquivo
- Rotação automática de logs
- Configuração por nível (DEBUG, INFO, WARNING, ERROR)
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Path | None = None,
    max_bytes: int = 10_000_000,
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """Configura logger com formato estruturado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        level: Nível mínimo - DEBUG, INFO, WARNING, ERROR
        log_file: Caminho do arquivo de log (None = console only)
        max_bytes: Tamanho máximo antes de rotação (padrão: 10MB)
        backup_count: Número de backups mantidos (padrão: 5)
        console: Se True, também loga no console
    
    Returns:
        Logger configurado
    
    Exemplo:
        >>> from timeblock.utils.logger import setup_logger
        >>> logger = setup_logger(__name__)
        >>> logger.info("Operação iniciada")
        >>> logger.error("Erro ao processar", exc_info=True)
    """
    # Cria ou obtém logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove handlers existentes (evita duplicação)
    logger.handlers.clear()

    # Formato estruturado: [timestamp] [level] [module] message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para console (stderr)
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Handler para arquivo com rotação
    if log_file:
        # Garante que diretório existe
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Evita propagação para root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtém logger existente ou cria um novo com configuração padrão.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
    
    Returns:
        Logger configurado
    
    Nota:
        Se logger não existir, cria com nível INFO e console only.
    """
    logger = logging.getLogger(name)

    # Se logger não tem handlers, configura padrão
    if not logger.handlers:
        return setup_logger(name, level="INFO", console=True)

    return logger


def disable_logging():
    """Desabilita todos os logs (útil para testes).
    
    Exemplo:
        >>> from timeblock.utils.logger import disable_logging
        >>> disable_logging()  # Silencia logs durante testes
    """
    logging.disable(logging.CRITICAL)


def enable_logging():
    """Reabilita logs após disable_logging()."""
    logging.disable(logging.NOTSET)
