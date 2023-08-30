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


def angulos_en_zona(imgBordes, imgSobelX, imgSobelY):
    # calcular angulos de la zona
    # recorre pixel por pixel (muy lento!)
    angulos = []
    for row in range(imgBordes.shape[0]):
        for col in range(imgBordes.shape[1]):
            # si es un pixel de borde (magnitud del gradiente > umbral)
            if imgBordes[row][col] > 0:
                dx = imgSobelX[row][col]
                dy = imgSobelY[row][col]
                angulo = 90
                if dx != 0:
                    # un numero entre -180 y 180
                    angulo = math.degrees(numpy.arctan(dy/dx))
                    # dejar en el rango -90 a 90
                    if angulo <= -90:
                        angulo += 180
                    if angulo > 90:
                        angulo -= 180
                angulos.append(angulo)
    return angulos

def angulos_en_zona2(imgBordes, imgSobelX, imgSobelY):
    sobelX=imgSobelX[imgBordes>0]
    sobelY=imgSobelY[imgBordes>0]
    degrees=numpy.degrees(numpy.arctan(numpy.divide(sobelY,sobelX,where=sobelX!=0))) 
    return degrees 

def angulos_por_zona(archivo_imagen):
    # divisiones
    num_zonas_x = 4
    num_zonas_y = 4
    num_bins_por_zona = 9
    threshold_magnitud_gradiente = 150
    # leer imagen
    imagen = cv2.imread(archivo_imagen, cv2.IMREAD_GRAYSCALE)

    # calcular filtro de sobel (usar cv2.GaussianBlur para borrar ruido)
    imagen = cv2.equalizeHist(imagen)
    imagen = cv2.GaussianBlur(imagen, (5,5), 0, 0)
    sobelX = cv2.Sobel(imagen, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
    sobelY = cv2.Sobel(imagen, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=3)
    magnitud = numpy.sqrt(numpy.square(sobelX) + numpy.square(sobelY))
    th, bordes = cv2.threshold(magnitud, threshold_magnitud_gradiente, 255, cv2.THRESH_BINARY)
    imagen_hists = numpy.full((imagen.shape[0], imagen.shape[1], 3), (200,210,255), dtype=numpy.uint8)

    # procesar cada zona
    descriptor = numpy.array([])

    for j in range(num_zonas_y):
        desde_y = int(imagen.shape[0] / num_zonas_y * j)
        hasta_y = int(imagen.shape[0] / num_zonas_y * (j+1))
        for i in range(num_zonas_x):
            desde_x = int(imagen.shape[1] / num_zonas_x * i)
            hasta_x = int(imagen.shape[1] / num_zonas_x * (i+1))
            # calcular angulos de la zona
            angulos = angulos_en_zona2(bordes[desde_y : hasta_y, desde_x : hasta_x],
                                      sobelX[desde_y : hasta_y, desde_x : hasta_x],
                                      sobelY[desde_y : hasta_y, desde_x : hasta_x])
            # histograma de los angulos de la zona
            histograma, limites = numpy.histogram(angulos, bins=num_bins_por_zona, range=(-90,90))
            # normalizar histograma (bins suman 1)
            if numpy.sum(histograma) != 0:
                histograma = histograma / numpy.sum(histograma)
            # agregar descriptor de la zona al descriptor global
            descriptor=numpy.append(descriptor,histograma)   
        
    return descriptor

