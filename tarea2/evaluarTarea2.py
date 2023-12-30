# CC5213 - TAREA 2
# 28 de septiembre de 2023 
import sys
import os.path
import subprocess
import numpy
import shutil
import time


class Deteccion:
    def __init__(self, id_deteccion, archivo_fuente, tipo, television, desde, largo, comercial, confianza):
        self.id_deteccion = id_deteccion
        self.archivo_fuente = archivo_fuente
        self.tipo = tipo
        self.television = television
        self.desde = desde
        self.largo = largo
        self.comercial = comercial
        self.confianza = confianza

    def interseccion(self, otra):
        if self.television != otra.television or self.comercial != otra.comercial:
            return 0
        ini1 = self.desde
        end1 = self.desde + self.largo
        ini2 = otra.desde
        end2 = otra.desde + otra.largo
        inter = min(end1, end2) - max(ini1, ini2)
        union = max(end1, end2) - min(ini1, ini2)
        if inter <= 0 or union <= 0:
            return 0
        return inter / union


def get_filename(filepath):
    name = filepath.lower().strip()
    if name.rfind('/') >= 0:
        name = name[name.rfind('/') + 1:]
    if name.rfind('\\') >= 0:
        name = name[name.rfind('\\') + 1:]
    return name


def parsear_deteccion(id_deteccion, archivo_fuente, linea, es_gt):
    linea = linea.rstrip("\r\n")
    # se ignoran lineas vacias o comentarios
    if linea == "" or linea.startswith("#"):
        return None
    partes = linea.split("\t")
    if len(partes) != 5:
        raise Exception(
            archivo_fuente + " incorrecto numero de columnas (se esperan 5 columnas separadas por un tabulador)")
    tipo = television = comercial = ""
    desde = largo = confianza = 0
    if es_gt:
        tipo = partes[0]
        television = get_filename(partes[1])
        desde = round(float(partes[2]), 3)
        largo = round(float(partes[3]), 3)
        comercial = get_filename(partes[4])
    else:
        television = get_filename(partes[0])
        desde = round(float(partes[1]), 3)
        largo = round(float(partes[2]), 3)
        comercial = get_filename(partes[3])
        confianza = float(partes[4])
        if confianza <= 0:
            raise Exception("valor incorrecto confianza={} en {}".format(confianza, archivo_fuente))
    if television == "":
        raise Exception("nombre television invalido en " + archivo_fuente)
    if comercial == "":
        raise Exception("nombre comercial invalido en " + archivo_fuente)
    if desde < 0:
        raise Exception("valor incorrecto desde={} en {}".format(desde, archivo_fuente))
    if largo <= 0:
        raise Exception("valor incorrecto largo={} en {}".format(largo, archivo_fuente))
    det = Deteccion(id_deteccion, archivo_fuente, tipo, television, desde, largo, comercial, confianza)
    return det


def leer_archivo_detecciones(lista, filename, es_gt):
    if not os.path.isfile(filename):
        if filename == "":
            return
        raise Exception("no existe el archivo {}".format(filename))
    cont_lineas = 0
    cont_detecciones = 0
    with open(filename) as f:
        for linea in f:
            cont_lineas += 1
            try:
                # el id es su posición en la lista
                det = parsear_deteccion(len(lista), filename, linea, es_gt)
                if det is not None:
                    lista.append(det)
                    cont_detecciones += 1
            except Exception as ex:
                print("Error {} (linea {}): {}".format(filename, cont_lineas, ex))
    print("{} detecciones en archivo {}".format(cont_detecciones, filename))


class ResultadoDeteccion:
    def __init__(self, deteccion):
        self.deteccion = deteccion
        self.es_incorrecta = False
        self.es_duplicada_mismo_fuente = False
        self.es_duplicada_otro_fuente = False
        self.es_correcta = False
        self.gt = None
        self.iou = 0


class Metricas:
    def __init__(self, threshold):
        self.threshold = threshold
        self.total_gt = 0
        self.total_detecciones = 0
        self.correctas = 0
        self.incorrectas = 0
        self.recall = 0
        self.precision = 0
        self.f1 = 0
        self.iou = 0
        self.f1_iou = 0
        self.correctas_por_tipo = dict()
        self.recall_por_tipo = dict()


