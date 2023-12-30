# CC5213 - TAREA 2
# 28 de septiembre de 2023
# Alumno: [nombre]
import scipy
import sys
import os.path
import pickle
from utils import Ventana
import numpy as np
def tarea2_busqueda(dir_descriptores_q, dir_descriptores_r, dir_resultados_knn):
    if not os.path.isdir(dir_descriptores_q):
        print("ERROR: no existe directorio {}".format(dir_descriptores_q))
        sys.exit(1)
    elif not os.path.isdir(dir_descriptores_r):
        print("ERROR: no existe directorio {}".format(dir_descriptores_r))
        sys.exit(1)
    elif os.path.exists(dir_resultados_knn):
        print("ERROR: ya existe archivo {}".format(dir_resultados_knn))
        sys.exit(1)
    # Implementar la busqueda
    #  1-leer descriptores de Q de dir_descriptores_q
    with open(os.path.join(dir_descriptores_q,'descriptores.pkl'), 'rb') as f:
        descriptores_q,ventanas_q = pickle.load(f)
        
    #  2-leer descriptores de R de dir_descriptores_r
    with open(os.path.join(dir_descriptores_r,'descriptores.pkl'), 'rb') as f:
        descriptores_r, ventanas_r = pickle.load(f)
    #  3-para cada descriptor q localizar el mas cercano en R
    #     usar cdist o usar indices de busqueda eficiente    
    matriz_distancias = scipy.spatial.distance.cdist(descriptores_q , descriptores_r, metric='euclidean')
    posiciones_min = np.argmin(matriz_distancias, axis=1)
    # minimos = np.amin(matriz_distancias, axis=1)
    #  4-crear dir_resultados_knn
    os.makedirs(dir_resultados_knn, exist_ok=True)
    #  5-escribir los knn en dir_resultados_knn
    with open(os.path.join(dir_resultados_knn,'resultados_knn.txt'), 'w') as f:
        for i,_ in enumerate(ventanas_q):
            f.write("{}\t{}\t{}\t{}\r\n".format(ventanas_q[i].nombre_archivo, ventanas_q[i].segundos_desde,\
                                            ventanas_r[posiciones_min[i]].nombre_archivo, ventanas_r[posiciones_min[i]].segundos_desde))

    #    incluir tambien los tiempos que representa cada ventana de q y r
    # borrar la siguiente linea


# inicio de la tarea
if len(sys.argv) < 4:
    print("Uso: {} [dir_descriptores_q] [dir_descriptores_r] [dir_resultados_knn]".format(sys.argv[0]))
    sys.exit(1)

dir_descriptores_q = sys.argv[1]
dir_descriptores_r = sys.argv[2]
dir_resultados_knn = sys.argv[3]

tarea2_busqueda(dir_descriptores_q, dir_descriptores_r, dir_resultados_knn)
