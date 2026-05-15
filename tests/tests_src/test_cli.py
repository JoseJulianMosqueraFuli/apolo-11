import asyncio
from unittest.mock import MagicMock, patch

import pytest

from apolo_11.cli import _run_generator, _run_reporter, _parse_args

BASE_CONFIG = {'general': {'num_files_initial': 1, 'num_files_final': 100, 'time_cycle': 20}}


class TestParseArgs:
    def test_valid_args(self):
        args = _parse_args(BASE_CONFIG, argv=[
            '--num_files_min', '5', '--num_files_max', '50',
            '--generator_interval', '10', '--reporter_interval', '30'])
        assert args.num_files_min == 5
        assert args.num_files_max == 50
        assert args.generator_interval == 10
        assert args.reporter_interval == 30

    def test_defaults_from_config(self):
        config = {'general': {'num_files_initial': 3, 'num_files_final': 200, 'time_cycle': 15}}
        args = _parse_args(config, argv=[])
        assert args.num_files_min == 3
        assert args.num_files_max == 200
        assert args.generator_interval == 15
        assert args.reporter_interval == 45

    def test_negative_min_raises(self):
        with pytest.raises(SystemExit):
            _parse_args(BASE_CONFIG, argv=['--num_files_min', '-5'])

    def test_zero_max_raises(self):
        with pytest.raises(SystemExit):
            _parse_args(BASE_CONFIG, argv=['--num_files_max', '0'])

    def test_min_greater_than_max_raises(self):
        with pytest.raises(SystemExit):
            _parse_args(BASE_CONFIG, argv=['--num_files_min', '50', '--num_files_max', '10'])

    def test_exceeds_limit_raises(self):
        with pytest.raises(SystemExit):
            _parse_args(BASE_CONFIG, argv=['--num_files_max', '100001'])

    def test_dashboard_flag(self):
        args = _parse_args(BASE_CONFIG, argv=['--dashboard'])
        assert args.dashboard is True

    def test_dashboard_default_false(self):
        args = _parse_args(BASE_CONFIG, argv=[])
        assert args.dashboard is False

    def test_generator_interval_zero_raises(self):
        with pytest.raises(SystemExit):
            _parse_args(BASE_CONFIG, argv=['--generator_interval', '0'])

    def test_reporter_interval_zero_raises(self):
        with pytest.raises(SystemExit):
            _parse_args(BASE_CONFIG, argv=['--reporter_interval', '0'])


class TestAsyncMain:
    @pytest.mark.asyncio
    async def test_reporter_interval_error_returns(self):
        with patch('apolo_11.cli.ConfigManager.read_yaml_config',
                   return_value={'general': {'num_files_initial': 1, 'num_files_final': 100,
                                             'time_cycle': 10},
                                 'missions': {'codes': {}, 'names': []},
                                 'devices': {'types': [], 'status': []},
                                 'date_format': '%d%m%y%H%M%S',
                                 'routes': {'devices': '/tmp', 'backups': '/tmp', 'results': '/tmp'}}):
            with patch('apolo_11.cli.setup_logging') as mock_setup:
                mock_logger = MagicMock()
                mock_setup.return_value = mock_logger
                from apolo_11.cli import _async_main
                with patch('apolo_11.cli.sys.argv', ['apolo', '--generator_interval', '5',
                                                       '--reporter_interval', '3']):
                    await _async_main()
                    mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_main_runs_tasks_and_stops(self):
        with patch('apolo_11.cli.ConfigManager.read_yaml_config',
                   return_value={'general': {'num_files_initial': 1, 'num_files_final': 100,
                                             'time_cycle': 20},
                                 'missions': {'codes': {}, 'names': []},
                                 'devices': {'types': [], 'status': []},
                                 'date_format': '%d%m%y%H%M%S',
                                 'routes': {'devices': '/tmp', 'backups': '/tmp', 'results': '/tmp'}}):
            with patch('apolo_11.cli.setup_logging'), \
                 patch('apolo_11.src.generator.Generator') as mock_gen, \
                 patch('apolo_11.src.reporter.Reporter'), \
                 patch('apolo_11.cli.Dashboard'), \
                 patch('apolo_11.cli.signal'):
                from apolo_11.cli import _async_main
                with patch('apolo_11.cli.sys.argv', ['apolo', '--generator_interval', '3',
                                                       '--reporter_interval', '6',
                                                       '--num_files_min', '1',
                                                       '--num_files_max', '5']):
                    with pytest.raises(TimeoutError):
                        await asyncio.wait_for(_async_main(), timeout=0.5)
                    mock_gen.return_value.generate_device_folder.assert_called_once()


