# CC5213 - TAREA 1 - RECUPERACIÓN DE INFORMACIÓN MULTIMEDIA
# Programa de evaluación de la Tarea 1
# autor: Juan Manuel Barrios
# 15 de agosto de 2023

import sys
import subprocess
import os
import numpy
import shutil
import time

def get_filename(filepath):
    name = filepath.lower().strip()
    if name.rfind('/') >= 0:
        name = name[name.rfind('/') + 1:]
    if name.rfind('\\') >= 0:
        name = name[name.rfind('\\') + 1:]
    return name


class GT:
    def __init__(self, imagen_q, tipo, imagen_r):
        self.imagen_q = imagen_q
        self.tipo = tipo
        self.imagen_r = imagen_r


class GroudTruth:
    def __init__(self):
        self.lista = list()
        self.gt_por_query = dict()
        self.total_por_tipo = dict()
        self.num_queries = 0

    def leer_archivo_gt(self, filename):
        if not os.path.isfile(filename):
            print("ERROR: No existe {}".format(filename))
            sys.exit(1)
        with open(filename) as f:
            for linea in f:
                linea = linea.rstrip("\r\n")
                if linea == "" or linea.startswith("#"):
                    continue
                partes = linea.split()
                if len(partes) != 3:
                    print("{}: archivo GT invalido".format(filename))
                    sys.exit(1)
                gt = GT(partes[0], partes[1], partes[2])
                self.lista.append(gt)
                self.gt_por_query[gt.imagen_q] = gt
                if gt.imagen_r != "-":
                    self.total_por_tipo[gt.tipo] = self.total_por_tipo.get(gt.tipo, 0) + 1
                    self.num_queries += 1
        if len(self.lista) != 4347:
            print("{}: archivo GT invalido ({} queries)".format(filename, len(self.lista)))
            sys.exit(1)

    def buscar_gt(self, imagen_q):
        if imagen_q not in self.gt_por_query:
            return None
        return self.gt_por_query[imagen_q]

    def total_queries(self):
        return self.num_queries


class Deteccion:
    def __init__(self, linea, imagen_q, imagen_r, distancia):
        self.linea = linea
        self.imagen_q = get_filename(imagen_q)
        self.imagen_r = get_filename(imagen_r)
        self.distancia = distancia


class Detecciones:
    def __init__(self):
        self.lista = list()

    def leer_archivo_detecciones(self, filename):
        if not os.path.isfile(filename):
            print("ERROR: No existe {}".format(filename))
            sys.exit(1)
        cont_lineas = 0
        with open(filename) as f:
            for linea in f:
                cont_lineas += 1
                try:
                    linea = linea.rstrip("\r\n")
                    if linea == "" or linea.startswith("#"):
                        continue
                    partes = linea.split()
                    if len(partes) != 3:
                        print("{}: Formato incorrecto (se esperan 3 columnas)".format(filename))
                        sys.exit(1)
                    det = Deteccion(linea, partes[0], partes[1], float(partes[2]))
                    if det.distancia < 0:
                        print("{}: Formato incorrecto (distancia={})".format(filename, det.distancia))
                        sys.exit(1)
                    self.lista.append(det)
                except Exception as ex:
                    print("{} (linea {}): {}".format(filename, cont_lineas, ex))
                    sys.exit(1)
        print("{} detecciones en {}".format(len(self.lista), filename))


class Metricas:
    def __init__(self):
        self.correctas = 0
        self.incorrectas = 0
        self.ignoradas = 0
        self.duplicadas = 0
        self.precision = 0
        self.recall = 0
        self.f1 = 0
        self.correcta_por_tipo = dict()
        self.recall_por_tipo = dict()
        self.threshold = None

    def get_resultado_por_tipo(self):
        val = ""
        for tipo in self.recall_por_tipo:
            val += "      {:12s}={:4} correctas ({:.0f}%)\n".format(tipo,
                                                                    self.correcta_por_tipo[tipo],
                                                                    100 * self.recall_por_tipo[tipo])
        return val

    def get_umbral(self):
        return "umbral {:7.3f}".format(self.threshold)

    def get_metricas1(self):
        val = "respuestas={}".format(self.ignoradas + self.duplicadas + self.correctas + self.incorrectas)
        val += " correctas={}".format(self.correctas)
        val += " incorrectas={}".format(self.incorrectas)
        if self.duplicadas > 0:
            val += " duplicadas={}".format(self.duplicadas)
        if self.ignoradas > 0:
            val += " ignoradas={}".format(self.ignoradas)
        return val

    def get_metricas2(self):
        return "precision={:.3f}  recall={:.3f}  F1={:.3f}".format(self.precision, self.recall, self.f1)


