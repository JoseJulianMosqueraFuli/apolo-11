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

        # Verificar que se hayan generado las carpetas de respaldo y reportes
        backups_dir = os.path.join(tmp_dir, 'backups')
        reports_dir = os.path.join(tmp_dir, 'reports')
        assert os.path.exists(backups_dir)
        assert os.path.exists(reports_dir)

        # Verificar que se hayan movido las carpetas correctas a la carpeta de respaldo
        backup_subdirs = os.listdir(backups_dir)
        assert 'cycle-0' in backup_subdirs
        assert 'cycle-1' in backup_subdirs

        # Verificar que se haya generado el archivo de estadísticas
        stats_files = os.listdir(reports_dir)
        assert any(stats_file.startswith('APLSTATS-REPORT') for stats_file in stats_files)

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
