"""Dashboard module for Apollo 11 system monitoring."""

import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MissionStats:
    """Statistics for a specific mission."""
    name: str
    device_counts: Dict[str, int]  # device_type -> count
    status_counts: Dict[str, int]  # status -> count


@dataclass
class DashboardStats:
    """Complete dashboard statistics."""
    files_generated: int
    current_cycle: int
    missions: Dict[str, MissionStats]
    last_report_time: Optional[datetime]


class Dashboard:
    """Terminal User Interface dashboard for Apollo 11 system monitoring."""
    def __init__(self):
        """Initialize the dashboard."""
        self.console = Console()
        self.stats = DashboardStats(
            files_generated=0,
            current_cycle=0,
            missions={},
            last_report_time=None
        )
        self._live = None

    def update_stats(self, generator_stats: Dict[str, Any], reporter_stats: Dict[str, Any]) -> None:
        """Update dashboard statistics.

        Args:
            generator_stats: Statistics from the generator component
            reporter_stats: Statistics from the reporter component
        """
        self.stats.files_generated = generator_stats.get('files_count', 0)
        self.stats.current_cycle = generator_stats.get('cycle', 0)
        self.stats.last_report_time = reporter_stats.get('last_report_time')

        # Update mission statistics
        missions_data = reporter_stats.get('missions', {})
        self.stats.missions = {}

        for mission_name, mission_data in missions_data.items():
            self.stats.missions[mission_name] = MissionStats(
                name=mission_name,
                device_counts=mission_data.get('device_counts', {}),
                status_counts=mission_data.get('status_counts', {})
            )

    def render(self) -> Layout:
        """Render the dashboard layout.

        Returns:
            Layout: The complete dashboard layout
        """
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        # Header
        header_text = Text("Apollo 11 Mission Control Dashboard", style="bold blue")
        layout["header"].update(Panel(Align.center(header_text), style="blue"))

        # Body - split into left and right sections
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        # Left side - System Status
        layout["left"].update(self._render_system_status())
        # Right side - Mission Statistics
        layout["right"].update(self._render_mission_stats())

        # Footer
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Last Updated: {current_time} | Press Ctrl+C to exit"
        layout["footer"].update(Panel(Align.center(footer_text), style="green"))

        return layout

    def _render_system_status(self) -> Panel:
        """Render the system status panel."""
        table = Table(title="System Status", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Files Generated", str(self.stats.files_generated))
        table.add_row("Current Cycle", str(self.stats.current_cycle))

        if self.stats.last_report_time:
            last_report = self.stats.last_report_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_report = "N/A"
        table.add_row("Last Report", last_report)

        return Panel(table, title="System Overview", border_style="blue")

    def _render_mission_stats(self) -> Panel:
        """Render the mission statistics panel."""
        if not self.stats.missions:
            empty_text = Text("No mission data available", style="italic yellow")
            return Panel(Align.center(empty_text), title="Mission Statistics", border_style="red")

        table = Table(title="Mission Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Mission", style="cyan", no_wrap=True)
        table.add_column("Device Types", style="white")
        table.add_column("Total Devices", style="green")
        table.add_column("Status Summary", style="yellow")

        for mission_name, mission_stats in self.stats.missions.items():
            device_types = ", ".join(mission_stats.device_counts.keys()) if mission_stats.device_counts else "None"
            total_devices = sum(mission_stats.device_counts.values()) if mission_stats.device_counts else 0

            # Create status summary
            status_summary = []
            for status, count in mission_stats.status_counts.items():
                status_summary.append(f"{status}: {count}")
            status_text = ", ".join(status_summary) if status_summary else "No status data"

            table.add_row(
                mission_name,
                device_types,
                str(total_devices),
                status_text
            )

        return Panel(table, title="Mission Overview", border_style="green")

    def start_live_display(self) -> Live:
        """Start the live display.

        Returns:
            Live: The live display object
        """
        self._live = Live(self.render(), console=self.console, refresh_per_second=1)
        return self._live

    def update_display(self) -> None:
        """Update the live display with current data."""
        if self._live:
            self._live.update(self.render())

    def stop_display(self) -> None:
        """Stop the live display."""
        if self._live:
            self._live.stop()
            self._live = None