class Evaluacion:
    def __init__(self, ground_truth):
        self.ground_truth = ground_truth
        self.lista_ignoradas = list()
        self.lista_duplicadas = list()
        self.lista_correctas = list()
        self.lista_incorrectas = list()
        self.correctas_por_tipo = dict()
        self.current_threshold = None
        self.queries = set()

    def evaluar(self, det, gt):
        self.current_threshold = det.distancia
        # no es un query con respuesta correcta
        if gt is None:
            det.linea += '\t(según GT es -)'
            self.lista_incorrectas.append(det)
            return
        # la tarea evalua solo la primera respuesta por query
        if det.imagen_q in self.queries:
            self.lista_duplicadas.append(det)
            return
        self.queries.add(det.imagen_q)
        # evaluar si la deteccion es correcta a no
        if gt.imagen_r == det.imagen_r:
            self.lista_correctas.append(det)
            if gt.tipo not in self.correctas_por_tipo:
                self.correctas_por_tipo[gt.tipo] = list()
            self.correctas_por_tipo[gt.tipo].append(det)
        else:
            det.linea += '\t(según GT es ' + gt.imagen_r + ')'
            if gt.imagen_r != '-':
                det.linea += ' (tipo=' + gt.tipo + ')'
            self.lista_incorrectas.append(det)

    def calcular_metricas(self):
        m = Metricas()
        m.threshold = self.current_threshold
        m.ignoradas = len(self.lista_ignoradas)
        m.duplicadas = len(self.lista_duplicadas)
        m.correctas = len(self.lista_correctas)
        m.incorrectas = len(self.lista_incorrectas)
        m.num_queries = self.ground_truth.total_queries()
        m.precision = m.correctas / (m.correctas + m.incorrectas)
        m.recall = m.correctas / self.ground_truth.total_queries()
        if m.precision == 0 or m.recall == 0:
            m.f1 = 0
        else:
            m.f1 = 2 * m.precision * m.recall / (m.precision + m.recall)
        for tipo in self.ground_truth.total_por_tipo:
            total = self.ground_truth.total_por_tipo[tipo]
            correctas = 0
            if tipo in self.correctas_por_tipo:
                correctas = len(self.correctas_por_tipo[tipo])
            m.correcta_por_tipo[tipo] = correctas
            m.recall_por_tipo[tipo] = correctas / total
        return m


class Evaluador:
    def __init__(self, filename_ground_truth, filename_detecciones):
        self.ground_truth = GroudTruth()
        self.ground_truth.leer_archivo_gt(filename_ground_truth)
        self.detecciones = Detecciones()
        self.detecciones.leer_archivo_detecciones(filename_detecciones)
        self.mejor_f1 = None
        self.metricas = None
        self.ev = Evaluacion(self.ground_truth)

    def evaluar_detecciones(self):
        # ordenar detecciones por distancia
        self.detecciones.lista.sort(key=lambda x: x.distancia)
        # revisar cada deteccion
        for det in self.detecciones.lista:
            gt = self.ground_truth.buscar_gt(det.imagen_q)
            # evaluar si la deteccion es correcta a no
            self.ev.evaluar(det, gt)
            self.metricas = self.ev.calcular_metricas()
            # mantener el mejor resultado encontrado hasta el momento
            if self.mejor_f1 is None or self.metricas.f1 > self.mejor_f1.f1:
                self.mejor_f1 = self.metricas

    def imprimir_resultado_general(self, nombre):
        print()
        print("Resultado general en {}:".format(nombre))
        print("  De {} casos, {} se detectaron correctamente ({:.0f}%)".format(self.metricas.num_queries,
                                                                               self.metricas.correctas,
                                                                               100 * self.metricas.recall))
        print(self.metricas.get_resultado_por_tipo())

    def imprimir_incorrectas(self, incorrectas_a_mostrar):
        print("  Las {} respuestas incorrectas de menor distancia:".format(incorrectas_a_mostrar))
        cont = 0
        for det in self.ev.lista_incorrectas:
            print("     {}".format(det.linea))
            cont += 1
            if cont == incorrectas_a_mostrar:
                break

    def imprimir_metricas(self):
        print()
        print("  Mejor F1-score con {}".format(self.mejor_f1.get_umbral()))
        print("    {}".format(self.mejor_f1.get_metricas1()))
        print("    {}".format(self.mejor_f1.get_metricas2()))


def evaluar_resultado_en_dataset(nombre, filename_gt, filename_resultados):
    print()
    print("---------")
    print("Evaluando {} con {}".format(filename_resultados, filename_gt))
    incorrectas_a_mostrar = 5
    evaluador = Evaluador(filename_gt, filename_resultados)
    evaluador.evaluar_detecciones()
    evaluador.imprimir_resultado_general(nombre)
    evaluador.imprimir_incorrectas(incorrectas_a_mostrar)
    evaluador.imprimir_metricas()
    return evaluador.mejor_f1.f1


def ejecutar(comando):
    print(" ".join(comando))
    code = subprocess.call(comando)
    if code != 0:
        print("ERROR!")
        sys.exit(1)


