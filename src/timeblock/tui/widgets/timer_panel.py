"""TimerPanel - Card compacto do timer com ASCII art (BR-TUI-003, BR-TUI-021).

BR-TUI-021: Keybindings de timer no dashboard.
BR-TUI-003-R25: Timer card compacto (sem ASCII art no dashboard v2).
BR-TUI-003-R27: Cores por estado (Mauve running, Yellow paused, Overlay0 idle).
"""

from typing import Any

from textual.events import Key
from textual.message import Message
from textual.widgets import Static

from timeblock.tui.colors import C_ACCENT, C_MUTED, C_WARNING
from timeblock.tui.formatters import render_ascii_time


class TimerPanel(Static):
    can_focus = True
    """Card do timer com elapsed em ASCII art grande."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._timer_info: dict | None = None

    # =========================================================================
    # Messages (BR-TUI-021)
    # =========================================================================

    class TimerPauseRequest(Message):
        """Solicita pausa do timer ao coordinator."""

        def __init__(self, timer_id: int) -> None:
            self.timer_id = timer_id
            super().__init__()

    class TimerResumeRequest(Message):
        """Solicita retomada do timer ao coordinator."""

        def __init__(self, timer_id: int) -> None:
            self.timer_id = timer_id
            super().__init__()

    class TimerStopRequest(Message):
        """Solicita parada do timer ao coordinator."""

        def __init__(self, timer_id: int) -> None:
            self.timer_id = timer_id
            super().__init__()

    class TimerCancelRequest(Message):
        """Solicita cancelamento do timer ao coordinator."""

        def __init__(self, timer_id: int) -> None:
            self.timer_id = timer_id
            super().__init__()

    # =========================================================================
    # Key Dispatch (BR-TUI-021, ADR-035)
    # =========================================================================

    def on_key(self, event: Key) -> None:
        """Captura keybindings do timer (ADR-035)."""
        if not self._timer_info:
            return
        timer_id = self._timer_info.get("id")
        if not timer_id:
            return
        if event.key == "space":
            st = self._timer_info.get("status", "")
            if st == "running":
                self.post_message(self.TimerPauseRequest(timer_id))
            elif st == "paused":
                self.post_message(self.TimerResumeRequest(timer_id))
            event.stop()
        elif event.key == "s":
            self.post_message(self.TimerStopRequest(timer_id))
            event.stop()
        elif event.key == "c":
            self.post_message(self.TimerCancelRequest(timer_id))
            event.stop()

    def update_data(self, timer_info: dict | None) -> None:
        """Recebe info do timer do coordinator e renderiza."""
        self._timer_info = timer_info
        self._refresh_content()

    def _refresh_content(self) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        if self._timer_info:
            lines = self._build_active_lines()
        else:
            lines = self._build_idle_lines()
        self.update("\n".join(lines))

    def _build_active_lines(self) -> list[str]:
        """Monta linhas para timer ativo (running ou paused).

        Princípio do projeto: nenhum panel exibe hints de teclado inline.
        Hints vivem exclusivamente no footer global (status_bar). Issue #29.
        """
        assert self._timer_info is not None
        info = self._timer_info
        elapsed = info.get("elapsed", "00:00")
        name = info.get("name", "")
        st = info.get("status", "running")

        if st == "paused":
            color = C_WARNING
            icon = "⏸"
            label = "pausado"
            self.border_title = "Timer"
            self.border_subtitle = "⏸ paused"
        else:
            color = C_ACCENT
            icon = "▶"
            label = "em andamento"
            self.border_title = "Timer"
            self.border_subtitle = "▶ ativo"

        art = render_ascii_time(elapsed)
        lines = [""]
        for row in art:
            lines.append(f"    [bold {color}]{row}[/bold {color}]")
        lines.append("")
        lines.append(f"    [{color}]{icon} {label}[/{color}] · {name}")
        return lines

    def _build_idle_lines(self) -> list[str]:
        """Monta linhas para timer idle."""
        self.border_title = "Timer"
        self.border_subtitle = "idle"
        art = render_ascii_time("00:00")
        lines = [""]
        for row in art:
            lines.append(f"    [{C_MUTED}]{row}[/{C_MUTED}]")
        lines.append("")
        lines.append(f"    [{C_MUTED}]⏹ idle[/{C_MUTED}]")
        return lines