class Evaluacion:
    def __init__(self):
        self.detecciones_gt = list()
        self.total_gt_por_tipo = dict()
        self.detecciones = list()
        self.resultado_por_deteccion = list()
        self.resultado_global = None

    def leer_archivo_gt(self, file_gt):
        # cargar el ground-truth
        leer_archivo_detecciones(self.detecciones_gt, file_gt, True)
        for gt in self.detecciones_gt:
            self.total_gt_por_tipo[gt.tipo] = self.total_gt_por_tipo.get(gt.tipo, 0) + 1

    def leer_archivo_detecciones(self, file_detecciones):
        # cargar las detecciones
        leer_archivo_detecciones(self.detecciones, file_detecciones, False)

    def evaluar_cada_deteccion(self):
        # ordenar detecciones por confianza de mayor a menor
        self.detecciones.sort(key=lambda x: x.confianza, reverse=True)
        # para descartar las detecciones duplicadas
        ids_encontradas = {}
        # revisar cada deteccion
        for det in self.detecciones:
            # evaluar cada deteccion si es correcta a no
            gt_encontrada, iou = self.buscar_deteccion_en_gt(det)
            # retorna resultado
            res = ResultadoDeteccion(det)
            if gt_encontrada is None:
                res.es_incorrecta = True
            elif gt_encontrada.id_deteccion in ids_encontradas:
                fuentes = ids_encontradas[gt_encontrada.id_deteccion]
                # revisar si ya se detectó en el mismo archivo
                if det.archivo_fuente in fuentes:
                    res.es_duplicada_mismo_fuente = True
                else:
                    res.es_duplicada_otro_fuente = True
                    fuentes.add(det.archivo_fuente)
            else:
                res.es_correcta = True
                res.gt = gt_encontrada
                res.iou = iou
                # agrego el origen que lo detectó
                fuentes = set()
                fuentes.add(det.archivo_fuente)
                ids_encontradas[gt_encontrada.id_deteccion] = fuentes
            self.resultado_por_deteccion.append(res)
        # ordenar los resultados como el archivo de entrada
        self.resultado_por_deteccion.sort(key=lambda x: x.deteccion.id_deteccion)

    def buscar_deteccion_en_gt(self, deteccion):
        gt_encontrada = None
        iou = 0
        # busca en gt la deteccion que tiene mayor interseccion
        for det_gt in self.detecciones_gt:
            interseccion = deteccion.interseccion(det_gt)
            if interseccion > iou:
                gt_encontrada = det_gt
                iou = interseccion
        return gt_encontrada, iou

    def calcular_metricas(self):
        # todos los umbrales posibles
        set_confianzas = set()
        for res in self.resultado_por_deteccion:
            if res.es_correcta:
                set_confianzas.add(res.deteccion.confianza)
        set_confianzas.add(0)
        # calcular las metricas para cada confianza y seleccionar el mejor
        for confianza in sorted(list(set_confianzas), reverse=True):
            met = self.evaluar_con_threshold(confianza)
            if self.resultado_global is None or met.f1_iou > self.resultado_global.f1_iou:
                self.resultado_global = met

    def evaluar_con_threshold(self, threshold):
        met = Metricas(threshold)
        met.total_gt = len(self.detecciones_gt)
        suma_iou = 0
        correctas_por_tipo = dict()
        for res in self.resultado_por_deteccion:
            # ignorar detecciones con confianza bajo el umbral
            if res.deteccion.confianza < threshold or res.es_duplicada_otro_fuente:
                continue
            met.total_detecciones += 1
            if res.es_correcta:
                met.correctas += 1
                suma_iou += res.iou
                correctas_por_tipo[res.gt.tipo] = correctas_por_tipo.get(res.gt.tipo, 0) + 1
            if res.es_incorrecta or res.es_duplicada_mismo_fuente:
                met.incorrectas += 1
        if met.correctas > 0:
            met.recall = met.correctas / met.total_gt
            met.precision = met.correctas / met.total_detecciones
        if met.precision > 0 and met.recall > 0:
            met.f1 = (2 * met.precision * met.recall) / (met.precision + met.recall)
        if met.correctas > 0:
            met.iou = suma_iou / met.correctas
        # para evaluar se usa una combinacion entre f1 con iou
        if met.f1 > 0 and met.iou > 0:
            met.f1_iou = met.f1 * 0.8 + met.iou * 0.2
        for tipo in self.total_gt_por_tipo:
            total = self.total_gt_por_tipo[tipo]
            correctas = correctas_por_tipo.get(tipo, 0)
            met.correctas_por_tipo[tipo] = correctas
            met.recall_por_tipo[tipo] = correctas / total
        return met

    def imprimir_resultado_por_deteccion(self):
        if len(self.resultado_por_deteccion) == 0:
            return
        print("Resultado detallado de cada una de las {} detecciones:".format(len(self.resultado_por_deteccion)))
        for res in self.resultado_por_deteccion:
            s1 = ""
            s2 = ""
            if res.es_correcta:
                s1 = "   OK)"
                s2 = " //IoU={:.1%} gt=({} {})".format(res.iou, res.gt.desde, res.gt.largo)
            elif res.es_duplicada_mismo_fuente:
                s1 = "dup--)"
            elif res.es_duplicada_otro_fuente:
                s1 = "dupOK)"
            elif res.es_incorrecta:
                s1 = "   --)"
            d = res.deteccion
            print(" {} {} {} {} {} {} {}".format(s1, d.television, d.desde, d.largo, d.comercial, d.confianza, s2))

    def imprimir_resultado_global(self):
        if self.resultado_global is None:
            return
        m = self.resultado_global
        print()
        print("Resultado global:")
        print(" {} detecciones en GT, {} detecciones a evaluar".format(m.total_gt, len(self.resultado_por_deteccion)))
        print(" Al usar umbral={} se seleccionan {} detecciones:".format(m.threshold, m.total_detecciones))
        print("    {} detecciones correctas, {} detecciones incorrectas".format(m.correctas, m.incorrectas))
        print("    Precision={:.3f} ({}/{})  Recall={:.3f} ({}/{})".format(m.precision, m.correctas,
                                                                           m.total_detecciones, m.recall, m.correctas,
                                                                           m.total_gt))
        print("    F1={:.3f}  IoU={:.1%}  ->  F1-IOU={:.3f}".format(m.f1, m.iou, m.f1_iou))
        print()
        print("Resultado por transformacion:")
        for tipo in m.recall_por_tipo:
            print("    {:9s}={:4} correctas ({:.0f}%)".format(tipo, m.correctas_por_tipo[tipo],
                                                              100 * m.recall_por_tipo[tipo]))