class TestRunGenerator:
    @pytest.mark.asyncio
    async def test_calls_generate_files_and_updates_dashboard(self):
        gen = MagicMock()
        rep = MagicMock()
        rep.mission_stats.return_value = {}
        rep.last_report_time = None
        dashboard = MagicMock()
        args = MagicMock(num_files_min=1, num_files_max=5, generator_interval=1)
        stop = asyncio.Event()

        async def schedule_stop():
            await asyncio.sleep(0.3)
            stop.set()

        await asyncio.gather(
            _run_generator(gen, rep, args, dashboard, stop),
            schedule_stop(),
        )

        gen.generate_files.assert_called_once_with(1, 5)
        assert dashboard.update_stats.call_count >= 1
        dashboard.update_display.assert_called_once()

    @pytest.mark.asyncio
    async def test_stops_when_stop_is_set_before_iteration(self):
        gen = MagicMock()
        rep = MagicMock()
        rep.mission_stats.return_value = {}
        dashboard = MagicMock()
        stop = asyncio.Event()
        stop.set()

        await _run_generator(gen, rep, MagicMock(), dashboard, stop)

        gen.generate_files.assert_not_called()

    @pytest.mark.asyncio
    async def test_works_without_dashboard(self):
        gen = MagicMock()
        rep = MagicMock()
        rep.mission_stats.return_value = {}
        args = MagicMock(num_files_min=1, num_files_max=5, generator_interval=1)
        stop = asyncio.Event()

        async def schedule_stop():
            await asyncio.sleep(0.3)
            stop.set()

        await asyncio.gather(
            _run_generator(gen, rep, args, None, stop),
            schedule_stop(),
        )

        gen.generate_files.assert_called_once()


class TestRunReporter:
    @pytest.mark.asyncio
    async def test_calls_process_files_and_updates_dashboard(self):
        gen = MagicMock()
        gen.generate_files_call_count = 5
        rep = MagicMock()
        rep.mission_stats.return_value = {}
        rep.last_report_time = None
        dashboard = MagicMock()
        args = MagicMock(num_files_min=1, num_files_max=5, reporter_interval=0)
        config_data = {'routes': {'devices': '/tmp/devices', 'backups': '/tmp/backups'}}
        stop = asyncio.Event()

        async def schedule_stop():
            await asyncio.sleep(0.2)
            stop.set()

        await asyncio.gather(
            _run_reporter(gen, rep, args, dashboard, config_data, stop),
            schedule_stop(),
        )

        rep.process_files.assert_called_with('/tmp/devices', '/tmp/backups')
        assert rep.process_files.call_count >= 1
        assert dashboard.update_stats.call_count >= 1
        assert dashboard.update_display.call_count >= 1

    @pytest.mark.asyncio
    async def test_stops_when_stop_is_set_before_timeout(self):
        gen = MagicMock()
        rep = MagicMock()
        dashboard = MagicMock()
        args = MagicMock(reporter_interval=10)
        stop = asyncio.Event()
        stop.set()

        await _run_reporter(gen, rep, args, dashboard, {}, stop)

        rep.process_files.assert_not_called()
