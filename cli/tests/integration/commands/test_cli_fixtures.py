"""
Integration tests - Validação de fixtures de CLI.

Valida que fixtures essenciais estão configuradas corretamente
e funcionam como esperado nos testes de integração.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from typer.testing import CliRunner


class TestBRTestInfrastructure:
    """
    Integration: Validação de infraestrutura de testes (BR-TEST-INFRA-*).
    
    Valida que fixtures essenciais estão disponíveis e funcionais
    para execução de testes de integração.
    
    BRs cobertas:
    - BR-TEST-INFRA-001: CLI runner disponível e funcional
    """

    def test_br_test_infra_001_cli_runner_available(
        self, cli_runner: CliRunner
    ) -> None:
        """
        Integration: Fixture cli_runner está disponível e funcional.
        
        DADO: Fixture cli_runner injetada no teste
        QUANDO: Teste executa
        ENTÃO: Fixture não é None
        E: Fixture possui método invoke para executar comandos CLI
        
        Referências:
            - BR-TEST-INFRA-001: CLI runner disponível
        
        Nota:
            Este teste valida a configuração básica de infraestrutura
            necessária para todos os outros testes de integração CLI.
        """
        # ASSERT
        assert cli_runner is not None, "CLI runner deve estar disponível"
        assert hasattr(
            cli_runner, "invoke"
        ), "CLI runner deve ter método invoke"