def evaluar_resultado_en_dataset(nombre, filename_gt, filename_resultados):
    print()
    print("Evaluando {} con {}".format(filename_resultados, filename_gt))
    ev = Evaluacion()
    ev.leer_archivo_gt(filename_gt)
    ev.leer_archivo_detecciones(filename_resultados)
    ev.evaluar_cada_deteccion()
    ev.calcular_metricas()
    ev.imprimir_resultado_por_deteccion()
    ev.imprimir_resultado_global()
    return ev.resultado_global.f1_iou


def ejecutar(comando):
    print(" ".join(comando))
    code = subprocess.call(comando)
    if code != 0:
        print("ERROR!")
        sys.exit(1)


def ejecutar_tarea(dataset_radio, dataset_canciones, datos_temporales, filename_resultados):
    dir_descriptores_canciones = "{}/descriptores_canciones/".format(datos_temporales)
    dir_descriptores_radio = "{}/descriptores_radio/".format(datos_temporales)
    dir_resultados_knn = "{}/busqueda/".format(datos_temporales)
    # comando para calcular descriptores R
    comando1 = [sys.executable, "tarea2-extractor.py", dataset_canciones, dir_descriptores_canciones]
    ejecutar(comando1)
    # comando para calcular descriptores Q
    comando2 = [sys.executable, "tarea2-extractor.py", dataset_radio, dir_descriptores_radio]
    ejecutar(comando2)
    # comando para buscar
    comando3 = [sys.executable, "tarea2-busqueda.py", dir_descriptores_radio, dir_descriptores_canciones, dir_resultados_knn]
    ejecutar(comando3)
    # comando para detectar
    comando4 = [sys.executable, "tarea2-deteccion.py", dir_resultados_knn, filename_resultados]
    ejecutar(comando4)


