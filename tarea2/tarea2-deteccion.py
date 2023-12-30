# CC5213 - TAREA 2
# 28 de septiembre de 2023
# Alumno: [nombre]

import sys
import os.path
import queue
import numpy as np
import math
from constants import SAMPLE_RATE, SAMPLES_POR_VENTANA, SAMPLES_POR_SALTO, DIMENSION

class Evaluator():
    def __init__(self):
        self.previous=None
        self.is_full_seq=False    
        self.first_seq_found=False
        self.current_song=None
        self.current_radio=None
        self.current_init=None
        self.mismatches=0
        self.seq_time_data=list()   
        self.seq_mismatches_data=list()
        self.full_seq_data={"time_data":list(),"missmatches_data":list(),
                            "radio_ini":None,"radio_end":None,"radio_name":None,"song_name":None}
        
        # self.full_seq_time_data=list()
        # self.full_seq_missmatches_data=list()    
    # def find_sequences(self,,file):
    def add(self,radio_name,radio_time,song_name, song_time):
        if self.is_consecutive(song_name, song_time) and  self.current_song!=song_name:

            self.is_full_seq=True

            if  not self.first_seq_found:
                #preparing values for ending fist seq
                self.first_seq_found=True
                self.full_seq_data["radio_ini"]=self.previous["radio_time"]
                self.is_full_seq=False
            else:
                # get  values  for  current seq
                self.full_seq_data["song_name"]=self.current_song
                self.full_seq_data["radio_name"]=self.current_radio
                self.full_seq_data["time_data"]=self.seq_time_data
                self.full_seq_data["missmatches_data"]=self.seq_mismatches_data
                self.full_seq_data["radio_ini"]=self.current_init

            # update values for the next seq
            self.mismatches=0
            self.current_song=song_name
            self.current_radio=radio_name
            self.current_init=self.previous["radio_time"]
            self.seq_time_data=[self.previous["song_time"],song_time]
            self.seq_mismatches_data=[0,0]

        elif song_name==self.current_song:
            # adding values to the current seq
            self.is_full_seq=False
            self.seq_time_data.append(song_time)
            self.seq_mismatches_data.append(self.mismatches)
            self.full_seq_data["radio_end"]=radio_time
            self.mismatches=0
            self.set_previous(radio_name,radio_time,song_name,song_time)

        
        elif radio_name!=self.current_radio and self.current_radio!=None:
            self.is_full_seq=True
            # get  values  for  current seq
            self.full_seq_data["song_name"]=self.current_song
            self.full_seq_data["radio_name"]=self.current_radio
            self.full_seq_data["time_data"]=self.seq_time_data
            self.full_seq_data["missmatches_data"]=self.seq_mismatches_data
            self.full_seq_data["radio_ini"]=self.current_init
            # update values for the next seq
            self.first_seq_found=False
            self.mismatches=0
            self.current_song=None
            self.current_radio=radio_name
            self.set_previous(radio_name,radio_time,song_name,song_time)
        else:
            # skiping  this values
            self.is_full_seq=False
            self.set_previous(radio_name,radio_time,song_name,song_time)
            self.mismatches+=1
                        
    def calculate_score(self,factor=5):
        
        if self.full_seq_data["radio_end"]-self.full_seq_data["radio_ini"]<5:
            return 0,0
        
        mismatches=np.cumsum(np.array(self.full_seq_data["missmatches_data"]))
        x=np.arange(len(self.full_seq_data["time_data"]))+mismatches
        y=np.array(self.full_seq_data["time_data"])
        slope,residuals,_,_,_=np.polyfit(x,y,1,full=True)                
        residuals,=residuals/len(self.full_seq_data["time_data"])

        if abs(slope[0]-SAMPLES_POR_VENTANA/SAMPLE_RATE)<0.1:
            slope_factor=1
        else:               #1-(0.1-0.003)
            slope_factor=1-abs(slope[0]-SAMPLES_POR_VENTANA/SAMPLE_RATE)/ SAMPLES_POR_VENTANA/SAMPLE_RATE
        
        score =np.exp(-abs(slope[0]-SAMPLES_POR_VENTANA/SAMPLE_RATE)*factor)
        
        return score,slope[0]
    
    def is_consecutive(self,song_name, song_time):
        try:
            dif=song_time-self.previous["song_time"]
            if self.previous["song_name"]==song_name and  0<dif <=(SAMPLES_POR_VENTANA/SAMPLE_RATE)+0.01 :
                return True
        except TypeError:
            return False
        return False
    
    def set_previous(self,radio_name,radio_time ,song_name, song_time):
        self.previous={"radio_name":radio_name,"radio_time":radio_time,"song_name":song_name, "song_time":song_time}


def tarea2_deteccion(dir_resultados_knn, file_resultados_txt):
    if not os.path.isdir(dir_resultados_knn):
        print("ERROR: no existe directorio {}".format(dir_resultados_knn))
        sys.exit(1)
    elif os.path.exists(file_resultados_txt):
        print("ERROR: ya existe archivo {}".format(file_resultados_txt))
        sys.exit(1)
    # Implementar la deteccion
    #  1-leer resultados de knn en dir_resultados_knn
    with open(os.path.join(dir_resultados_knn, 'resultados_knn.txt'), 'r') as f:
        with open(file_resultados_txt, 'w') as f2:
            ev = Evaluator()            
            for linea in f:
                [radio, radio_tiempo, cancion,cancion_tiempo] = linea.removesuffix("\r\n").split('\t')
                #  2-buscar secuencias similares entre audios
                ev.add(radio,float(radio_tiempo),cancion, float(cancion_tiempo))                
                if ev.is_full_seq:
                    score,slope=ev.calculate_score()
                #  4-escribir en file_resultados_txt las detecciones encontradas
                    if score>0.75:
                        f2.write("{}\t{}\t{}\t{}\t{}\r\n".format(
                                ev.full_seq_data["radio_name"].removesuffix(".40960.wav"), ev.full_seq_data["radio_ini"], ev.full_seq_data["radio_end"]-ev.full_seq_data["radio_ini"], ev.full_seq_data["song_name"].removesuffix(".40960.wav"),score))                    
            

if len(sys.argv) < 3:
    print("Uso: {} [dir_resultados_knn] [file_resultados_txt]".format(
        sys.argv[0]))
    sys.exit(1)

dir_resultados_knn = sys.argv[1]
file_resultados_txt = sys.argv[2]

tarea2_deteccion(dir_resultados_knn, file_resultados_txt)
