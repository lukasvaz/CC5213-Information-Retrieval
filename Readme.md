# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
## Profesor: Juan Manuel Barrios 
## 15 de agosto de 2023

# Tarea 1

Para la tarea 1 debe crear dos programas:

  * `tarea1-indexar.py`
     Recibe dos parámetros por la línea de comandos:
	    1. La carpeta de entrada con imágenes originales R.
        2. Una carpeta de salida donde guardar los descriptores de R.
   
  * `tarea1-buscar.py`
     Recibe tres parámetros por la línea de comandos:
	   1. La carpeta de entrada con imágenes de consulta Q.
	   2. La carpeta con descriptores de R.
	   3. Un nombre de archivo de salida para guardar el resultado de buscar Q en R.

El archivo de salida debe tener un formato de 3 columnas separadas por un tabulador. En cada
fila debe tener el nombre de una imagen de Q, el nombre de la imagen de R más cercana y la
distancia entre ambas imágenes.

Por ejemplo, un posible archivo de resultados sería este:

q0001.jpg	r0432.jpg	610.2
q0002.jpg	r0231.jpg	126.1
[......]
q2441.jpg	r0156.jpg	11.5
q2442.jpg	r1849.jpg	119.5


Para probar su tarea debe usar el programa de evaluación:

  `python evaluarTarea1.py`

Este programa llamará su tarea con todos los datasets y mostrará el resultado obtenido y la nota.

Para probar su tarea con solo un dataset ejecutar:

  `python evaluarTarea1.py a`

Su tarea no puede demorar más de 15 minutos (900 segundos) para evaluar en cada dataset.
