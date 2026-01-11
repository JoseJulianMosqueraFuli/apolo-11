import os
import pytest
from datetime import datetime
from unittest.mock import patch
from apolo_11.src.generator import Generator

@pytest.fixture
def generator_instance():
    return Generator()

def test_generate_device_folder(generator_instance, tmpdir):
    # El método usa el path base proporcionado
    base_path = str(tmpdir)
    generator_instance.generate_device_folder(base_path)
    output_dir = os.path.join(base_path, 'devices')
    assert os.path.exists(output_dir)

def test_generate_filename(generator_instance):
    mission_name = 'OrbitOne'
    file_number = 42
    expected_filename = 'APLORBONE-0042.log'

    result = generator_instance.generate_filename(mission_name, file_number)

    assert result == expected_filename

@patch('apolo_11.src.generator.datetime')
def test_generate_contentfile(mock_datetime, generator_instance):
    mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

    file_number = 1
    result = generator_instance.generate_contentfile(file_number)

    # generate_contentfile retorna un objeto GeneratedFile
    assert result.filename.startswith('APL')
    assert result.filename.endswith('.log')
    assert 'Date: 010123120000' in result.content
    assert 'Mission: ' in result.content
    assert 'Device Type: ' in result.content
    assert 'Device Status: ' in result.content
    assert 'Hash: ' in result.content

@patch('builtins.open', create=True)
@patch('os.path.join')
def test_load_cycle_number(mock_join, mock_open, generator_instance):
    # Test con archivo existente
    mock_join.return_value = '/mocked/path/cycle_number.txt'
    mock_file = mock_open.return_value.__enter__.return_value
    mock_file.read.return_value.strip.return_value = '42'
    
    generator_instance.load_cycle_number()
    
    assert generator_instance.generate_files_call_count == 42
    mock_open.assert_called_with('/mocked/path/cycle_number.txt', 'r')

@patch('builtins.open', create=True)
@patch('os.path.join')
def test_load_cycle_number_file_not_found(mock_join, mock_open, generator_instance):
    # Test con archivo no existente
    mock_join.return_value = '/mocked/path/cycle_number.txt'
    mock_open.side_effect = [FileNotFoundError, mock_open.return_value]
    
    generator_instance.load_cycle_number()
    
    # Cuando no existe el archivo, se inicializa en 0 y luego save_cycle_number() lo incrementa a 1
    assert generator_instance.generate_files_call_count == 1
    # Verifica que se llama save_cycle_number cuando no existe el archivo
    assert mock_open.call_count == 2  # Una para leer (falla) y otra para escribir

@patch('builtins.open', create=True)
@patch('os.path.join')
def test_save_cycle_number(mock_join, mock_open, generator_instance):
    # Test que verifica incremento y guardado correcto
    mock_join.return_value = '/mocked/path/cycle_number.txt'
    mock_file = mock_open.return_value.__enter__.return_value
    
    # Establecer un valor inicial
    generator_instance.generate_files_call_count = 5
    
    generator_instance.save_cycle_number()
    
    # Verificar que se incrementó
    assert generator_instance.generate_files_call_count == 6
    
    # Verificar que se escribió el archivo con el valor correcto
    mock_open.assert_called_with('/mocked/path/cycle_number.txt', 'w')
    mock_file.write.assert_called_with('6')

def test_create_output_directory(generator_instance):
    # Test que verifica el formato correcto del directorio creado
    times_stamp = '20230101120000'
    call_count = 999  # Usar un número único para evitar conflictos

    result = generator_instance.create_output_directory(times_stamp, call_count)

    # Verificar que el directorio fue creado
    assert os.path.exists(result)
    
    # Verificar el formato correcto del directorio
    expected_format = f'cycle-{call_count}-{times_stamp}-noreport'
    assert expected_format in result
    
    # Verificar que termina con la estructura esperada
    assert result.endswith(f'results/devices/{expected_format}')
    
    # Verificar que contiene la ruta relativa correcta
    assert './../results/devices/' in result

    # Limpiar el directorio creado
    os.rmdir(result)

