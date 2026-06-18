"""Configuração de testes de snapshot e2e.

Fixture snap_compare customizada usando syrupy 5.x + a API pilot do Textual,
substituindo a dependência legada pytest-textual-snapshot.

A fixture preserva a mesma interface usada por todos os testes existentes:
    assert snap_compare(app, terminal_size=(...), run_before=callback)
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import pytest
from freezegun import freeze_time
from syrupy.extensions.single_file import SingleFileSnapshotExtension

if TYPE_CHECKING:
    from collections.abc import Callable

    from syrupy.assertion import SnapshotAssertion
    from syrupy.types import SerializableData, SerializedData
    from textual.app import App


SNAPSHOT_FROZEN_DATETIME = "2025-06-16 09:00:00"


@pytest.fixture(autouse=True)
def _freeze_snapshot_clock(request: pytest.FixtureRequest):
    """Congela o relógio nos testes de snapshot para render determinístico (#66).

    Restrito aos módulos de snapshot: as fontes de "agora" do dashboard
    (cabeçalho, loader, agenda, elapsed do timer) passam por
    date.today()/datetime.now(), e o congelamento remove a variação diária.
    Usa tick=True para o relógio avançar em tempo real a partir da data fixa:
    sem isso o freezegun congela time.monotonic() e os timers do asyncio nunca
    disparam, travando o pilot.pause() dos testes que abrem modais. Com tick,
    data e minuto seguem fixos (o teste roda em milissegundos) e o elapsed do
    timer trunca para o valor esperado. Demais testes e2e (com
    freeze próprio ou dependentes de now real) ficam intactos. Ver ADR-059.
    """
    if "snapshot" not in request.module.__name__:
        yield
        return
    with freeze_time(SNAPSHOT_FROZEN_DATETIME, tick=True):
        yield


class SVGSnapshotExtension(SingleFileSnapshotExtension):
    """Extensão do syrupy que armazena snapshots como arquivos .svg individuais.

    Sobrescreve serialize para aceitar str do export_screenshot() do Textual,
    já que SingleFileSnapshotExtension espera bytes por padrão.
    """

    _file_extension = "svg"

    def serialize(
        self,
        data: SerializableData,
        *,
        exclude: Any = None,
        include: Any = None,
        matcher: Any = None,
    ) -> SerializedData:
        """Codifica a string SVG em bytes para armazenamento em arquivo único."""
        if isinstance(data, str):
            return data.encode("utf-8")
        return super().serialize(data, exclude=exclude, include=include, matcher=matcher)


@pytest.fixture(autouse=True)
def _allow_color_for_snapshots(monkeypatch: pytest.MonkeyPatch) -> None:
    """Permite cor na renderização do Textual para os snapshots e2e.

    O conftest raiz força NO_COLOR para tornar a saída de CLI determinística,
    mas os snapshots e2e capturam a UI colorida do Textual. Remover NO_COLOR
    por teste garante que export_screenshot preserve as cores do snapshot.
    """
    monkeypatch.delenv("NO_COLOR", raising=False)


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Configura o syrupy para usar snapshots SVG em arquivo único."""
    return snapshot.use_extension(SVGSnapshotExtension)


@pytest.fixture
def snap_compare(snapshot: SnapshotAssertion):
    """Substituto direto do snap_compare do pytest-textual-snapshot.

    Usa App.run_test() + export_screenshot() do Textual com o syrupy
    para a comparação de snapshot. Mantém a mesma assinatura de chamada.
    """

    def _compare(
        app: App,
        *,
        terminal_size: tuple[int, int] = (80, 24),
        run_before: Callable | None = None,
    ) -> bool:
        async def _capture() -> str:
            async with app.run_test(size=terminal_size) as pilot:
                if run_before is not None:
                    await run_before(pilot)
                return app.export_screenshot()

        svg = asyncio.run(_capture())
        assert svg == snapshot
        return True

    return _compare
