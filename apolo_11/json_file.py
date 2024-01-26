from datetime import datetime
import random
import hashlib
import json

class ContenidoArchivos:
    opciones_mision=["OrbitOne", "ColonyMoon", "VacMars", "GalaxyTwo","UNKN"]
    opciones_device_type=["Satelites", "Naves espaciales", "Vehículo espacial", 
                        "Pantallas y controles","Trajes termicos","Velocimetro","Sonda espacial",
                        "Laser infrarojo"]
    opciones_device_status=["excellent","good","warning","faulty","killed","unknown"]
        
    def __init__(self):
        self.date:str = datetime.now().strftime("%d%m%Y%H%M%S")
        self.mission:str = random.choice(ContenidoArchivos.opciones_mision)
        self.device_type:str = ""
        self.device_status:str = ""
        self.cadena_hash = self.date+self.mission+self.device_type+self.device_status
        self.hash:str = ""
        
        if self.mission == "UNKN":
            self.device_type = "unknown"
            self.device_status = "unknown"
            self.hash = "unknown" 
        else:
            self.device_type = random.choice(ContenidoArchivos.opciones_device_type)
            self.device_status = random.choice(ContenidoArchivos.opciones_device_status)        
            self.hash = hashlib.sha256(self.cadena_hash.encode()).hexdigest()
        
    def get_json(self):
        json_file = {}
        if self.mission == "UNKN":
            json_file = {"Date": self.date, "Mission": self.mission, "Device_type": self.device_type, 
                "Device_status": self.device_status, "ID": self.hash}
        else: 
            json_file = {"Date": self.date, "Mission": self.mission, "Device_type": self.device_type, 
            "Device_status": self.device_status, "ID": self.cadena_hash}
        print(type(json_file))
        with open('file_mission.log', "w") as fl:
            json_string = json.dumps(json_file, indent=4)
            fl.write(json_string)
        
        return json_string

    def get_file_name(self):
        
            pass
        
json_file=ContenidoArchivos()
print(json_file.get_json())

#este módulo crearía el bloque de archivos de una ejecución de 20 seg
