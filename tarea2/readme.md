## Sistema Operativo 
Ubuntu 22.04.3 LTS

## Explicación Alto nivel
#### extractor.py
Para  mejorar   los  resultados  en extractor.py  se cambia  la  dimensión  de  los descriptores a 41,  y se eliminan  las primeras  5 dimensiones de cada  uno.

#### deteccion.py
El procesamiento seguido  en deteccion.py es el siguiente:
 -Si  se encuentran dos ventanas  de  la  misma  canción  consecutivas  y  que cumplan  con la diferecnia de tiempo correspondiente , se  considera  que se está  dentro del fragmento de una canción.
 -Si nos  encontramos dentro del  fragmento de  una canción se agrega cada aparición  de la canción al fragmento (no necesariamente apariciones consecutivas). 

 -El fragmento  termina  en la  última aparición de la canción antes  de  otra aparicion consecutiva de  una  canción diferente,aquí  comienza otro fragmento.

 -El score es  una  regresión lineal  de los tiempos del fraagmento, si la pendiente es cercana  a  SAMPLES_POR_VENTANA/SAMPLE_RATE  el score es alto.