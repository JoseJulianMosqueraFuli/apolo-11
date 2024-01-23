from json_file import Component

#! La funcion de este codigo es crear n cantidad de archivos segun el parametro files_size que se le entreguen
# ? Revisar si hay que adicionar logica de cancelacion o no...


class Generator:
    def __init__(self, files_size: int):
        self.files_size = files_size

    def run(self):
        for _ in range(self.files_size):
            model_object = Component()
            self._create_json_file(model_object)

    def _create_json_file(self, model_object: Component):
        print(model_object.get_json())