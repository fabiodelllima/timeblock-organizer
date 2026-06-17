"""Testes das keybindings de timer no dashboard (BR-TUI-021, ADR-035).

Valida que HabitsPanel e TimerPanel emitem mensagens corretas
conforme estado do timer e keybinding pressionado.
"""

import pytest
from textual.app import App, ComposeResult

from timeblock.tui.screens.dashboard.screen import DashboardScreen
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.timer_panel import TimerPanel


class TimerTestApp(App):
    """App de teste para keybindings de timer."""

    def compose(self) -> ComposeResult:
        yield DashboardScreen(id="dashboard-view")


async def _wait_until(pilot, predicate, max_cycles: int = 20) -> None:
    """Avança o message pump até predicate() ser verdadeiro ou esgotar max_cycles.

    Um único ``pilot.pause()`` após um press cede apenas um ciclo do message
    pump, insuficiente para despachar a mensagem postada antes do assert sob a
    carga do runner do CI (BR-TUI-021, issue #67). Aguardar até o estado
    capturado ser observado — ou até um teto de ciclos — torna o teste
    determinístico: o caso positivo retorna assim que a mensagem chega, e o
    negativo esgota o teto com a lista ainda vazia, seguindo capaz de pegar uma
    mensagem inesperada.
    """
    for _ in range(max_cycles):
        await pilot.pause()
        if predicate():
            return


class TestBRTUI021HabitsTimerStart:
    """BR-TUI-021: Shift+Enter em hábito pendente emite TimerStartRequest."""

    @pytest.mark.asyncio
    async def test_br_tui_021_shift_enter_emits_timer_start(self):
        """Shift+Enter com hábito pendente selecionado posta TimerStartRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_habits_panel_timer_start_request(
                self, message: HabitsPanel.TimerStartRequest
            ) -> None:
                received.append(message.instance_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel._instances = [{"id": 10, "name": "Teste", "status": "pending"}]
            panel._showing_placeholders = False
            panel._set_item_count(1)
            app.set_focus(panel)
            await pilot.press("t")
            await _wait_until(pilot, lambda: received)
        assert received == [10]

    @pytest.mark.asyncio
    async def test_br_tui_021_shift_enter_no_item_no_message(self):
        """Shift+Enter sem item selecionado não posta mensagem."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_habits_panel_timer_start_request(
                self, message: HabitsPanel.TimerStartRequest
            ) -> None:
                received.append(message.instance_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel._instances = []
            panel._set_item_count(0)
            app.set_focus(panel)
            await pilot.press("t")
            await _wait_until(pilot, lambda: received)
        assert received == []


class TestBRTUI021StopAndDone:
    """BR-TUI-021: Ctrl+Enter em hábito running emite TimerStopAndDoneRequest."""

    @pytest.mark.asyncio
    async def test_br_tui_021_ctrl_enter_running_emits_stop_and_done(self):
        """Ctrl+Enter em hábito running posta TimerStopAndDoneRequest."""
        received_stop_done: list = []
        received_done: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_habits_panel_timer_stop_and_done_request(
                self, message: HabitsPanel.TimerStopAndDoneRequest
            ) -> None:
                received_stop_done.append(message.instance_id)

            def on_habits_panel_habit_done_request(
                self, message: HabitsPanel.HabitDoneRequest
            ) -> None:
                received_done.append(message.instance_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel._instances = [{"id": 20, "name": "Running", "status": "running"}]
            panel._showing_placeholders = False
            panel._set_item_count(1)
            app.set_focus(panel)
            await pilot.press("v")
            await _wait_until(pilot, lambda: received_stop_done)
        assert received_stop_done == [20]
        assert received_done == []

    @pytest.mark.asyncio
    async def test_br_tui_021_ctrl_enter_pending_emits_done(self):
        """Ctrl+Enter em hábito pendente posta HabitDoneRequest (preserva comportamento)."""
        received_stop_done: list = []
        received_done: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_habits_panel_timer_stop_and_done_request(
                self, message: HabitsPanel.TimerStopAndDoneRequest
            ) -> None:
                received_stop_done.append(message.instance_id)

            def on_habits_panel_habit_done_request(
                self, message: HabitsPanel.HabitDoneRequest
            ) -> None:
                received_done.append(message.instance_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel._instances = [{"id": 30, "name": "Pending", "status": "pending"}]
            panel._showing_placeholders = False
            panel._set_item_count(1)
            app.set_focus(panel)
            await pilot.press("v")
            await _wait_until(pilot, lambda: received_done)
        assert received_done == [30]
        assert received_stop_done == []


class TestBRTUI021TimerPanelKeys:
    """BR-TUI-021: TimerPanel emite mensagens corretas por keybinding."""

    @pytest.mark.asyncio
    async def test_br_tui_021_shift_enter_running_emits_pause(self):
        """Shift+Enter em timer running posta TimerPauseRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_timer_panel_timer_pause_request(
                self, message: TimerPanel.TimerPauseRequest
            ) -> None:
                received.append(message.timer_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TimerPanel)
            panel.update_data({"id": 5, "status": "running", "elapsed": "01:30", "name": "T"})
            app.set_focus(panel)
            await pilot.press("space")
            await _wait_until(pilot, lambda: received)
        assert received == [5]

    @pytest.mark.asyncio
    async def test_br_tui_021_shift_enter_paused_emits_resume(self):
        """Shift+Enter em timer paused posta TimerResumeRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_timer_panel_timer_resume_request(
                self, message: TimerPanel.TimerResumeRequest
            ) -> None:
                received.append(message.timer_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TimerPanel)
            panel.update_data({"id": 6, "status": "paused", "elapsed": "02:00", "name": "T"})
            app.set_focus(panel)
            await pilot.press("space")
            await _wait_until(pilot, lambda: received)
        assert received == [6]

    @pytest.mark.asyncio
    async def test_br_tui_021_ctrl_enter_emits_stop(self):
        """Ctrl+Enter em timer ativo posta TimerStopRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_timer_panel_timer_stop_request(
                self, message: TimerPanel.TimerStopRequest
            ) -> None:
                received.append(message.timer_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TimerPanel)
            panel.update_data({"id": 7, "status": "running", "elapsed": "05:00", "name": "T"})
            app.set_focus(panel)
            await pilot.press("s")
            await _wait_until(pilot, lambda: received)
        assert received == [7]

    @pytest.mark.asyncio
    async def test_br_tui_021_ctrl_x_emits_cancel(self):
        """Ctrl+X em timer ativo posta TimerCancelRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_timer_panel_timer_cancel_request(
                self, message: TimerPanel.TimerCancelRequest
            ) -> None:
                received.append(message.timer_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TimerPanel)
            panel.update_data({"id": 8, "status": "running", "elapsed": "03:00", "name": "T"})
            app.set_focus(panel)
            await pilot.press("c")
            await _wait_until(pilot, lambda: received)
        assert received == [8]

    @pytest.mark.asyncio
    async def test_br_tui_021_no_timer_no_message(self):
        """Keybindings sem timer ativo não emitem mensagens."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_timer_panel_timer_pause_request(self, message) -> None:
                received.append("pause")

            def on_timer_panel_timer_stop_request(self, message) -> None:
                received.append("stop")

            def on_timer_panel_timer_cancel_request(self, message) -> None:
                received.append("cancel")

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TimerPanel)
            panel.update_data(None)
            app.set_focus(panel)
            await pilot.press("space")
            await pilot.press("s")
            await pilot.press("c")
            await _wait_until(pilot, lambda: received)
        assert received == []
