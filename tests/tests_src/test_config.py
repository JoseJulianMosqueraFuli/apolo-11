import pytest
from apolo_11.src.config import ConfigManager


@pytest.fixture
def setup_test_environment(tmpdir):
    tmpdir.mkdir("apolo_11").mkdir("config")

    tmp_config_path = tmpdir.join("apolo_11/config/config.yaml")
    tmp_config_path.write(
        """
        general:
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

        routes:
          - devices: /results/devices/
        """
    )

    return tmpdir


def test_read_yaml_config(setup_test_environment):
    tmpdir = setup_test_environment

    config_manager = ConfigManager()
    config_path = tmpdir.join("apolo_11/config/config.yaml")

    config_data = config_manager.read_yaml_config(config_path)

    assert "general" in config_data
    assert "missions" in config_data
    assert "devices" in config_data
    assert "date_format" in config_data
    assert "routes" in config_data

def test_read_yaml_config_file_not_found():
    config_manager = ConfigManager()

    with pytest.raises(FileNotFoundError):
        config_data = config_manager.read_yaml_config("nonexistent.yaml")

def test_read_yaml_config_empty_file(setup_test_environment):
    tmpdir = setup_test_environment

    empty_config_path = tmpdir.join("apolo_11/config/empty_config.yaml")
    empty_config_path.write("")

    config_manager = ConfigManager()

    # ConfigManager should raise ValueError for empty files
    with pytest.raises(ValueError) as exc_info:
        config_manager.read_yaml_config(str(empty_config_path))

    assert "empty" in str(exc_info.value).lower()
