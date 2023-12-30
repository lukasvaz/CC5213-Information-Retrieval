# CC5213 - TAREA 2
# 28 de septiembre de 2023
# Alumno: [nombre]

import sys
import os.path
import subprocess
import librosa
import pickle
import tempfile
import numpy as np
from utils import Ventana   
from  constants import SAMPLE_RATE, SAMPLES_POR_VENTANA, SAMPLES_POR_SALTO, DIMENSION

def lista_ventanas(nombre_archivo, numero_descriptores, sample_rate, samples_por_ventana):
    # tantas ventanas como numero de descriptores
    tiempos = []
    for i in range(0, samples_por_ventana * numero_descriptores, samples_por_ventana):
        # tiempo de inicio de la ventana
        segundos_desde = i / sample_rate
        # tiempo de fin de la ventana
        segundos_hasta = (i + samples_por_ventana - 1) / sample_rate
        # crear objeto
        v = Ventana(nombre_archivo, segundos_desde, segundos_hasta)
        # agregar a la lista
        tiempos.append(v)
    return tiempos

def convertir_a_wav(archivo_audio, sample_rate, dir_temporal):
    archivo_wav = "{}/{}.{}.wav".format(dir_temporal,
                                        os.path.basename(archivo_audio), sample_rate)
    # verificar si ya esta creado
    if os.path.isfile(archivo_wav):
        return archivo_wav
    comando = ["ffmpeg", "-i", archivo_audio, "-ac",
               "1", "-ar", str(sample_rate), archivo_wav,"-loglevel","quiet"]
    proc = subprocess.run(comando, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise Exception("Error ({}) en comando: {}".format(
            proc.returncode, " ".join(comando)))
    return archivo_wav



def calcular_descriptores_mfcc(archivo_wav, sample_rate, samples_por_ventana, samples_salto, dimension):
    # leer audio
    samples, sr = librosa.load(archivo_wav, sr=None)
    # calcular MFCC
    mfcc = librosa.feature.mfcc(
        y=samples, sr=sr, n_mfcc=dimension, n_fft=samples_por_ventana, hop_length=samples_salto)
    # convertir a descriptores por fila
    descriptores = mfcc.transpose()
    # usualmente es buena idea borrar la(s) primera(s) columna(s)
    return descriptores

def tarea2_extractor(dir_audios, dir_descriptores):
    if not os.path.isdir(dir_audios):
        print("ERROR: no existe directorio {}".format(dir_audios))
        sys.exit(1)
    elif os.path.exists(dir_descriptores):
        print("ERROR: ya existe directorio {}".format(dir_descriptores))
        sys.exit(1)
    # Implementar la tarea con los siguientes pasos:
    #  1-leer archivos de audio .m4a en dir_audios
    archivos = [os.path.join(dir_audios, x) for x in os.listdir(dir_audios)]
    #  2-crear dir_descriptores
    os.makedirs(dir_descriptores, exist_ok=True)
    #  3-cada audio convertirlo a wav con ffmpeg
    archivos_wav = []    
    with tempfile.TemporaryDirectory() as temp_dir:
        for x in archivos:
            convertir_a_wav(x, SAMPLE_RATE, temp_dir)
        #  4-cargar cada archivo wav
        archivos_wav = [x for x in os.listdir(temp_dir)]
        #  5-calcular descriptores (ver material)
        descriptores = np.array([])
        ventanas=[]
        for i,archivo in enumerate(archivos_wav):
            descriptor=calcular_descriptores_mfcc(os.path.join(
                temp_dir, archivo), SAMPLE_RATE, SAMPLES_POR_VENTANA, SAMPLES_POR_SALTO, DIMENSION)
            descriptor=descriptor[::,5::]
            if i==0:
                descriptores=descriptor
                ventanas.extend(lista_ventanas(os.path.basename(archivo),descriptor.shape[0],SAMPLE_RATE,SAMPLES_POR_VENTANA))
            else:
                descriptores=np.vstack((descriptores,descriptor))
                ventanas.extend(lista_ventanas(os.path.basename(archivo),descriptor.shape[0],SAMPLE_RATE,SAMPLES_POR_VENTANA))

    #  6-escribir descriptores de cada audio en dir_descriptores
    with open(os.path.join(dir_descriptores,'descriptores.pkl'), 'wb') as f:
        pickle.dump((descriptores,ventanas), f)

# inicio de la tarea
if len(sys.argv) < 3:
    print("Uso: {} [dir_audios] [dir_descriptores]".format(sys.argv[0]))
    sys.exit(1)

dir_audios = sys.argv[1]
dir_descriptores = sys.argv[2]

tarea2_extractor(dir_audios, dir_descriptores)