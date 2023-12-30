class Ventana:
    def __init__(self, nombre_archivo, segundos_desde, segundos_hasta):
        self.nombre_archivo = nombre_archivo
        self.segundos_desde = segundos_desde
        self.segundos_hasta = segundos_hasta
    def __str__(self):
        return "{} [{:6.3f}-{:6.3f}]".format(self.nombre_archivo, self.segundos_desde, self.segundos_hasta)
