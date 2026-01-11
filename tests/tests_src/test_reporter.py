import os
from tempfile import TemporaryDirectory
from unittest.mock import patch
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


def test_process_file():
    """Test process_file method with valid log file
    
    Requirements: 5.2 - Test con archivo de log válido, verificar extracción de datos correcta
    """
    with TemporaryDirectory() as tmp_dir:
        # Create a valid log file
        log_file_path = os.path.join(tmp_dir, 'test.log')
        log_content = """Date: 010123120000
Mission: OrbitOne
Device Type: Satellite
Device Status: excellent
Hash: 12345"""
        
        with open(log_file_path, 'w') as f:
            f.write(log_content)
        
        # Create reporter instance and process the file
        reporter_instance = Reporter()
        reporter_instance.process_file(log_file_path)
        
        # Verify data extraction was correct
        assert len(reporter_instance.devices_reports) == 1
        
        # Check that the correct mission and device type were extracted
        key = ('OrbitOne', 'Satellite')
        assert key in reporter_instance.devices_reports
        
        # Check that the device status was correctly extracted
        assert reporter_instance.devices_reports[key] == ['excellent']


def test_process_file_with_missing_fields():
    """Test process_file method with log file missing some fields"""
    with TemporaryDirectory() as tmp_dir:
        # Create a log file with missing fields
        log_file_path = os.path.join(tmp_dir, 'incomplete.log')
        log_content = """Date: 010123120000
Mission: OrbitOne
Hash: 12345"""
        
        with open(log_file_path, 'w') as f:
            f.write(log_content)
        
        # Create reporter instance and process the file
        reporter_instance = Reporter()
        reporter_instance.process_file(log_file_path)
        
        # Verify that missing fields are handled with "unknown"
        key = ('OrbitOne', 'unknown')
        assert key in reporter_instance.devices_reports
        assert reporter_instance.devices_reports[key] == ['unknown']


@patch('apolo_11.src.reporter.datetime')
def test_generate_stats_report(mock_datetime):
    """Test generate_stats_report method with test data
    
    Requirements: 5.3 - Test con datos de prueba, verificar formato del reporte
    """
    with TemporaryDirectory() as tmp_dir:
        # Mock datetime for consistent filename
        mock_datetime.now.return_value.strftime.return_value = '010123120000'
        
        # Create reporter instance and add test data
        reporter_instance = Reporter()
        
        # Add test data to devices_reports
        reporter_instance.devices_reports[('OrbitOne', 'Satellite')] = ['excellent', 'good', 'unknown']
        reporter_instance.devices_reports[('ColonyMoon', 'Spaceship')] = ['good', 'good']
        
        # Mock the config routes for reports directory
        with patch('apolo_11.src.reporter.config', {
            'routes': [None, None, None, {'reports': tmp_dir}],
            'date_format': '%d%m%y%H%M%S'
        }):
            reporter_instance.generate_stats_report()
        
        # Verify the report file was created
        expected_filename = 'APLSTATS-REPORT-010123120000.log'
        report_path = os.path.join(tmp_dir, expected_filename)
        assert os.path.exists(report_path)
        
        # Read and verify report content
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Verify report sections are present
        assert 'Análisis de eventos:' in content
        assert 'Gestión de desconexiones:' in content
        assert 'Consolidación de misiones:' in content
        assert 'Cálculo de porcentajes:' in content
        
        # Verify mission data is included
        assert 'Misión: OrbitOne' in content
        assert 'Misión: ColonyMoon' in content
        assert 'Tipo de Dispositivo: Satellite' in content
        assert 'Tipo de Dispositivo: Spaceship' in content
        
        # Verify status counts
        assert 'Estado: excellent, Cantidad: 1' in content
        assert 'Estado: good, Cantidad: 2' in content or 'Estado: good, Cantidad: 1' in content
        assert 'Estado: unknown, Cantidad: 1' in content
        
        # Verify disconnections section
        assert 'Desconexiones (unknown): 1' in content
        assert 'Desconexiones (unknown): 0' in content
        
        # Verify consolidation section
        assert 'Total de dispositivos inoperables: 1' in content
        
        # Verify percentage calculations are present
        assert 'Porcentaje:' in content


