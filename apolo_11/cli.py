import argparse
import asyncio
import signal
from contextlib import nullcontext

from apolo_11.src import generator, reporter
from apolo_11.src.config import ConfigManager
from apolo_11.src.logging_config import setup_logging
from apolo_11.src.dashboard import Dashboard


def _parse_args(config_data: dict) -> argparse.Namespace | None:
    parser = argparse.ArgumentParser(
        description='Generate files and generate reports for the Apolo 11 mission'
    )
    general_config = config_data['general']
    default_time_cycle = general_config['time_cycle']

    parser.add_argument('--num_files_min', type=int,
                        default=general_config['num_files_initial'],
                        help='Minimum number of files to generate')
    parser.add_argument('--num_files_max', type=int,
                        default=general_config['num_files_final'],
                        help='Maximum number of files to generate')
    parser.add_argument('--generator_interval', type=int,
                        default=default_time_cycle,
                        help='Time interval in seconds for the generator')
    parser.add_argument('--reporter_interval', type=int,
                        default=default_time_cycle * 3,
                        help='Time interval in seconds for the reporter')
    parser.add_argument('--dashboard', action='store_true',
                        help='Enable dashboard TUI for real-time monitoring')
    args = parser.parse_args()

    if args.num_files_min <= 0:
        parser.error('--num_files_min must be a positive integer')
    if args.num_files_max <= 0:
        parser.error('--num_files_max must be a positive integer')
    if args.num_files_max > 100000:
        parser.error('--num_files_max cannot exceed 100000')
    if args.num_files_min > args.num_files_max:
        parser.error('--num_files_min cannot be greater than --num_files_max')
    if args.generator_interval <= 0:
        parser.error('--generator_interval must be a positive integer')
    if args.reporter_interval <= 0:
        parser.error('--reporter_interval must be a positive integer')
    return args


async def _run_generator(gen: generator.Generator, rep: reporter.Reporter,
                         args: argparse.Namespace, dashboard: Dashboard | None,
                         stop: asyncio.Event):
    logger = setup_logging()
    while not stop.is_set():
        await asyncio.to_thread(gen.generate_files, args.num_files_min, args.num_files_max)

        if dashboard:
            dashboard.update_stats(
                {'files_count': gen.generate_files_call_count * args.num_files_max,
                 'cycle': gen.generate_files_call_count},
                {'missions': rep.mission_stats(),
                 'last_report_time': rep.last_report_time},
            )
            dashboard.update_display()

        try:
            await asyncio.wait_for(stop.wait(), timeout=args.generator_interval)
        except TimeoutError:
            pass


async def _run_reporter(gen: generator.Generator, rep: reporter.Reporter,
                        args: argparse.Namespace, dashboard: Dashboard | None,
                        config_data: dict, stop: asyncio.Event):
    logger = setup_logging()
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=args.reporter_interval)
        except TimeoutError:
            pass
        if stop.is_set():
            break

        await asyncio.to_thread(
            rep.process_files,
            config_data['routes']['devices'],
            config_data['routes']['backups'],
        )

        if dashboard:
            from datetime import datetime
            dashboard.update_stats(
                {'files_count': gen.generate_files_call_count * args.num_files_max,
                 'cycle': gen.generate_files_call_count},
                {'missions': rep.mission_stats(),
                 'last_report_time': rep.last_report_time},
            )
            dashboard.update_display()


async def _async_main():
    logger = setup_logging()
    config_data = ConfigManager.read_yaml_config()

    args = _parse_args(config_data)
    if args is None:
        return

    if args.reporter_interval <= args.generator_interval:
        logger.error("El intervalo de reportes debe ser mayor que el intervalo de generadores.")
        return

    gen = generator.Generator(config_data=config_data)
    gen.generate_device_folder()

    rep = reporter.Reporter(config_data=config_data)

    dashboard = Dashboard() if args.dashboard else None
    live = dashboard.start_live_display() if dashboard else None

    stop = asyncio.Event()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: stop.set())

    try:
        with live if live else nullcontext():
            await asyncio.gather(
                _run_generator(gen, rep, args, dashboard, stop),
                _run_reporter(gen, rep, args, dashboard, config_data, stop),
            )
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario.")
    finally:
        stop.set()
        if dashboard:
            dashboard.stop_display()


def main():
    asyncio.run(_async_main())
