import threading
from datetime import datetime
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
import uvicorn

from .dashboard import MissionStats, DashboardStats
from .logging_config import get_logger

logger = get_logger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Apollo 11 Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0e1a; color: #e0e0e0; padding: 20px; }}
  h1 {{ text-align: center; color: #4fc3f7; margin-bottom: 24px; font-weight: 300; letter-spacing: 2px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 1200px; margin: 0 auto; }}
  .card {{ background: #111827; border: 1px solid #1e3a5f; border-radius: 12px; padding: 20px; }}
  .card h2 {{ color: #4fc3f7; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; border-bottom: 1px solid #1e3a5f; padding-bottom: 8px; }}
  .full {{ grid-column: 1 / -1; }}
  .stat {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1a1f2e; }}
  .stat:last-child {{ border: none; }}
  .stat-label {{ color: #8899aa; }}
  .stat-value {{ color: #e0e0e0; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; color: #8899aa; font-size: 12px; text-transform: uppercase; padding: 8px 4px; border-bottom: 1px solid #1e3a5f; }}
  td {{ padding: 8px 4px; border-bottom: 1px solid #1a1f2e; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin: 1px; }}
  .badge-excellent {{ background: #064e3b; color: #6ee7b7; }}
  .badge-good {{ background: #1e3a5f; color: #93c5fd; }}
  .badge-warning {{ background: #451a03; color: #fbbf24; }}
  .badge-faulty {{ background: #450a0a; color: #fca5a5; }}
  .badge-killed {{ background: #3b0764; color: #d8b4fe; }}
  .badge-unknown {{ background: #1f2937; color: #9ca3af; }}
  .footer {{ text-align: center; margin-top: 20px; color: #4b5563; font-size: 12px; }}
  .status-na {{ color: #6b7280; font-style: italic; }}
  #updated {{ color: #4b5563; font-size: 12px; text-align: center; margin-top: 12px; }}
</style>
</head>
<body>
  <h1>🛸 Apollo 11 Mission Control</h1>
  <div class="grid" id="content">
    <div class="card">
      <h2>System Status</h2>
      <div class="stat"><span class="stat-label">Files Generated</span><span class="stat-value">{files_generated}</span></div>
      <div class="stat"><span class="stat-label">Current Cycle</span><span class="stat-value">{current_cycle}</span></div>
      <div class="stat"><span class="stat-label">Last Report</span><span class="stat-value">{last_report}</span></div>
    </div>
    <div class="card">
      <h2>System Overview</h2>
      <div class="stat"><span class="stat-label">Total Missions</span><span class="stat-value">{total_missions}</span></div>
      <div class="stat"><span class="stat-label">Active Device Types</span><span class="stat-value">{total_device_types}</span></div>
      <div class="stat"><span class="stat-label">Total Devices</span><span class="stat-value">{total_devices}</span></div>
    </div>
    <div class="card full">
      <h2>Mission Statistics</h2>
      {missions_table}
    </div>
  </div>
  <p id="updated">Last updated: {updated_at}</p>
  <div class="footer">Apollo 11 Monitoring System &mdash; Auto-refreshes every 3s</div>
<script>
  setInterval(() => {{
    fetch('/api/stats')
      .then(r => r.json())
      .then(data => {{
        document.getElementById('content').innerHTML = render(data);
        document.getElementById('updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
      }});
  }}, 3000);
  function render(data) {{
    const lastRpt = data.last_report_time ? new Date(data.last_report_time).toLocaleString() : '<span class="status-na">N/A</span>';
    const missions = Object.entries(data.missions || {{}});
    const totalDevices = missions.reduce((s, [,m]) => s + Object.values(m.device_counts).reduce((a,b) => a+b, 0), 0);
    const deviceTypes = new Set();
    missions.forEach(([,m]) => Object.keys(m.device_counts).forEach(d => deviceTypes.add(d)));
    let rows = '';
    if (missions.length === 0) {{
      rows = '<tr><td colspan="4" class="status-na">Waiting for first report cycle...</td></tr>';
    }} else {{
      missions.forEach(([name, m]) => {{
        const types = Object.keys(m.device_counts).join(', ') || 'None';
        const total = Object.values(m.device_counts).reduce((a,b) => a+b, 0);
        const badges = Object.entries(m.status_counts).map(([s,c]) =>
          `<span class="badge badge-${{s.toLowerCase()}}">${{s}}: ${{c}}</span>`
        ).join(' ');
        rows += `<tr><td>${{name}}</td><td>${{types}}</td><td>${{total}}</td><td>${{badges || '<span class="status-na">No data</span>'}}</td></tr>`;
      }});
    }}
    return `
      <div class="card">
        <h2>System Status</h2>
        <div class="stat"><span class="stat-label">Files Generated</span><span class="stat-value">${{data.files_generated}}</span></div>
        <div class="stat"><span class="stat-label">Current Cycle</span><span class="stat-value">${{data.current_cycle}}</span></div>
        <div class="stat"><span class="stat-label">Last Report</span><span class="stat-value">${{lastRpt}}</span></div>
      </div>
      <div class="card">
        <h2>System Overview</h2>
        <div class="stat"><span class="stat-label">Total Missions</span><span class="stat-value">${{missions.length}}</span></div>
        <div class="stat"><span class="stat-label">Active Device Types</span><span class="stat-value">${{deviceTypes.size}}</span></div>
        <div class="stat"><span class="stat-label">Total Devices</span><span class="stat-value">${{totalDevices}}</span></div>
      </div>
      <div class="card full">
        <h2>Mission Statistics</h2>
        <table><thead><tr><th>Mission</th><th>Device Types</th><th>Total Devices</th><th>Status Summary</th></tr></thead>
        <tbody>${{rows}}</tbody></table>
      </div>`;
  }}
</script>
</body>
</html>"""


class WebDashboard:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.stats = DashboardStats(
            files_generated=0,
            current_cycle=0,
            missions={},
            last_report_time=None
        )
        self._lock = threading.Lock()
        self.app = FastAPI(title="Apollo 11 Dashboard")
        self._setup_routes()
        self._server: uvicorn.Server | None = None

    def _setup_routes(self):
        @self.app.get("/api/stats")
        async def get_stats():
            with self._lock:
                return self._stats_to_dict()

        @self.app.get("/metrics", response_class=PlainTextResponse)
        async def metrics():
            with self._lock:
                return self._render_prometheus_metrics()

        @self.app.get("/", response_class=HTMLResponse)
        async def index():
            with self._lock:
                return self._render_html()

    def _stats_to_dict(self) -> dict:
        return {
            "files_generated": self.stats.files_generated,
            "current_cycle": self.stats.current_cycle,
            "last_report_time": (
                self.stats.last_report_time.isoformat()
                if self.stats.last_report_time else None
            ),
            "missions": {
                name: {
                    "device_counts": dict(ms.device_counts),
                    "status_counts": dict(ms.status_counts),
                }
                for name, ms in self.stats.missions.items()
            }
        }

    def update_stats(self, generator_stats: dict[str, Any], reporter_stats: dict[str, Any]) -> None:
        with self._lock:
            self.stats.files_generated = generator_stats.get('files_count', 0)
            self.stats.current_cycle = generator_stats.get('cycle', 0)
            self.stats.last_report_time = reporter_stats.get('last_report_time')

            missions_data = reporter_stats.get('missions', {})
            self.stats.missions = {}
            for mission_name, mission_data in missions_data.items():
                self.stats.missions[mission_name] = MissionStats(
                    name=mission_name,
                    device_counts=mission_data.get('device_counts', {}),
                    status_counts=mission_data.get('status_counts', {})
                )

    def _render_html(self) -> str:
        stats = self._stats_to_dict()
        missions = stats.get("missions", {})
        total_devices = sum(
            sum(dc.values())
            for m in missions.values()
            if (dc := m.get("device_counts", {}))
        )
        total_device_types = len({
            dt
            for m in missions.values()
            for dt in (m.get("device_counts", {}) or {}).keys()
        })
        last_report = (
            self.stats.last_report_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.stats.last_report_time else "N/A"
        )

        if not missions:
            missions_rows = '<tr><td colspan="4" class="status-na">Waiting for first report cycle...</td></tr>'
        else:
            rows = []
            for name, m in missions.items():
                types = ", ".join(m.get("device_counts", {}).keys()) or "None"
                total = sum(m.get("device_counts", {}).values())
                badges = " ".join(
                    f'<span class="badge badge-{s.lower()}">{s}: {c}</span>'
                    for s, c in m.get("status_counts", {}).items()
                )
                if not badges:
                    badges = '<span class="status-na">No data</span>'
                rows.append(f"<tr><td>{name}</td><td>{types}</td><td>{total}</td><td>{badges}</td></tr>")
            missions_rows = "".join(rows)

        return HTML_TEMPLATE.format(
            files_generated=stats["files_generated"],
            current_cycle=stats["current_cycle"],
            last_report=last_report,
            total_missions=len(missions),
            total_device_types=total_device_types,
            total_devices=total_devices,
            missions_table=f'<table><thead><tr><th>Mission</th><th>Device Types</th><th>Total Devices</th><th>Status Summary</th></tr></thead><tbody>{missions_rows}</tbody></table>',
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def start(self):
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning",
        )
        self._server = uvicorn.Server(config)
        thread = threading.Thread(target=self._server.run, daemon=True)
        thread.start()
        logger.info("Web dashboard started on http://%s:%s", self.host, self.port)

    def update_display(self) -> None:
        """No-op needed (data is served via HTTP)."""

    def stop(self):
        if self._server:
            self._server.should_exit = True
            logger.info("Web dashboard stopped")

    def _render_prometheus_metrics(self) -> str:
        lines = []
        lines.append("# HELP apolo_files_generated_total Total files generated")
        lines.append("# TYPE apolo_files_generated_total counter")
        lines.append(f"apolo_files_generated_total {self.stats.files_generated}")
        lines.append("")
        lines.append("# HELP apolo_current_cycle Current generation cycle number")
        lines.append("# TYPE apolo_current_cycle gauge")
        lines.append(f"apolo_current_cycle {self.stats.current_cycle}")
        lines.append("")
        lines.append("# HELP apolo_missions_total Number of active missions")
        lines.append("# TYPE apolo_missions_total gauge")
        lines.append(f"apolo_missions_total {len(self.stats.missions)}")
        lines.append("")

        for mission_name, ms in self.stats.missions.items():
            for status, count in ms.status_counts.items():
                safe_name = mission_name.lower().replace(" ", "_")
                lines.append("# HELP apolo_device_status_count Device count by mission and status")
                lines.append("# TYPE apolo_device_status_count gauge")
                lines.append(
                    f'apolo_device_status_count{{mission="{safe_name}",status="{status}"}} {count}'
                )
            for dtype, count in ms.device_counts.items():
                safe_name = mission_name.lower().replace(" ", "_")
                safe_type = dtype.lower().replace(" ", "_")
                lines.append("# HELP apolo_device_type_count Device count by mission and type")
                lines.append("# TYPE apolo_device_type_count gauge")
                lines.append(
                    f'apolo_device_type_count{{mission="{safe_name}",type="{safe_type}"}} {count}'
                )

        lines.append("")
        return "\n".join(lines)