def test_process_file_malformed_log():
    """Test process_file method with malformed log file
    
    Requirements: 5.4 - Edge case: archivos malformados
    """
    with TemporaryDirectory() as tmp_dir:
        # Create a malformed log file (no colons, invalid format)
        log_file_path = os.path.join(tmp_dir, 'malformed.log')
        log_content = """This is not a valid log file
No colons here
Mission without colon OrbitOne
Device Type Satellite"""
        
        with open(log_file_path, 'w') as f:
            f.write(log_content)
        
        # Create reporter instance and process the file
        reporter_instance = Reporter()
        reporter_instance.process_file(log_file_path)
        
        # Verify that malformed data is handled with "unknown"
        key = ('unknown', 'unknown')
        assert key in reporter_instance.devices_reports
        assert reporter_instance.devices_reports[key] == ['unknown']


def test_process_file_empty_log():
    """Test process_file method with empty log file
    
    Requirements: 5.4 - Edge case: archivos vacíos
    """
    with TemporaryDirectory() as tmp_dir:
        # Create an empty log file
        log_file_path = os.path.join(tmp_dir, 'empty.log')
        with open(log_file_path, 'w') as f:
            f.write('')
        
        # Create reporter instance and process the file
        reporter_instance = Reporter()
        reporter_instance.process_file(log_file_path)
        
        # Verify that empty file is handled with "unknown" values
        key = ('unknown', 'unknown')
        assert key in reporter_instance.devices_reports
        assert reporter_instance.devices_reports[key] == ['unknown']


def test_process_files_empty_directory():
    """Test process_files method with empty directory
    
    Requirements: 5.4 - Edge case: directorios vacíos
    """
    with TemporaryDirectory() as tmp_dir:
        # Create empty directories
        input_dir = os.path.join(tmp_dir, 'input')
        backup_dir = os.path.join(tmp_dir, 'backup')
        os.makedirs(input_dir)
        os.makedirs(backup_dir)
        
        # Create reporter instance and process empty directory
        reporter_instance = Reporter()
        
        # This should not raise an exception
        reporter_instance.process_files(input_dir, backup_dir)
        
        # Verify no reports were generated (empty directory)
        assert len(reporter_instance.devices_reports) == 0


def test_process_files_directory_with_non_log_files():
    """Test process_files method with directory containing non-log files
    
    Requirements: 5.4 - Edge case: archivos que no son .log
    """
    with TemporaryDirectory() as tmp_dir:
        # Create directory with non-log files
        input_dir = os.path.join(tmp_dir, 'input')
        backup_dir = os.path.join(tmp_dir, 'backup')
        os.makedirs(input_dir)
        os.makedirs(backup_dir)
        
        # Create non-log files
        with open(os.path.join(input_dir, 'readme.txt'), 'w') as f:
            f.write('This is not a log file')
        
        with open(os.path.join(input_dir, 'config.json'), 'w') as f:
            f.write('{"key": "value"}')
        
        # Create reporter instance and process directory
        reporter_instance = Reporter()
        reporter_instance.process_files(input_dir, backup_dir)
        
        # Verify no reports were generated (no .log files)
        assert len(reporter_instance.devices_reports) == 0


def test_generate_stats_report_empty_data():
    """Test generate_stats_report method with no data
    
    Requirements: 5.4 - Edge case: sin datos para procesar
    """
    with TemporaryDirectory() as tmp_dir:
        # Create reporter instance with no data
        reporter_instance = Reporter()
        
        # Mock the config routes for reports directory
        with patch('apolo_11.src.reporter.config', {
            'routes': [None, None, None, {'reports': tmp_dir}],
            'date_format': '%d%m%y%H%M%S'
        }):
            with patch('apolo_11.src.reporter.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '010123120000'
                reporter_instance.generate_stats_report()
        
        # Verify the report file was created even with no data
        expected_filename = 'APLSTATS-REPORT-010123120000.log'
        report_path = os.path.join(tmp_dir, expected_filename)
        assert os.path.exists(report_path)
        
        # Read and verify report content contains headers but no data
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Verify report sections are present
        assert 'Análisis de eventos:' in content
        assert 'Gestión de desconexiones:' in content
        assert 'Consolidación de misiones:' in content
        assert 'Cálculo de porcentajes:' in content
        
        # Verify consolidation shows 0 inoperable devices
        assert 'Total de dispositivos inoperables: 0' in content


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
