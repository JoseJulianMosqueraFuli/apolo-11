import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def sample_config_yaml():
    return """general:
  num_files_initial: 1
  num_files_final: 100
  time_cycle: 20

missions:
  codes:
    OrbitOne: ORBONE
    ColonyMoon: CLNM
  names:
    - OrbitOne
    - ColonyMoon

devices:
  status:
    - excellent
    - good
  types:
    - Satellite
    - Spaceship

date_format: "%d%m%y%H%M%S"

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

routes:
  - results: /tmp/results
  - devices: /tmp/results/devices
  - backups: /tmp/results/backups/
  - reports: /tmp/results/reports/
"""


@pytest.fixture
def temp_config_file(sample_config_yaml):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(sample_config_yaml)
        temp_path = f.name
    yield temp_path
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_results_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        (base / "devices").mkdir(parents=True, exist_ok=True)
        (base / "backups").mkdir(parents=True, exist_ok=True)
        (base / "reports").mkdir(parents=True, exist_ok=True)
        yield base
