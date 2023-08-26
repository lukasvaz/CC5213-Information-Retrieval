# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# 15 de agosto de 2023
# Alumno: [nombre]

import sys
import os.path

def tarea1_buscar(dir_input_imagenes_Q, dir_input_descriptores_R, file_output_resultados):
    if not os.path.isdir(dir_input_imagenes_Q):
        print("ERROR: no existe directorio {}".format(dir_input_imagenes_Q))
        sys.exit(1)
    elif not os.path.isdir(dir_input_descriptores_R):
        print("ERROR: no existe directorio {}".format(dir_input_descriptores_R))
        sys.exit(1)
    elif os.path.exists(file_output_resultados):
        print("ERROR: ya existe archivo {}".format(file_output_resultados))
        sys.exit(1)
    # Implementar la tarea:
    #  1-leer imágenes en dir_input_imagenes_Q y calcular descriptores cada imagen
    #    for nombre in os.listdir(dir_input_imagenes_Q):
    #        if not nombre.endswith(".jpg"):
    #            continue
    #        archivo_imagen = "{}/{}".format(dir_input_imagenes_Q, nombre)
    
    #  2-leer descriptores de R de dir_input_descriptores_R
    #  3-para cada descriptor q localizar el mas cercano en R
    #  4-escribir en file_output_resultados haciendo print() con el formato: 
    #    with open(file_output_resultados, 'w') as f:
    #        for ....
    #            print("{}\t{}\t{}".format(imagen_q, imagen_r, distancia), file=f)
    # borrar la siguiente linea
    print("ERROR: no implementado!")


# inicio de la tarea
if len(sys.argv) < 4:
    print("Uso: {} [dir_input_imagenes_Q] [dir_input_descriptores_R] [file_output_resultados]".format(sys.argv[0]))
    sys.exit(1)

dir_input_imagenes_Q = sys.argv[1]
dir_input_descriptores_R = sys.argv[2]
file_output_resultados = sys.argv[3]

tarea1_buscar(dir_input_imagenes_Q, dir_input_descriptores_R, file_output_resultados)
