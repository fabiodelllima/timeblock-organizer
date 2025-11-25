"""Testes para módulo de logging."""

import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.timeblock.utils.logger import disable_logging, enable_logging, get_logger, setup_logger


class TestSetupLogger:
    """Testa configuração de loggers."""

    def test_setup_logger_console_only(self):
        """Configura logger apenas para console.

        DADO: Sem arquivo de log especificado
        QUANDO: Configurar logger
        ENTÃO: Deve ter handler de console apenas
        """
        # Ação: Configura logger console only
        logger = setup_logger("test.console", level="INFO")

        # Verificação: Tem exatamente 1 handler (console)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert logger.level == logging.INFO

    def test_setup_logger_with_file(self):
        """Configura logger com arquivo de log.

        DADO: Arquivo de log especificado
        QUANDO: Configurar logger
        ENTÃO: Deve ter handlers de console e arquivo
        """
        # Preparação: Cria arquivo temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Ação: Configura logger com arquivo
            logger = setup_logger("test.file", level="DEBUG", log_file=log_file)

            # Verificação: Tem 2 handlers (console + arquivo)
            assert len(logger.handlers) == 2
            assert logger.level == logging.DEBUG

            # Verificação: Arquivo foi criado
            assert log_file.exists()

    def test_setup_logger_without_console(self):
        """Configura logger sem console (apenas arquivo).

        DADO: console=False e arquivo especificado
        QUANDO: Configurar logger
        ENTÃO: Deve ter apenas handler de arquivo (RotatingFileHandler)
        """
        # Preparação: Cria arquivo temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Ação: Configura logger sem console
            logger = setup_logger("test.nocons", level="INFO", log_file=log_file, console=False)

            # Verificação: Apenas 1 handler
            assert len(logger.handlers) == 1

            # Verificação: É especificamente RotatingFileHandler
            assert isinstance(logger.handlers[0], RotatingFileHandler)

    def test_log_levels(self):
        """Testa diferentes níveis de log.

        DADO: Logger configurado em diferentes níveis
        QUANDO: Logar mensagens
        ENTÃO: Apenas mensagens acima do nível devem passar
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Preparação: Logger em WARNING
            logger = setup_logger("test.levels", level="WARNING", log_file=log_file, console=False)

            # Ação: Loga em diferentes níveis
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            # Verificação: Arquivo contém apenas WARNING e ERROR
            content = log_file.read_text()
            assert "Debug message" not in content
            assert "Info message" not in content
            assert "Warning message" in content
            assert "Error message" in content

    def test_log_rotation(self):
        """Testa rotação de logs quando arquivo atinge tamanho máximo.

        DADO: Logger com max_bytes=100
        QUANDO: Escrever mais de 100 bytes
        ENTÃO: Deve criar arquivo de backup

        Regra de Negócio: Rotação automática previne arquivos gigantes.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Preparação: Logger com limite pequeno
            logger = setup_logger(
                "test.rotation",
                level="INFO",
                log_file=log_file,
                max_bytes=100,  # Muito pequeno para forçar rotação
                backup_count=2,
                console=False,
            )

            # Ação: Escreve muitas mensagens
            for i in range(50):
                logger.info(f"Mensagem de teste número {i} com texto extra")

            # Verificação: Arquivos de backup criados
            backup_files = list(Path(tmpdir).glob("test.log.*"))
            assert len(backup_files) > 0, "Backup files devem ser criados"


class TestGetLogger:
    """Testa obtenção de loggers existentes."""

    def test_get_logger_new(self):
        """Obtém logger novo (cria com padrão).

        DADO: Logger não existe
        QUANDO: Chamar get_logger
        ENTÃO: Deve criar com configuração padrão
        """
        # Ação: Obtém logger inexistente
        logger = get_logger("test.new.logger")

        # Verificação: Logger criado com padrão
        assert logger is not None
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_get_logger_existing(self):
        """Obtém logger existente.

        DADO: Logger já configurado
        QUANDO: Chamar get_logger novamente
        ENTÃO: Deve retornar mesmo logger
        """
        # Preparação: Cria logger
        logger1 = setup_logger("test.existing", level="DEBUG")

        # Ação: Obtém logger existente
        logger2 = get_logger("test.existing")

        # Verificação: Mesmo logger
        assert logger1 is logger2
        assert logger2.level == logging.DEBUG


class TestDisableEnableLogging:
    """Testa desabilitar/habilitar logs globalmente."""

    def test_disable_logging(self):
        """Desabilita todos os logs.

        DADO: Logging habilitado
        QUANDO: Chamar disable_logging
        ENTÃO: Nenhuma mensagem deve ser logada

        Caso de Uso: Silenciar logs durante testes.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Preparação: Logger normal
            logger = setup_logger("test.disable", level="INFO", log_file=log_file, console=False)

            # Ação: Desabilita logging
            disable_logging()
            logger.info("Esta mensagem NÃO deve aparecer")
            logger.error("Esta mensagem também NÃO deve aparecer")

            # Verificação: Arquivo vazio ou inexistente
            if log_file.exists():
                content = log_file.read_text()
                assert len(content) == 0 or content.strip() == ""

            # Limpeza: Reabilita para outros testes
            enable_logging()

    def test_enable_logging(self):
        """Reabilita logs após desabilitar.

        DADO: Logging desabilitado
        QUANDO: Chamar enable_logging
        ENTÃO: Logs devem voltar a funcionar
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Preparação: Logger normal
            logger = setup_logger("test.enable", level="INFO", log_file=log_file, console=False)

            # Ação: Desabilita e reabilita
            disable_logging()
            logger.info("Mensagem durante desabilitado")
            enable_logging()
            logger.info("Mensagem após reabilitar")

            # Verificação: Apenas segunda mensagem aparece
            content = log_file.read_text()
            assert "durante desabilitado" not in content
            assert "após reabilitar" in content


class TestLogFormat:
    """Testa formato das mensagens de log."""

    def test_log_format_structure(self):
        """Verifica estrutura do formato de log.

        DADO: Logger configurado
        QUANDO: Logar mensagem
        ENTÃO: Formato deve ser [timestamp] [level] [module] message
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            # Preparação: Logger
            logger = setup_logger("test.format", level="INFO", log_file=log_file, console=False)

            # Ação: Loga mensagem
            logger.info("Mensagem de teste")

            # Verificação: Formato correto
            content = log_file.read_text()
            assert "[INFO]" in content
            assert "[test.format]" in content
            assert "Mensagem de teste" in content

            # Verifica presença de timestamp (formato: [YYYY-MM-DD HH:MM:SS])
            import re

            timestamp_pattern = r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]"
            assert re.search(timestamp_pattern, content), "Timestamp deve estar presente"
