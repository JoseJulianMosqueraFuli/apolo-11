import os

class Folders:
    def __init__(self, path_proyecto):
        self.path_proyecto = path_proyecto

    def create_folder(self, folder_name):
        path_folder = os.path.join(self.path_proyecto, folder_name)

        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
        else:
            print(f'La carpeta "{folder_name}" ya existe en {self.path_proyecto}')

    def create_folders(self, simulaciones):
        self.create_folder('devices')
        self.create_folder('backups')
        self.create_folder('reportes')
        devices_path = os.path.join(self.path_proyecto, 'Devices')
        
        for i in range(1, simulaciones + 1):
            simulacion_name = f'Simulación {i}'
            self.create_folder(os.path.join(devices_path, simulacion_name))
            
path_apolo11 = os.path.dirname(os.path.abspath(__file__))
simulaciones = int(input("Ingrese la cantidad de simulaciones por ejecución: "))

folders = Folders(path_apolo11)
folders.create_folders(simulaciones)