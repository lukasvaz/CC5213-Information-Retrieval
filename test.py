import numpy
import cv2
import os

def agregar_texto(imagen, texto):
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.7
    fontThickness = 2
    position = (10, 30)
    fontColor = (50,50,50)
    cv2.putText(imagen, texto, position, fontFace, fontScale, fontColor, fontThickness, cv2.LINE_AA)

def mostrar_imagen(window_name, imagen, texto):
    MIN_WIDTH, MAX_WIDTH = 200, 800
    MIN_HEIGHT, MAX_HEIGHT = 200, 800
    if imagen.shape[0] > MAX_HEIGHT or imagen.shape[1] > MAX_WIDTH:
        # reducir tamaño
        fh = MAX_HEIGHT / imagen.shape[0]
        fw = MAX_WIDTH / imagen.shape[1]
        escala = min(fh, fw)
        imagen = cv2.resize(imagen, (0,0), fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    elif imagen.shape[0] < MIN_HEIGHT or imagen.shape[1] < MIN_WIDTH:
        # aumentar tamaño
        fh = MIN_HEIGHT / imagen.shape[0]
        fw = MIN_WIDTH / imagen.shape[1]
        escala = max(fh, fw)
        imagen = cv2.resize(imagen, (0,0), fx=escala, fy=escala, interpolation=cv2.INTER_NEAREST)
    # incluir el nombre sobre la imagen
    agregar_texto(imagen, texto)
    # mostrar en pantalla con el nomnbre
    cv2.imshow(window_name, imagen)

#funcion que retorna un vector
def vector_de_intensidades(archivo_imagen):
    imagen_1 = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    imagen_2 = cv2.resize(imagen_1, (20, 20), interpolation=cv2.INTER_AREA)
    # flatten convierte una matriz de nxm en un array de largo nxm
    descriptor_imagen = imagen_2.flatten()
    # mostrar una visualizacion del cálculo del descriptor
    global mostrar_imagenes
    if mostrar_imagenes:
        nombre = os.path.basename(archivo_imagen)
        mostrar_imagen("imagen_1", imagen_1, nombre)
        mostrar_imagen("imagen_2", imagen_2, nombre)
        cv2.waitKey()
        cv2.destroyAllWindows()
    return descriptor_imagen

def vector_de_intensidades_equalize(archivo_imagen):
    imagen_1 = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    imagen_2 = cv2.equalizeHist(imagen_1)
    imagen_2 = cv2.resize(imagen_2, (4, 4), interpolation=cv2.INTER_AREA)
    descriptor_imagen = imagen_2.flatten()
    global mostrar_imagenes
    if mostrar_imagenes:
        mostrar_imagen("imagen_1", imagen_1, archivo_imagen)
        mostrar_imagen("imagen_2", imagen_2, "")
        cv2.waitKey()
        cv2.destroyAllWindows()
    return descriptor_imagen

def vector_de_intensidades_omd(archivo_imagen):
    imagen_1 = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    imagen_2 = cv2.resize(imagen_1, (15, 15), interpolation=cv2.INTER_AREA)
    descriptor_imagen = imagen_2.flatten()
    posiciones = numpy.argsort(descriptor_imagen)
    for i in range(len(posiciones)):
        descriptor_imagen[posiciones[i]] = i
    return descriptor_imagen

def calcular_descriptores(metodo_descriptor, imagenes_dir):
    lista_nombres = []
    matriz_descriptores = []    
    for nombre in os.listdir(imagenes_dir):
        archivo_imagen = "{}/{}".format(imagenes_dir, nombre)
        descriptor_imagen = metodo_descriptor(archivo_imagen)
        # agregar descriptor a la matriz de descriptores
        if len(matriz_descriptores) == 0:
            matriz_descriptores = descriptor_imagen
        else:
            matriz_descriptores = numpy.vstack([matriz_descriptores, descriptor_imagen])
        # agregar nombre del archivo a la lista de nombres
        lista_nombres.append(nombre)
    return lista_nombres, matriz_descriptores

def imprimir_matriz_descriptores(nombres, descriptores):
    print("matriz de descriptores (filas={}, columnas={})".format(descriptores.shape[0], descriptores.shape[1]))
    numpy.set_printoptions(precision=3, floatmode="fixed", suppress=True, threshold=15, edgeitems=5, linewidth=100)
    print("filas de la matriz:")
    with open('./resultados/res1.txt','w') as f:
        for i in range(len(nombres)):
            print("  {}) {:>15s} {}".format(i, nombres[i], descriptores[i]))
            f.write("  {}) {:>15s} {}".format(i, nombres[i], descriptores[i]))
        print()