def evaluar_en_dataset(nombre, dir_evaluacion):
    print()
    print("------- {} -------".format(nombre))
    dataset_dir = "datasets/{}".format(nombre)
    if not os.path.isdir(dataset_dir):
        print("no existe {}".format(dataset_dir))
        sys.exit(1)
    dataset_radio = "{}/radio/".format(dataset_dir)
    dataset_canciones = "{}/canciones/".format(dataset_dir)
    filename_gt = "{}/gt.txt".format(dataset_dir)
    if not os.path.isdir(dataset_radio):
        print("error leyendo {}. No existe {}".format(nombre, dataset_radio))
        sys.exit(1)
    if not os.path.isdir(dataset_canciones):
        print("error leyendo {}. No existe {}".format(nombre, dataset_canciones))
        sys.exit(1)
    if not os.path.isfile(filename_gt):
        print("error leyendo {}. No existe {}".format(nombre, filename_gt))
        sys.exit(1)
    datos_temporales = "{}/datos_{}".format(dir_evaluacion, nombre)
    filename_resultados = "{}/resultado_{}.txt".format(dir_evaluacion, nombre)
    os.makedirs(datos_temporales, exist_ok=True)
    t0 = time.time()
    ejecutar_tarea(dataset_radio, dataset_canciones, datos_temporales, filename_resultados)
    tiempo_segundos = time.time() - t0
    print("tiempo ejecucion: {:.1f} segundos".format(tiempo_segundos))
    f1_iou = evaluar_resultado_en_dataset(nombre, filename_gt, filename_resultados)
    return f1_iou, tiempo_segundos


def calcular_nota(resultado_promedio, metrica_para_4, metrica_para_7):
    if resultado_promedio <= metrica_para_4:
        nota = 1 + round(3 * resultado_promedio / metrica_para_4, 1)
        bonus = 0
    elif resultado_promedio <= metrica_para_7:
        nota = 4 + round(3 * (resultado_promedio - metrica_para_4) / (metrica_para_7 - metrica_para_4), 1)
        bonus = 0
    else:
        nota = 7
        bonus = round((resultado_promedio - metrica_para_7) / (1 - metrica_para_7), 1)
    return nota, bonus


def evaluar_tarea2(datasets):
    print("CC5213 - Recuperación de Información Multimedia - Primavera 2023")
    print("Evaluación Tarea 2")
    # datos para la evaluacion
    dir_evaluacion = "eval_t2"
    if os.path.exists(dir_evaluacion):
        print("borrando datos previos en {}...".format(dir_evaluacion))
        shutil.rmtree(dir_evaluacion)
    # evaluar sobre los datasets
    resultados = {}
    for name in datasets:
        nombre = "dataset_" + name
        f1_iou, tiempo_segundos = evaluar_en_dataset(nombre, dir_evaluacion)
        resultados[nombre] = (f1_iou, tiempo_segundos)
    # imprimir resultados
    print()
    print("--------------------------------------------")
    print("Resumen:")
    f1s = []
    for nombre in resultados:
        (f1_iou, tiempo_segundos) = resultados[nombre]
        f1s.append(f1_iou)
        print("    F1-IOU-score en {}: {:.3f}   (tiempo={:.1f} segundos)".format(nombre, f1_iou, tiempo_segundos))
    promedio = numpy.average(f1s)
    print("    ==> Promedio: {:.3f}".format(promedio))
    metrica_para_4 = 0.2
    metrica_para_7 = 0.9
    nota, bonus = calcular_nota(promedio, metrica_para_4, metrica_para_7)
    print()
    print("    Criterio: Para obtener nota 4.0 se requiere F1-IOU {:.3f}".format(metrica_para_4))
    print("              Para obtener nota 7.0 se requiere F1-IOU {:.3f}".format(metrica_para_7))
    print()
    print("    ==> Nota tarea 2 = {:.1f}".format(nota))
    if bonus > 0:
        print("    ==> Bonus = {:.1f}".format(bonus))


# parametros de entrada
datasets = ["a", "b", "c", "d"]
if len(sys.argv) > 1:
    datasets = sys.argv[1:]

evaluar_tarea2(datasets)
