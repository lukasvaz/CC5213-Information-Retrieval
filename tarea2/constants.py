
SAMPLE_RATE = 40960
# SAMPLE_QUALITY=44100  # calidad del audio (44100 es HD, se puede bajar)
# tamaño de la ventana a la que se calcula un descriptor MFCC (usualmente unas 5 a 10 por segundo)
SAMPLES_POR_VENTANA = 4096
# se puede proabr con un  el salto es menor al tamaño de la ventana para que haya traslape entre ventanas
SAMPLES_POR_SALTO = 4096
DIMENSION = 41  # largo del descriptor MFCC (usualmente entre 10 a 64)
