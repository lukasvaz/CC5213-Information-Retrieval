# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# 15 de agosto de 2023
# Alumno: [nombre]

import sys
import os.path
import cv2
import numpy
from test import vector_de_intensidades_omd

def tarea1_indexar(dir_input_imagenes_R, dir_output_descriptores_R):
    if not os.path.isdir(dir_input_imagenes_R):
        print("ERROR: no existe directorio {}".format(dir_input_imagenes_R))
        sys.exit(1)
    elif os.path.exists(dir_output_descriptores_R):
        print("ERROR: ya existe directorio {}".format(dir_output_descriptores_R))
        sys.exit(1)
    
    
    # Implementar la tarea:
    #  1-leer imágenes en dir_input_imagenes_R y calcular descriptores cada imagen
    descriptores=dict()
    for nombre in os.listdir(dir_input_imagenes_R):
        if not nombre.endswith(".jpg"):
            continue
        archivo_imagen = "{}/{}".format(dir_input_imagenes_R, nombre)
        descriptores[nombre]=vector_de_intensidades_omd(archivo_imagen)

    #  3-escribir en dir_output_descriptores_R los descriptores calculados (crear uno o más archivos)
    os.makedirs(dir_output_descriptores_R, exist_ok=True)
    archivo_salida = "{}/{}".format(dir_output_descriptores_R, "descriptores.data")
    with open(archivo_salida,"w") as f:
        for nombre,descriptor in descriptores.items(): 
            f.write("{}\t{}\n".format(nombre, descriptor))
    
# inicio de la tarea
if len(sys.argv) < 3:
    print("Uso: {} [dir_input_imagenes_R] [dir_output_descriptores_R]".format(sys.argv[0]))
    sys.exit(1)

dir_input_imagenes_R = sys.argv[1]
dir_output_descriptores_R = sys.argv[2]

tarea1_indexar(dir_input_imagenes_R, dir_output_descriptores_R)
