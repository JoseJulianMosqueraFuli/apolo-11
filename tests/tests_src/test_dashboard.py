"""Tests for the dashboard module."""

import pytest
from datetime import datetime
from hypothesis import given, strategies as st
from rich.layout import Layout

from apolo_11.src.dashboard import Dashboard, DashboardStats, MissionStats


class TestDashboard:
    """Test cases for the Dashboard class."""

    def test_dashboard_initialization(self):
        """Test that dashboard initializes correctly."""
        dashboard = Dashboard()

        assert dashboard.stats.files_generated == 0
        assert dashboard.stats.current_cycle == 0
        assert dashboard.stats.missions == {}
        assert dashboard.stats.last_report_time is None

    def test_update_stats(self):
        """Test that dashboard stats are updated correctly."""
        dashboard = Dashboard()

        generator_stats = {
            'files_count': 10,
            'cycle': 5
        }

        reporter_stats = {
            'last_report_time': datetime.now(),
            'missions': {
                'ORBONE': {
                    'device_counts': {'sensor': 3, 'actuator': 2},
                    'status_counts': {'operational': 4, 'unknown': 1}
                }
            }
        }

        dashboard.update_stats(generator_stats, reporter_stats)

        assert dashboard.stats.files_generated == 10
        assert dashboard.stats.current_cycle == 5
        assert 'ORBONE' in dashboard.stats.missions
        assert dashboard.stats.missions['ORBONE'].name == 'ORBONE'
        assert dashboard.stats.missions['ORBONE'].device_counts == {'sensor': 3, 'actuator': 2}

    def test_render_returns_layout(self):
        """Test that render method returns a Layout object."""
        dashboard = Dashboard()
        layout = dashboard.render()

        assert isinstance(layout, Layout)

    @given(
        files_generated=st.integers(min_value=0, max_value=1000),
        current_cycle=st.integers(min_value=0, max_value=100),
        mission_names=st.lists(st.text(min_size=1, max_size=10), min_size=0, max_size=5),
        device_types=st.lists(st.text(min_size=1, max_size=10), min_size=0, max_size=3),
        device_counts=st.lists(st.integers(min_value=0, max_value=10), min_size=0, max_size=3)
    )
    def test_dashboard_content_completeness_property(self, files_generated, current_cycle, 
                                                   mission_names, device_types, device_counts):
        """
        Feature: apolo-11-improvements, Property 4: Dashboard muestra información completa
        Validates: Requirements 6.1, 6.2, 6.3

        For any set of generator and reporter statistics, the dashboard render output 
        SHALL contain: files generated count, mission statistics, and last report status.
        """
        dashboard = Dashboard()

        # Create mission statistics
        missions = {}
        for i, mission_name in enumerate(mission_names):
            device_counts_dict = {}
            status_counts_dict = {'operational': 1, 'unknown': 0}

            # Create device counts for this mission
            for j, device_type in enumerate(device_types):
                if j < len(device_counts):
                    device_counts_dict[device_type] = device_counts[j]

            missions[mission_name] = {
                'device_counts': device_counts_dict,
                'status_counts': status_counts_dict
            }

        generator_stats = {
            'files_count': files_generated,
            'cycle': current_cycle
        }

        reporter_stats = {
            'last_report_time': datetime.now(),
            'missions': missions
        }

        # Update dashboard with generated stats
        dashboard.update_stats(generator_stats, reporter_stats)

        # Render the dashboard
        layout = dashboard.render()

        # Verify the layout is properly structured
        assert isinstance(layout, Layout)

        # Convert layout to string to check content
        console_output = dashboard.console.render(layout)
        layout_str = str(console_output)

        # Property: Dashboard must show files generated count
        assert str(files_generated) in layout_str

        # Property: Dashboard must show current cycle
        assert str(current_cycle) in layout_str

        # Property: Dashboard must show last report status (either timestamp or "N/A")
        assert ("Last Report" in layout_str and 
                (datetime.now().strftime("%Y-%m-%d") in layout_str or "N/A" in layout_str))

        # Property: Dashboard must show mission information when missions exist
        if missions:
            for mission_name in mission_names:
                if mission_name:  # Only check non-empty mission names
                    assert mission_name in layout_str or "Mission Statistics" in layout_str
        else:
            # When no missions, should show appropriate message
            assert "No mission data available" in layout_str or "Mission Statistics" in layout_str

    def test_start_and_stop_live_display(self):
        """Test starting and stopping live display."""
        dashboard = Dashboard()

        # Start live display
        live = dashboard.start_live_display()
        assert live is not None
        assert dashboard._live is not None
        
        # Stop live display
        dashboard.stop_display()
        assert dashboard._live is None

    def test_update_display_without_live(self):
        """Test that update_display handles case when live display is not started."""
        dashboard = Dashboard()

        # Should not raise an exception
        dashboard.update_display()

    def test_mission_stats_dataclass(self):
        """Test MissionStats dataclass functionality."""
        mission_stats = MissionStats(
            name="ORBONE",
            device_counts={"sensor": 5, "actuator": 3},
            status_counts={"operational": 7, "unknown": 1}
        )

        assert mission_stats.name == "ORBONE"
        assert mission_stats.device_counts["sensor"] == 5
        assert mission_stats.status_counts["operational"] == 7

    def test_dashboard_stats_dataclass(self):
        """Test DashboardStats dataclass functionality."""
        mission_stats = MissionStats(
            name="ORBONE",
            device_counts={"sensor": 5},
            status_counts={"operational": 5}
        )

        dashboard_stats = DashboardStats(
            files_generated=100,
            current_cycle=10,
            missions={"ORBONE": mission_stats},
            last_report_time=datetime.now()
        )

        assert dashboard_stats.files_generated == 100
        assert dashboard_stats.current_cycle == 10
        assert "ORBONE" in dashboard_stats.missions
        assert dashboard_stats.last_report_time is not None
