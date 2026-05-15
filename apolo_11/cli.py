import argparse
import asyncio
import signal
from contextlib import nullcontext
from datetime import datetime

from apolo_11.src import generator, reporter
from apolo_11.src.config import ConfigManager
from apolo_11.src.logging_config import setup_logging
from apolo_11.src.dashboard import Dashboard
from apolo_11.src.web_dashboard import WebDashboard
from apolo_11.src.messaging import MessageBroker, QUEUE_GENERATED


def _parse_args(config_data: dict, argv: list[str] | None = None) -> argparse.Namespace | None:
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
    parser.add_argument('--api', action='store_true',
                        help='Enable web API dashboard')
    parser.add_argument('--api-port', type=int, default=8000,
                        help='Port for the web API dashboard (default: 8000)')
    args = parser.parse_args(argv)

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
                         args: argparse.Namespace, dashboards: list,
                         stop: asyncio.Event, broker: MessageBroker | None = None):
    while not stop.is_set():
        await asyncio.to_thread(gen.generate_files, args.num_files_min, args.num_files_max)

        if broker and broker.enabled:
            await asyncio.to_thread(
                broker.publish, QUEUE_GENERATED, {
                    'cycle': gen.generate_files_call_count,
                    'files_count': gen.generate_files_call_count * args.num_files_max,
                    'num_files_min': args.num_files_min,
                    'num_files_max': args.num_files_max,
                    'timestamp': str(datetime.now()),
                })

        if dashboards:
            gen_stats = {'files_count': gen.generate_files_call_count * args.num_files_max,
                         'cycle': gen.generate_files_call_count}
            rep_stats = {'missions': rep.mission_stats(),
                         'last_report_time': rep.last_report_time}
            for d in dashboards:
                d.update_stats(gen_stats, rep_stats)
                d.update_display()

        try:
            await asyncio.wait_for(stop.wait(), timeout=args.generator_interval)
        except TimeoutError:
            pass


async def _run_reporter(gen: generator.Generator, rep: reporter.Reporter,
                        args: argparse.Namespace, dashboards: list,
                        config_data: dict, stop: asyncio.Event):
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=args.reporter_interval)
        except (TimeoutError, asyncio.CancelledError):
            pass
        if stop.is_set():
            break

        await asyncio.to_thread(
            rep.process_files,
            config_data['routes']['devices'],
            config_data['routes']['backups'],
        )

        if dashboards:
            gen_stats = {'files_count': gen.generate_files_call_count * args.num_files_max,
                         'cycle': gen.generate_files_call_count}
            rep_stats = {'missions': rep.mission_stats(),
                         'last_report_time': rep.last_report_time}
            for d in dashboards:
                d.update_stats(gen_stats, rep_stats)
                d.update_display()


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

    broker = MessageBroker()
    if broker.enabled:
        logger.info("Mensajería habilitada (RabbitMQ)")

    dashboards: list = []

    tui_dashboard = Dashboard() if args.dashboard else None
    if tui_dashboard:
        dashboards.append(tui_dashboard)

    web_dashboard = WebDashboard(port=args.api_port) if args.api else None
    if web_dashboard:
        dashboards.append(web_dashboard)

    live = tui_dashboard.start_live_display() if tui_dashboard else None

    if web_dashboard:
        web_dashboard.start()

    stop = asyncio.Event()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: stop.set())

    try:
        with live if live else nullcontext():
            await asyncio.gather(
                _run_generator(gen, rep, args, dashboards, stop, broker),
                _run_reporter(gen, rep, args, dashboards, config_data, stop),
            )
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario.")
    finally:
        stop.set()
        broker.close()
        if tui_dashboard:
            tui_dashboard.stop_display()
        if web_dashboard:
            web_dashboard.stop()


def main():
    asyncio.run(_async_main())
