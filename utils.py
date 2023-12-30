import math
import numpy
import cv2


def vector_de_intensidades_equalize(archivo_imagen):
    imagen_1 = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    imagen_2 = cv2.equalizeHist(imagen_1)
    imagen_2 = cv2.resize(imagen_2, (15, 15), interpolation=cv2.INTER_AREA)
    descriptor_imagen = imagen_2.flatten()
    return descriptor_imagen

def vector_de_intensidades_omd(archivo_imagen):
    imagen_1 = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    imagen_2 = cv2.resize(imagen_1, (15, 15), interpolation=cv2.INTER_AREA)
    descriptor_imagen = imagen_2.flatten()
    posiciones = numpy.argsort(descriptor_imagen)
    for i in range(len(posiciones)):
        descriptor_imagen[posiciones[i]] = i
    return descriptor_imagen

def histograma_por_zona(archivo_imagen):
    # divisiones
    num_zonas_x = 4
    num_zonas_y = 4
    num_bins_por_zona = 9
    ecualizar = True
    # leer imagen
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)
    if ecualizar:
        imagen = cv2.equalizeHist(imagen)
    
    
    imagen_hists = numpy.full((imagen.shape[0], imagen.shape[1], 3), (200,255,200), dtype=numpy.uint8)
    # procesar cada zona
    descriptor = numpy.array([])
    for j in range(num_zonas_y):
        desde_y = int(imagen.shape[0] / num_zonas_y * j)
        hasta_y = int(imagen.shape[0] / num_zonas_y * (j+1))
        for i in range(num_zonas_x):
            desde_x = int(imagen.shape[1] / num_zonas_x * i)
            hasta_x = int(imagen.shape[1] / num_zonas_x * (i+1))
            # recortar zona de la imagen
            zona = imagen[desde_y : hasta_y, desde_x : hasta_x]
            # histograma de los pixeles de la zona
            histograma, limites = numpy.histogram(zona, bins=num_bins_por_zona, range=(0,255))
            # normalizar histograma (bins suman 1)
            histograma = histograma / numpy.sum(histograma)
            # agregar descriptor de la zona al descriptor global
            descriptor=numpy.append(descriptor,histograma)
    return descriptor


def angulos_en_zona(imgBordes, imgSobelX, imgSobelY):
    sobelX=imgSobelX[imgBordes>0]
    sobelY=imgSobelY[imgBordes>0]
    degrees=numpy.degrees(numpy.arctan(numpy.divide(sobelY,sobelX,where=sobelX!=0))) 
    return degrees 

def angulos_por_zona(archivo_imagen):
    # no mostró resultados relevantes, su mejor desempeño  
    # fue con GAMMA, sin embargo otros descritpores se desempeñaron mejor  
    
    num_zonas_x = 4
    num_zonas_y = 4
    num_bins_por_zona = 9
    threshold_magnitud_gradiente = 150
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)

    imagen = cv2.equalizeHist(imagen)
    imagen = cv2.GaussianBlur(imagen, (5,5), 0, 0)
    sobelX = cv2.Sobel(imagen, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
    sobelY = cv2.Sobel(imagen, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=3)
    magnitud = numpy.sqrt(numpy.square(sobelX) + numpy.square(sobelY))
    th, bordes = cv2.threshold(magnitud, threshold_magnitud_gradiente, 255, cv2.THRESH_BINARY)
    imagen_hists = numpy.full((imagen.shape[0], imagen.shape[1], 3), (200,210,255), dtype=numpy.uint8)

    descriptor = numpy.array([])

    for j in range(num_zonas_y):
        desde_y = int(imagen.shape[0] / num_zonas_y * j)
        hasta_y = int(imagen.shape[0] / num_zonas_y * (j+1))
        for i in range(num_zonas_x):
            desde_x = int(imagen.shape[1] / num_zonas_x * i)
            hasta_x = int(imagen.shape[1] / num_zonas_x * (i+1))
            angulos = angulos_en_zona(bordes[desde_y : hasta_y, desde_x : hasta_x],
                                      sobelX[desde_y : hasta_y, desde_x : hasta_x],
                                      sobelY[desde_y : hasta_y, desde_x : hasta_x])
            histograma, limites = numpy.histogram(angulos, bins=num_bins_por_zona, range=(-90,90))
            if numpy.sum(histograma) != 0:
                histograma = histograma / numpy.sum(histograma)
            descriptor=numpy.append(descriptor,histograma)   
        
    return descriptor

def concat_features(archivo_imagen):
    descriptor1=histograma_por_zona(archivo_imagen)
    descriptor2=vector_de_intensidades_omd(archivo_imagen)
    descriptor1=descriptor1*descriptor2.mean()/descriptor1.mean()
    con= numpy.concatenate((descriptor2,descriptor1)) 
    return con
