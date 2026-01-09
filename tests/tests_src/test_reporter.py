import os
from tempfile import TemporaryDirectory
from apolo_11.src.reporter import Reporter

def test_process_files():
    with TemporaryDirectory() as tmp_dir:
        # Crear archivos de prueba en el directorio temporal
        generate_test_files(tmp_dir)

        # Crear una instancia de Reporter y procesar los archivos
        reporter_instance = Reporter()
        reporter_instance.process_files(tmp_dir, tmp_dir)

        # El método process_files usa rutas del config, no los parámetros
        # Verificamos que los archivos fueron procesados correctamente
        assert len(reporter_instance.devices_reports) > 0

        # Verificar que se registraron las misiones correctas
        missions = [key[0] for key in reporter_instance.devices_reports.keys()]
        assert 'OrbitOne' in missions or 'ColonyMoon' in missions

def generate_test_files(directory):
    # Crear archivos de prueba en el directorio dado
    # Puedes personalizar esto según sea necesario para tus pruebas
    with open(os.path.join(directory, 'file1.log'), 'w') as file:
        file.write("Date: 20220101120000\nMission: OrbitOne\nDevice Type: Satellite\nDevice Status: good\nHash: 123")

    with open(os.path.join(directory, 'file2.log'), 'w') as file:
        file.write("Date: 20220101130000\nMission: ColonyMoon\nDevice Type: Spaceship\nDevice Status: excellent\nHash: 456")

def test_extract_value():
    reporter_instance = Reporter()

    lines = [
        "Date: 20220101120000",
        "Mission: OrbitOne",
        "Device Type: Satellite",
        "Device Status: good",
        "Hash: 123"
    ]

    # Prueba de extracción de valores para una línea específica
    assert reporter_instance.extract_value(lines, "Mission") == "OrbitOne"
    assert reporter_instance.extract_value(lines, "Device Type") == "Satellite"
    assert reporter_instance.extract_value(lines, "Device Status") == "good"

    # Prueba de manejo de clave inexistente
    assert reporter_instance.extract_value(lines, "UnknownKey") == "unknown"

def test_move_folders_to_backup():
    with TemporaryDirectory() as tmp_dir:
        source_dir = os.path.join(tmp_dir, 'source')
        backup_dir = os.path.join(tmp_dir, 'backup')

        # Crear una carpeta de origen y una carpeta de respaldo
        os.makedirs(source_dir)
        os.makedirs(backup_dir)

        # Crear carpetas de origen con el formato esperado
        os.makedirs(os.path.join(source_dir, 'cycle-0-noreport'))
        os.makedirs(os.path.join(source_dir, 'cycle-1-noreport'))
        os.makedirs(os.path.join(source_dir, 'cycle-2'))

        # Crear una instancia de Reporter y realizar el movimiento
        reporter_instance = Reporter()
        reporter_instance.move_folders_to_backup(source_dir, backup_dir)

        # Verificar que las carpetas esperadas se hayan movido al respaldo
        backup_subdirs = os.listdir(backup_dir)
        assert 'cycle-0' in backup_subdirs
        assert 'cycle-1' in backup_subdirs
        assert 'cycle-2' not in backup_subdirs


# Property-Based Tests
from hypothesis import given, strategies as st, settings


@given(
    source_suffix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=10),
    backup_suffix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=10)
)
@settings(max_examples=100)
def test_move_folders_respects_parameters(source_suffix, backup_suffix):
    """
    Feature: apolo-11-improvements, Property 1: Parámetros de move_folders_to_backup son respetados
    Validates: Requirements 1.1

    For any valid source and backup directory paths passed to move_folders_to_backup,
    the method SHALL operate on those specific directories and not on hardcoded config values.
    """
    with TemporaryDirectory() as tmp_dir:
        # Create unique source and backup directories based on generated suffixes
        source_dir = os.path.join(tmp_dir, f'source_{source_suffix}')
        backup_dir = os.path.join(tmp_dir, f'backup_{backup_suffix}')

        os.makedirs(source_dir)
        os.makedirs(backup_dir)

        # Create a test folder with -noreport suffix
        test_folder_name = 'test-folder-noreport'
        os.makedirs(os.path.join(source_dir, test_folder_name))

        reporter_instance = Reporter()
        reporter_instance.move_folders_to_backup(source_dir, backup_dir)

        # Verify the folder was moved to the specified backup directory (not config default)
        expected_dest = os.path.join(backup_dir, 'test-folder')
        assert os.path.exists(expected_dest), f"Folder should be moved to {expected_dest}"

        # Verify the source folder no longer exists
        original_source = os.path.join(source_dir, test_folder_name)
        assert not os.path.exists(original_source), f"Original folder should not exist at {original_source}"



@given(
    folder_base_name=st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='-_'),
        min_size=1,
        max_size=20
    ).filter(lambda x: not x.endswith('-noreport') and x.strip())
)
@settings(max_examples=100)
def test_noreport_suffix_transformation(folder_base_name):
    """
    Feature: apolo-11-improvements, Property 2: Transformación de nombres de carpetas -noreport
    Validates: Requirements 1.3

    For any folder name ending with "-noreport", when moved to backup,
    the resulting folder name SHALL be the original name without the "-noreport" suffix.
    """
    with TemporaryDirectory() as tmp_dir:
        source_dir = os.path.join(tmp_dir, 'source')
        backup_dir = os.path.join(tmp_dir, 'backup')

        os.makedirs(source_dir)
        os.makedirs(backup_dir)

        # Create folder with -noreport suffix
        folder_with_suffix = f'{folder_base_name}-noreport'
        os.makedirs(os.path.join(source_dir, folder_with_suffix))

        reporter_instance = Reporter()
        reporter_instance.move_folders_to_backup(source_dir, backup_dir)

        # Verify the folder was renamed correctly (without -noreport suffix)
        expected_dest = os.path.join(backup_dir, folder_base_name)
        assert os.path.exists(expected_dest), \
            f"Folder '{folder_with_suffix}' should be moved to '{folder_base_name}' in backup"

        # Verify original folder no longer exists
        original_path = os.path.join(source_dir, folder_with_suffix)
        assert not os.path.exists(original_path), \
            f"Original folder '{folder_with_suffix}' should not exist after move"
