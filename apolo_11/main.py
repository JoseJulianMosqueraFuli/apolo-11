from core import Simulator

#! La tarea de este script es leer el yaml y ejecutar el Simulador

def main():
    # TODO: Leer archivo de configuracion para obtener frecuencia y cantidad de archivos
    frequency = 20
    min_file_generation = 1
    max_file_generation = 100
    sim = Simulator(frequency, min_file_generation, max_file_generation)
    sim.run()
    # TODO: Decidir si el simulador y analista corren a la vez, o bajo que criterio corre el analista



if __name__ == '__main__':
    main()