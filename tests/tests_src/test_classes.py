import pytest
from hypothesis import given, strategies as st
from apolo_11.src.config import ConfigManager
from apolo_11.src.classes import Mission, Device, Configurable


# Test para verificar el funcionamiento correcto de la clase Mission
def test_mission_class():
    # Cargar config real con ConfigManager
    config = ConfigManager.read_yaml_config()
    
    # Crear una instancia de Mission
    mission_instance = Mission()

    # Verificar que la instancia se crea correctamente
    assert isinstance(mission_instance, Mission)

    # Comparar Mission.codes contra config["missions"]["codes"]
    assert mission_instance.codes == config["missions"]["codes"]
    
    # Comparar Mission.name contra config["missions"]["names"]
    assert mission_instance.name == config["missions"]["names"]


# Test para verificar el funcionamiento correcto de la clase Device
def test_device_class():
    # Cargar config real con ConfigManager
    config = ConfigManager.read_yaml_config()
    
    # Crear una instancia de Device
    device_instance = Device()

    # Verificar que la instancia se crea correctamente
    assert isinstance(device_instance, Device)

    # Comparar Device.type contra config["devices"]["types"]
    assert device_instance.type == config["devices"]["types"]
    
    # Comparar Device.status contra config["devices"]["status"]
    assert device_instance.status == config["devices"]["status"]

# Test de borde: Verificar el manejo de una clave de configuración inexistente
def test_configurable_class_invalid_key():
    with pytest.raises(KeyError):
        invalid_key_instance = Configurable("invalid_key")


@given(st.text().filter(lambda x: x not in ["missions", "devices", "general", "date_format", "routes"]))
def test_property_invalid_config_keys_raise_keyerror(invalid_key):
    """
    Property 3: Claves de configuración inválidas lanzan KeyError
    Validates: Requirements 2.3
    
    For any configuration key that does not exist in the loaded configuration,
    the Configurable class SHALL raise a KeyError exception.
    """
    with pytest.raises(KeyError):
        Configurable(invalid_key)