def ejecutar_tarea(dataset_q, dataset_r, descriptores_r, filename_resultados):
    # comandos para calcular descriptores
    comando1 = [sys.executable, "tarea1-indexar.py", dataset_r, descriptores_r]
    ejecutar(comando1)
    # comandos para buscar
    comando2 = [sys.executable, "tarea1-buscar.py", dataset_q, descriptores_r, filename_resultados]
    ejecutar(comando2)
    ## comandos para binarios (C++) en Windows
    #comando1 = ["tarea1-indexar.exe", dataset_r, descriptores_r]
    #ejecutar(comando1)
    #comando2 = ["tarea1-buscar.exe", dataset_q, descriptores_r, filename_resultados]
    #ejecutar(comando2)
    ## comandos para binarios (C++) en Linux
    #comando1 = ["./tarea1-indexar", dataset_r, descriptores_r]
    #ejecutar(comando1)
    #comando2 = ["./tarea1-buscar", dataset_q, descriptores_r, filename_resultados]
    #ejecutar(comando2)

def evaluar_en_dataset(nombre, dir_evaluacion):
    print()
    print("------- {} -------".format(nombre))
    dataset_dir = "datasets/{}".format(nombre)
    if not os.path.isdir(dataset_dir):
        print("no existe {}".format(dataset_dir))
        sys.exit(1)
    dataset_q = "{}/q".format(dataset_dir)
    dataset_r = "{}/r".format(dataset_dir)
    filename_gt = "{}/gt.txt".format(dataset_dir)
    if not os.path.isdir(dataset_q):
        print("error leyendo {}. No existe {}".format(nombre, dataset_q))
        sys.exit(1)
    if not os.path.isdir(dataset_r):
        print("error leyendo {}. No existe {}".format(nombre, dataset_r))
        sys.exit(1)
    if not os.path.isfile(filename_gt):
        print("error leyendo {}. No existe {}".format(nombre, filename_gt))
        sys.exit(1)
    descriptores_r = "{}/datos_{}_r".format(dir_evaluacion, nombre)
    filename_resultados = "{}/resultado_{}.txt".format(dir_evaluacion, nombre)
    t0 = time.time()
    ejecutar_tarea(dataset_q, dataset_r, descriptores_r, filename_resultados)
    tiempo_segundos = time.time() - t0
    print("tiempo ejecucion: {:.1f} segundos".format(tiempo_segundos))
    f1 = evaluar_resultado_en_dataset(nombre, filename_gt, filename_resultados)
    return f1, tiempo_segundos

def calcular_nota(f1_promedio):
    f1_para_4 = 0.3
    f1_para_7 = 0.75
    f1_max_bonus = 0.9
    if f1_promedio <= f1_para_4:
        nota = 1 + round(3 * f1_promedio / f1_para_4, 1)
        bonus = 0
    elif f1_promedio <= f1_para_7:
        nota = 4 + round(3 * (f1_promedio - f1_para_4) / (f1_para_7 - f1_para_4), 1)
        bonus = 0
    elif f1_promedio <= f1_max_bonus:
        nota = 7
        bonus = round((f1_promedio - f1_para_7) / (f1_max_bonus - f1_para_7), 1)
    else:
        nota = 7
        bonus = 1
    return nota, bonus

def evaluar_tarea1(datasets):
    print("CC5213 - Recuperación de Información Multimedia - Primavera 2023")
    print("Evaluación Tarea 1")
    # datos para la evaluacion
    dir_evaluacion = "eval_t1"
    if os.path.exists(dir_evaluacion):
        print("borrando datos previos en {}...".format(dir_evaluacion))
        shutil.rmtree(dir_evaluacion)
    # evaluar sobre los datasets
    resultados = {}
    for name in datasets:
        nombre = "dataset_" + name
        f1, tiempo_segundos = evaluar_en_dataset(nombre, dir_evaluacion)
        resultados[nombre] = (f1, tiempo_segundos)
    # imprimir resultados
    print()
    print("--------------------------------------------")
    print("Resumen:")
    f1s = []
    for nombre in resultados:
        (f1, tiempo_segundos) = resultados[nombre]
        f1s.append(f1)
        print("    F1-score en {}: {:.3f}   (tiempo={:.1f} segundos)".format(nombre, f1, tiempo_segundos))
    promedio = numpy.average(f1s)
    print("    ==> Promedio F1-score: {:.3f}".format(promedio))
    nota, bonus = calcular_nota(promedio)
    print()
    print("    ==> Nota tarea 1 = {:.1f}".format(nota))
    if bonus > 0:
        print("    ==> Bonus = {:.1f}".format(bonus))


# parametros de entrada
datasets = ["a", "b", "c"]
if len(sys.argv) > 1:
    datasets = sys.argv[1:]

evaluar_tarea1(datasets)
