from datetime import datetime
from unittest.mock import patch

import pytest
from apolo_11.src.web_dashboard import WebDashboard


@pytest.fixture
def web_dashboard():
    return WebDashboard(host="127.0.0.1", port=0)


class TestWebDashboardInit:
    def test_initial_stats_defaults(self, web_dashboard):
        assert web_dashboard.stats.files_generated == 0
        assert web_dashboard.stats.current_cycle == 0
        assert web_dashboard.stats.missions == {}
        assert web_dashboard.stats.last_report_time is None

    def test_app_created(self, web_dashboard):
        assert web_dashboard.app.title == "Apollo 11 Dashboard"


class TestUpdateStats:
    def test_updates_stats(self, web_dashboard):
        gen_stats = {'files_count': 42, 'cycle': 5}
        rep_stats = {
            'missions': {
                'OrbitOne': {
                    'device_counts': {'Rover': 3, 'Satellite': 2},
                    'status_counts': {'good': 4, 'excellent': 1}
                }
            },
            'last_report_time': datetime(2026, 5, 14, 12, 0, 0)
        }
        web_dashboard.update_stats(gen_stats, rep_stats)
        assert web_dashboard.stats.files_generated == 42
        assert web_dashboard.stats.current_cycle == 5
        assert web_dashboard.stats.last_report_time == datetime(2026, 5, 14, 12, 0, 0)
        assert 'OrbitOne' in web_dashboard.stats.missions
        assert web_dashboard.stats.missions['OrbitOne'].device_counts == {'Rover': 3, 'Satellite': 2}

    def test_update_display_is_noop(self, web_dashboard):
        web_dashboard.update_display()

    def test_missing_keys(self, web_dashboard):
        web_dashboard.update_stats({}, {})
        assert web_dashboard.stats.files_generated == 0
        assert web_dashboard.stats.missions == {}


class TestStatsToDict:
    def test_empty_stats(self, web_dashboard):
        result = web_dashboard._stats_to_dict()
        assert result['files_generated'] == 0
        assert result['missions'] == {}

    def test_with_data(self, web_dashboard):
        gen_stats = {'files_count': 10, 'cycle': 3}
        rep_stats = {
            'missions': {
                'VacMars': {
                    'device_counts': {'Rover': 1},
                    'status_counts': {'faulty': 1}
                }
            },
            'last_report_time': None
        }
        web_dashboard.update_stats(gen_stats, rep_stats)
        result = web_dashboard._stats_to_dict()
        assert result['files_generated'] == 10
        assert result['current_cycle'] == 3
        assert result['last_report_time'] is None
        assert 'VacMars' in result['missions']


class TestRenderHtml:
    def test_renders_empty(self, web_dashboard):
        html = web_dashboard._render_html()
        assert "Apollo 11" in html
        assert "0" in html
        assert "Waiting for first report cycle" in html

    def test_renders_with_data(self, web_dashboard):
        gen_stats = {'files_count': 10, 'cycle': 3}
        rep_stats = {
            'missions': {
                'OrbitOne': {
                    'device_counts': {'Rover': 2, 'Satellite': 1},
                    'status_counts': {'good': 2, 'excellent': 1}
                }
            },
            'last_report_time': datetime(2026, 5, 14, 12, 0, 0)
        }
        web_dashboard.update_stats(gen_stats, rep_stats)
        html = web_dashboard._render_html()
        assert "Apollo 11" in html
        assert "OrbitOne" in html
        assert "10" in html
        assert "good: 2" in html


class TestLifecycle:
    @patch('uvicorn.Server.run')
    def test_start_stop(self, mock_run):
        wd = WebDashboard(host="127.0.0.1", port=0)
        wd.start()
        assert wd._server is not None
        wd.stop()

    def test_stop_without_start(self, web_dashboard):
        web_dashboard.stop()


class TestPrometheusMetrics:
    def test_metrics_empty(self, web_dashboard):
        output = web_dashboard._render_prometheus_metrics()
        assert "apolo_files_generated_total 0" in output
        assert "apolo_current_cycle 0" in output
        assert "apolo_missions_total 0" in output

    def test_metrics_with_data(self, web_dashboard):
        gen_stats = {'files_count': 50, 'cycle': 7}
        rep_stats = {
            'missions': {
                'Mars One': {
                    'device_counts': {'Rover': 3},
                    'status_counts': {'good': 2, 'excellent': 1}
                }
            },
            'last_report_time': datetime(2026, 5, 14, 12, 0, 0)
        }
        web_dashboard.update_stats(gen_stats, rep_stats)
        output = web_dashboard._render_prometheus_metrics()
        assert "apolo_files_generated_total 50" in output
        assert "apolo_current_cycle 7" in output
        assert 'apolo_missions_total 1' in output
        assert 'apolo_device_status_count{mission="mars_one",status="good"} 2' in output
        assert 'apolo_device_type_count{mission="mars_one",type="rover"} 3' in output

    def test_metrics_multiple_missions(self, web_dashboard):
        gen_stats = {'files_count': 100, 'cycle': 10}
        rep_stats = {
            'missions': {
                'Alpha': {
                    'device_counts': {'Sensor': 5},
                    'status_counts': {'warning': 3, 'faulty': 2}
                },
                'Beta': {
                    'device_counts': {'Camera': 2},
                    'status_counts': {'excellent': 2}
                }
            },
            'last_report_time': None
        }
        web_dashboard.update_stats(gen_stats, rep_stats)
        output = web_dashboard._render_prometheus_metrics()
        assert 'apolo_missions_total 2' in output
        assert 'apolo_device_status_count{mission="alpha",status="warning"} 3' in output
        assert 'apolo_device_status_count{mission="beta",status="excellent"} 2' in output
        assert 'apolo_device_type_count{mission="alpha",type="sensor"} 5' in output
        assert 'apolo_device_type_count{mission="beta",type="camera"} 2' in output
