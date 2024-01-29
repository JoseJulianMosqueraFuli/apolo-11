import os
import pytest
from datetime import datetime
from unittest.mock import patch
from apolo_11.src.generator import Generator

@pytest.fixture
def generator_instance():
    return Generator()

def test_generate_device_folder(generator_instance, tmpdir):
    output_dir = os.path.join(str(tmpdir), 'results', 'devices')
    generator_instance.generate_device_folder(str(tmpdir))
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
    filename, content = generator_instance.generate_contentfile(file_number)

    assert filename.startswith('APL')
    assert filename.endswith('.log')
    assert 'Date: 010123120000' in content  # Ensure date is formatted as expected
    assert 'Mission: ' in content
    assert 'Device Type: ' in content
    assert 'Device Status: ' in content
    assert 'Hash: ' in content

def test_load_cycle_number(generator_instance, tmpdir):
    cycle_number_file = os.path.join(str(tmpdir), 'cycle_number.txt')

    # When the file exists
    with open(cycle_number_file, 'w') as file:
        file.write('42')

    generator_instance.load_cycle_number()
    assert generator_instance.generate_files_call_count == 42

    # When the file doesn't exist
    os.remove(cycle_number_file)
    generator_instance.load_cycle_number()
    assert generator_instance.generate_files_call_count == 0

def test_save_cycle_number(generator_instance, tmpdir):
    cycle_number_file = os.path.join(str(tmpdir), 'cycle_number.txt')

    # Save cycle number
    generator_instance.generate_files_call_count = 42
    generator_instance.save_cycle_number()

    # Read the saved cycle number from the file
    with open(cycle_number_file, 'r') as file:
        saved_cycle_number = int(file.read().strip())

    assert saved_cycle_number == 42

def test_create_output_directory(generator_instance, tmpdir):
    times_stamp = '20230101120000'
    generator_instance.generate_files_call_count = 42

    expected_output_directory = os.path.join(str(tmpdir), 'results', 'devices', f'cycle-42-{times_stamp}-noreport')

    result = generator_instance.create_output_directory(times_stamp, generator_instance.generate_files_call_count)

    assert result == expected_output_directory
    assert os.path.exists(expected_output_directory)

def test_generate_hash(generator_instance):
    result = generator_instance.generate_hash('test', 42, 'example')
    assert isinstance(result, int)