def test_generate_hash(generator_instance):
    result = generator_instance.generate_hash('test', 42, 'example')
    assert isinstance(result, int)


def test_generate_contentfile_unknown_mission(generator_instance):
    """Test generate_contentfile con una misión que no está en codes"""
    # Añadir temporalmente una misión sin código
    original_names = generator_instance.mission_instance._config_data['names'].copy()
    generator_instance.mission_instance._config_data['names'] = ['UnknownMission']

    result = generator_instance.generate_contentfile(1)

    # Restaurar
    generator_instance.mission_instance._config_data['names'] = original_names

    assert 'unknown' in result.content
    assert 'ID:' in result.content


def test_custom_content_without_unique_id():
    """Test CustomContent cuando unique_id es None"""
    from apolo_11.src.generator import CustomContent
    content = CustomContent(
        current_date='010123120000',
        mission_name='Test',
        device_type='Satellite',
        device_status='good',
        hash_value=123,
        unique_id=None
    )
    result = content.generate_content_string()
    assert 'ID:' not in result


def test_default_content_generate_string():
    """Test DefaultContent.generate_content_string"""
    from apolo_11.src.generator import DefaultContent
    content = DefaultContent(
        current_date='010123120000',
        mission_name='OrbitOne',
        device_type='Satellite',
        device_status='excellent',
        hash_value=12345
    )
    result = content.generate_content_string()
    assert 'Date: 010123120000' in result
    assert 'Mission: OrbitOne' in result
    assert 'Hash: 12345' in result


@patch('apolo_11.src.generator.os.makedirs')
@patch('builtins.open', create=True)
@patch('apolo_11.src.generator.Generator.load_cycle_number')
@patch('apolo_11.src.generator.Generator.save_cycle_number')
@patch('apolo_11.src.generator.Generator.create_output_directory')
@patch('apolo_11.src.generator.Generator.generate_contentfile')
@patch('apolo_11.src.generator.datetime')
def test_generate_files(mock_datetime, mock_generate_contentfile, mock_create_output_directory,
                       mock_save_cycle_number, mock_load_cycle_number, mock_open, mock_makedirs, generator_instance):
    """Test generate_files method with mocks to avoid real I/O
    
    Requirements: 5.1 - Test con mocks para evitar I/O real, verificar creación de archivos
    """
    # Setup mocks
    mock_datetime.now.return_value.strftime.return_value = '20230101120000'
    mock_create_output_directory.return_value = '/mocked/output/dir'
    
    # Mock generate_contentfile to return test data
    from apolo_11.src.generator import GeneratedFile
    mock_generate_contentfile.side_effect = [
        GeneratedFile('APLORBONE-0001.log', 'test content 1'),
        GeneratedFile('APLORBONE-0002.log', 'test content 2')
    ]
    
    # Mock file operations
    mock_file = mock_open.return_value.__enter__.return_value
    
    # Mock random.randint to return a fixed number of files
    with patch('apolo_11.src.generator.random.randint', return_value=2):
        generator_instance.generate_files(1, 5)
    
    # Verify load_cycle_number was called
    mock_load_cycle_number.assert_called_once()
    
    # Verify create_output_directory was called with timestamp and call count
    mock_create_output_directory.assert_called_once_with('20230101120000', generator_instance.generate_files_call_count)
    
    # Verify generate_contentfile was called for each file
    assert mock_generate_contentfile.call_count == 2
    mock_generate_contentfile.assert_any_call(1)
    mock_generate_contentfile.assert_any_call(2)
    
    # Verify files were written
    assert mock_open.call_count == 2
    mock_open.assert_any_call('/mocked/output/dir/APLORBONE-0001.log', 'w')
    mock_open.assert_any_call('/mocked/output/dir/APLORBONE-0002.log', 'w')
    
    # Verify file content was written
    mock_file.write.assert_any_call('test content 1')
    mock_file.write.assert_any_call('test content 2')
    
    # Verify save_cycle_number was called
    mock_save_cycle_number.assert_called_once()
