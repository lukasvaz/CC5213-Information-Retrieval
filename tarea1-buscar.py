# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# 15 de agosto de 2023
# Alumno: [nombre]

import sys
import os.path
import scipy
import numpy as np
from test import vector_de_intensidades_omd

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
    nombres_Q=[]
    descriptores_Q=[]
    for nombre in os.listdir(dir_input_imagenes_Q):
        if not nombre.endswith(".jpg"):
            continue
        archivo_imagen = "{}/{}".format(dir_input_imagenes_Q, nombre)
        nombres_Q.append(nombre)
        descriptores_Q.append(vector_de_intensidades_omd(archivo_imagen))

    #  2-leer descriptores de R de dir_input_descriptores_R
    nombres_R=[]
    descriptores_R=[]
    with open(os.path.join(dir_input_descriptores_R,"descriptores.data")) as f:
        descriptor_data=""
        for line  in f:
            descriptor_data+=line
            if "]" in descriptor_data:
                descriptor_data=descriptor_data.strip("\n").split("\t")
                nombres_R.append(descriptor_data[0])
                descriptores_R.append(np.array(descriptor_data[1].strip("[]").split(),dtype='uint8'))
                descriptor_data=""
    #  3-para cada descriptor q localizar el mas cercano en R
    distance_matrix=scipy.spatial.distance.cdist(descriptores_Q,descriptores_R, 'canberra')            
    resultados=dict()
    for q_i in range(distance_matrix.shape[0]):
        distancia=distance_matrix[q_i].min()
        index=np.where(distance_matrix[q_i]==distancia)[0][0]
        resultados[nombres_Q[q_i]]=[nombres_R[index],distancia]        
    
    # 4-escribir en file_output_resultados haciendo print() con el formato: 
    with open(file_output_resultados, 'w') as f:
        for key in resultados.keys():
            print("{}\t{}\t{}".format(key, resultados[key][0], resultados[key][1]), file=f)
    
    
# inicio de la tarea
if len(sys.argv) < 4:
    print("Uso: {} [dir_input_imagenes_Q] [dir_input_descriptores_R] [file_output_resultados]".format(sys.argv[0]))
    sys.exit(1)

dir_input_imagenes_Q = sys.argv[1]
dir_input_descriptores_R = sys.argv[2]
file_output_resultados = sys.argv[3]

tarea1_buscar(dir_input_imagenes_Q, dir_input_descriptores_R, file_output_resultados)
