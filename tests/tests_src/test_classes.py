import pytest
from apolo_11.src.config import ConfigManager
from apolo_11.src.classes import Mission, Device, Configurable

# Fixture para configurar el entorno antes de cada prueba
@pytest.fixture
def config_fixture(tmpdir):
    # Asegurar que el directorio raíz existe
    tmpdir.ensure_dir("apolo_11/config")

    # Establecer la ubicación del archivo de configuración temporal
    tmp_config_path = tmpdir.join("apolo_11/config/config.yaml")
    tmp_config_path.write(
        """
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
        """
    )

    return tmpdir

# Test para verificar el funcionamiento correcto de la clase Mission
def test_mission_class(config_fixture):
    config = config_fixture

    # Crear una instancia de Mission
    mission_instance = Mission()

    # Verificar que la instancia se crea correctamente
    assert isinstance(mission_instance, Mission)

    # Verificar que los códigos y nombres de la misión se cargan correctamente desde la configuración
    assert mission_instance.codes == config["missions"]["codes"]
    assert mission_instance.name == config["missions"]["names"]

# Test para verificar el funcionamiento correcto de la clase Device
def test_device_class(config_fixture):
    config = config_fixture

    # Crear una instancia de Device
    device_instance = Device()

    # Verificar que la instancia se crea correctamente
    assert isinstance(device_instance, Device)

    # Verificar que los tipos y estados de dispositivos se cargan correctamente desde la configuración
    assert device_instance.type == config["devices"]["types"]
    assert device_instance.status == config["devices"]["status"]

# Test de borde: Verificar el manejo de una clave de configuración inexistente
def test_configurable_class_invalid_key():
    with pytest.raises(KeyError):
        invalid_key_instance = Configurable("invalid_key")
