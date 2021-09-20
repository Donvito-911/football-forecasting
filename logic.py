'''--------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

                        En este documento se realizará toda la lógica del proyecto:
                        - WebScraping & bases de datos
                        - Análisis de datos (Probabilidades)
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------'''

# importación de paquetes

import json
import urllib.request
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
#from colorama import Style, Back


'''---------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------WEB SCRAPING & bases de datos-----------------------------------------
 -----------------------------------------------------------------------------------------------------------------------------'''


def url_jornada(jornada: str, liga: int) -> str:
    if liga == 1:
        respuesta = url_jornada_premier(jornada)

    elif liga == 2:
        respuesta = url_jornada_bundesliga(jornada)

    return respuesta


def journey(liga: int, jornada: str):

    if liga == 1:
        url = url_jornada(jornada, liga)
        respuesta = jornada_premier(url)

    elif liga == 2:
        url = url_jornada(jornada, liga)
        respuesta = jornada_bundesliga(url)

    return respuesta


def tabla_de_posiciones(liga: int):
    if liga == 1:
        respuesta = tabla_de_posiciones_premier()

    elif liga == 2:
        respuesta = tabla_de_posiciones_bundesliga()

    return respuesta


def resultados_10_jornadas(jornada: str, liga: int):
    if liga == 1:
        respuesta = resultados_10_jornadas_premier(jornada)
    elif liga == 2:
        respuesta = resultados_10_jornadas_bundesliga(jornada)

    return respuesta


def base_datos(liga: int, jornada: str):

    resultados = resultados_10_jornadas(jornada, liga)

    if liga == 1:
        respuesta = base_datos_premier(resultados)

    elif liga == 2:
        respuesta = base_datos_bundesliga(resultados)

    return respuesta


'''-----------------------------------------PREMIER LEAGUE-----------------------------------------'''

# Jornadas


def url_jornada_premier(jornada: str) -> str:

    urlreq = 'https://draft.premierleague.com/api/event/' + jornada + '/fixtures'

    return urlreq


def jornada_premier(urlreq: str):

    # get response
    response = urllib.request.urlopen(urlreq)

    # load as json
    fixtures = json.load(response)

    tabla = pd.read_csv('premier_league.csv')

    equipos = pd.DataFrame({"equipos": tabla['equipos'].sort_values(
        ignore_index=True), "id": list(range(1, 21, 1))})

    # error del scraping que hay que corregir manualmente (Leicester y Leeds tienen distinto codigo)
    equipos.iloc[8, 1] = 10
    equipos.iloc[9, 1] = 9

    partidos = {"equipo_local": [], "equipo_visitante": []}

    for j in range(len(fixtures)):
        equipo_A = fixtures[j]["team_a"]
        equipo_B = fixtures[j]["team_h"]
        for i in range(0, len(equipos)):
            if equipo_A == equipos.iloc[i, 1]:
                equipo_A = equipos.iloc[i, 0]
                partidos["equipo_visitante"].append(equipo_A)

            if equipo_B == equipos.iloc[i, 1]:
                equipo_B = equipos.iloc[i, 0]
                partidos["equipo_local"].append(equipo_B)

    partidos = pd.DataFrame(partidos)

    return partidos

    # Tabla de posiciones


def tabla_de_posiciones_premier():
    # saco la url de la tabla
    url = "https://www.premierleague.com/tables"

    # creo el request de la pagina
    page = requests.get(url)

    # creo la sopa con todo el contenido html
    soup = BeautifulSoup(page.content, "html.parser")

    # creo la lista de equipos
    eq = soup.find_all('span', class_="long", limit=20)
    equipos = []
    for i in range(0, len(eq)):
        equipos.append(str(eq[i].string))

    # creo los datos
    jg = soup.find_all('tr')  # busco todas las filas (tag <tr>)
    # creo donde irá la lista de listas (cada lista son los resultados de un equipo)
    datos = []

    # analizo cada fila que hay en jg (donde solo hay filas de tablas(tr))
    for i in range(1, len(jg)):
        contenido = jg[i].contents  # miro el contenido de cada fila
        equipo = []  # creo el equipo instanciado
        # reviso en cada contenido si me sirve para los datos (tiene que ser <td>)
        for j in range(0, len(contenido)):
            # veo lo que hay dentro de cada linea de codigo, solo me quedo con los numeros
            contenido[j] = str(contenido[j].string)
            contenido[j] = contenido[j].strip()
            # saco los datos que no me interesan
            if len(contenido[j]) > 0 and contenido[j] != "None":
                equipo.append(contenido[j])
        if len(equipo) > 0:  # hay listas vacías, las quito.
            datos.append(equipo)

    # solo cojo los 20 primeros elementos que representan los datos de los equipos de la premier
    datos = datos[0:20]

    for i in range(0, len(datos)):
        for j in range(0, len(datos[i])):
            # los convierto en enteros para hacer futuras estimaciones
            datos[i][j] = int(datos[i][j])

    # creo la tabla
    tabla = pd.DataFrame({"equipos": equipos, "PJ": 0, "G": 0, "E": 0, "P": 0,
                          "GF": 0, "GC": 0, "DF": 0, "Puntos": 0}, index=np.arange(1, 21))

    # pego los datos que obtuve con scraping
    for i in range(0, len(tabla)):
        tabla.iloc[i, 1] = datos[i][0]
        tabla.iloc[i, 2] = datos[i][1]
        tabla.iloc[i, 3] = datos[i][2]
        tabla.iloc[i, 4] = datos[i][3]
        tabla.iloc[i, 5] = datos[i][4]
        tabla.iloc[i, 6] = datos[i][5]
        tabla.iloc[i, 7] = datos[i][6]
        tabla.iloc[i, 8] = datos[i][7]

    tabla.to_csv('premier_league.csv', index=False)
    return tabla


def resultado_por_jornada_premier(url):
    # get response
    response = urllib.request.urlopen(url)

    # load as json
    fixtures = json.load(response)

    tabla = pd.read_csv('premier_league.csv')

    equipos = pd.DataFrame({"equipos": tabla['equipos'].sort_values(
        ignore_index=True), "id": list(range(1, 21, 1))})

    # error del scraping que hay que corregir manualmente (Leicester y Leeds tienen distinto codigo)
    equipos.iloc[8, 1] = 10
    equipos.iloc[9, 1] = 9

    partidos = {"equipo_local": [], 'marcador': [], "equipo_visitante": []}

    for j in range(len(fixtures)):
        equipo_A = fixtures[j]["team_a"]
        equipo_B = fixtures[j]["team_h"]
        equipo_A_score = fixtures[j]["team_a_score"]
        equipo_B_score = fixtures[j]["team_h_score"]

        for i in range(0, len(equipos)):
            if equipo_A == equipos.iloc[i, 1]:
                equipo_A = equipos.iloc[i, 0]
                partidos["equipo_visitante"].append(equipo_A)
                partidos['marcador'].append(
                    str(equipo_B_score) + ':' + str(equipo_A_score))

            if equipo_B == equipos.iloc[i, 1]:
                equipo_B = equipos.iloc[i, 0]
                partidos["equipo_local"].append(equipo_B)

    partidos = pd.DataFrame(partidos)
    return partidos


def resultados_10_jornadas_premier(jornada: str):
    jornada = int(jornada)
    resultados_jornadas = pd.DataFrame()
    minimo = max(jornada - 10, 1)

    for i in range(minimo, jornada):
        url = url_jornada_premier(str(i))
        resultado_jornada = resultado_por_jornada_premier(url)
        resultados_jornadas = resultados_jornadas.append(
            resultado_jornada, ignore_index=True)

    return resultados_jornadas


def base_datos_premier(resultados):
    equipos = list(resultados['equipo_local'].unique())
    equipos.sort()
    data = {'equipo': equipos, 'gano': [0] * 20, 'perdio': [0] * 20, 'empato': [0] * 20, 'gano_local': [0] * 20, 'gano_visitante': [
        0] * 20, 'perdio_local': [0] * 20, 'perdio_visitante': [0] * 20, 'empato_local': [0] * 20, 'empato_visitante': [0] * 20}

    def resultado(marcador: str):
        indice = marcador.index(':')
        local = int(marcador[:indice])
        visitante = int(marcador[indice + 1:])

        if local > visitante:
            resultado = 'gano_local'

        elif local < visitante:
            resultado = 'gano_visitante'

        else:
            resultado = 'empato'

        return resultado

    resultados['resultado'] = resultados.marcador.apply(resultado)
    resultados['indice_local'] = resultados.equipo_local.apply(
        data['equipo'].index)
    resultados['indice_visitante'] = resultados.equipo_visitante.apply(
        data['equipo'].index)

    for i in range(len(resultados)):

        resultado = resultados.iloc[i]['resultado']
        indice_local = resultados.iloc[i]['indice_local']
        indice_visitante = resultados.iloc[i]['indice_visitante']
        if resultado == 'gano_local':
            data[resultado][indice_local] += 1
            data['perdio_visitante'][indice_visitante] += 1

        elif resultado == 'gano_visitante':
            data[resultado][indice_visitante] += 1
            data['perdio_local'][indice_local] += 1

        elif resultado == 'empato':
            data['empato_local'][indice_local] += 1
            data['empato_visitante'][indice_visitante] += 1

    data['gano'] = [sum(x) for x in zip(
        data['gano_local'], data['gano_visitante'])]
    data['empato'] = [sum(x) for x in zip(
        data['empato_local'], data['empato_visitante'])]
    data['perdio'] = [sum(x) for x in zip(
        data['perdio_local'], data['perdio_visitante'])]

    lists_of_lists = [data['gano_local'],
                      data['perdio_local'], data['empato_local']]
    data['partidos_local'] = [sum(x) for x in zip(*lists_of_lists)]

    lists_of_lists = [data['gano_visitante'],
                      data['perdio_visitante'], data['empato_visitante']]
    data['partidos_visitante'] = [sum(x) for x in zip(*lists_of_lists)]

    dataframe = pd.DataFrame(data)

    columnas = ['gano', 'perdio', 'empato']
    columnas_local = ['gano_local', 'perdio_local', 'empato_local']
    columnas_visitante = ['gano_visitante',
                          'perdio_visitante', 'empato_visitante']

    for i in range(len(dataframe)):
        total_partidos = dataframe.iloc[i]['gano'] + \
            dataframe.iloc[i]['perdio'] + dataframe.iloc[i]['empato']
        total_partidos_local = dataframe.iloc[i]['gano_local'] + \
            dataframe.iloc[i]['perdio_local'] + \
            dataframe.iloc[i]['empato_local']
        total_partidos_visitante = dataframe.iloc[i]['gano_visitante'] + \
            dataframe.iloc[i]['perdio_visitante'] + \
            dataframe.iloc[i]['empato_visitante']

        for j in columnas:
            dataframe.loc[i, j] = dataframe.loc[i, j] / total_partidos

        for j in columnas_local:
            dataframe.loc[i, j] = dataframe.loc[i, j] / total_partidos_local

        for j in columnas_visitante:
            dataframe.loc[i, j] = dataframe.loc[i, j] / \
                total_partidos_visitante

    return dataframe


'''-----------------------------------------Bundesliga-----------------------------------------'''

# Jornadas


def url_jornada_bundesliga(jornada: str) -> str:
    """


    Parameters
    ----------
    a : str
        toma una jornada en cuestión y la pega con la url para obtener la url de la jornada a.

    Returns
    -------
    str
        DESCRIPTION.

    """
    urlreq = "https://www.bundesliga.com/es/bundesliga/partidos/2020-2021/" + jornada

    return urlreq


def jornada_bundesliga(url: str):
    # creo el request de la pagina
    page = requests.get(url)

    # creo la sopa con todo el contenido html
    soup = BeautifulSoup(page.content, "html.parser")

    # creo la lista de equipos
    eq = soup.find_all('div', class_=['clubName'])

    partidos = {'equipo_local': [], 'equipo_visitante': []}

    for i in range(0, len(eq), 2):
        partidos['equipo_local'].append(str(eq[i].string))
        partidos['equipo_visitante'].append(str(eq[i + 1].string))

    partidos = pd.DataFrame(partidos)
    return partidos

    # Tabla de posiciones


def tabla_de_posiciones_bundesliga():
    # saco la url de la tabla
    url = "https://www.bundesliga.com/es/bundesliga/clasificacion"

    # creo el request de la pagina
    page = requests.get(url)

    # creo la sopa con todo el contenido html
    soup = BeautifulSoup(page.content, "html.parser")

    # creo la lista de equipos
    eq = soup.find_all('span', class_="d-none d-sm-inline d-lg-none", limit=20)
    equipos = []
    for i in range(len(eq)):
        equipos.append(str(eq[i].string))

    jg = soup.find_all('td', class_=['matches', 'd-none d-lg-table-cell wins', 'd-none d-lg-table-cell draws',
                       'd-none d-lg-table-cell looses', 'd-none d-md-table-cell goals', 'difference', 'pts'])
    datos = []
    n = 0
    equipo = []
    for i in range(len(jg)):

        contenido = jg[i]
        equipo.append(str(contenido.string))
        n += 1

        if n == 7:
            datos.append(equipo)
            equipo = []
            n = 0

    for i in range(len(datos)):
        datos[i].insert(7, datos[i].pop(1))  # cambio de posicion los puntos
        goles = datos[i][4]
        gc = goles[goles.index(':') + 1:]
        gf = goles[:goles.index(':')]
        datos[i].pop(4)
        datos[i].insert(4, gc)
        datos[i].insert(4, gf)

    tabla = pd.DataFrame({"equipos": equipos, "PJ": 0, "G": 0, "E": 0, "P": 0,
                          "GF": 0, "GC": 0, "DF": 0, "Puntos": 0}, index=np.arange(1, 19))

    # pego los datos que obtuve con scraping
    for i in range(0, len(tabla)):
        tabla.iloc[i, 1] = int(datos[i][0])
        tabla.iloc[i, 2] = int(datos[i][1])
        tabla.iloc[i, 3] = int(datos[i][2])
        tabla.iloc[i, 4] = int(datos[i][3])
        tabla.iloc[i, 5] = int(datos[i][4])
        tabla.iloc[i, 6] = int(datos[i][5])
        tabla.iloc[i, 7] = int(datos[i][6])
        tabla.iloc[i, 8] = int(datos[i][7])

    tabla.to_csv('bundesliga.csv', index=False)
    return tabla


# hacer todo esto en la premier league

# this
def resultado_por_jornada_bundesliga(url):
    page = requests.get(url)

    # creo la sopa con todo el contenido html
    soup = BeautifulSoup(page.content, "html.parser")

    # creo la lista de equipos
    eq = soup.find_all(['span', 'div'], class_=['scoreLive', 'clubName'])

    partidos = {'equipo_local': [], 'marcador': [], 'equipo_visitante': []}

    for i in range(len(eq)):
        if i + 1 in range(len(eq)):
            if len(eq[i].contents) == 1 and len(eq[i + 1].contents) > 1:
                equipo_local = str(eq[i].string)

                marcador = str(eq[i + 1].contents[0].string + eq[i
                               + 1].contents[1].string + eq[i + 1].contents[2].string)

                equipo_visitante = str(eq[i + 2].string)

                partidos['equipo_local'].append(equipo_local)
                partidos['equipo_visitante'].append(equipo_visitante)
                partidos['marcador'].append(marcador)
        else:
            break

    partidos = pd.DataFrame(partidos)

    return partidos


# this
def resultados_10_jornadas_bundesliga(jornada: str):
    jornada = int(jornada)
    resultados_jornadas = pd.DataFrame()
    minimo = max(jornada - 10, 1)

    for i in range(minimo, jornada):
        url = url_jornada_bundesliga(str(i))
        resultado_jornada = resultado_por_jornada_bundesliga(url)
        resultados_jornadas = resultados_jornadas.append(
            resultado_jornada, ignore_index=True)

    return resultados_jornadas


# this
def base_datos_bundesliga(resultados):
    equipos = list(resultados['equipo_local'].unique())
    equipos.sort()
    data = {'equipo': equipos, 'gano': [0] * 18, 'perdio': [0] * 18, 'empato': [0] * 18, 'gano_local': [0] * 18, 'gano_visitante': [
        0] * 18, 'perdio_local': [0] * 18, 'perdio_visitante': [0] * 18, 'empato_local': [0] * 18, 'empato_visitante': [0] * 18}

    def resultado(marcador: str):
        indice = marcador.index(':')
        local = int(marcador[:indice])
        visitante = int(marcador[indice + 1:])

        if local > visitante:
            resultado = 'gano_local'

        elif local < visitante:
            resultado = 'gano_visitante'

        else:
            resultado = 'empato'

        return resultado

    resultados['resultado'] = resultados.marcador.apply(resultado)
    resultados['indice_local'] = resultados.equipo_local.apply(
        data['equipo'].index)
    resultados['indice_visitante'] = resultados.equipo_visitante.apply(
        data['equipo'].index)

    for i in range(len(resultados)):

        resultado = resultados.iloc[i]['resultado']
        indice_local = resultados.iloc[i]['indice_local']
        indice_visitante = resultados.iloc[i]['indice_visitante']
        if resultado == 'gano_local':
            data[resultado][indice_local] += 1
            data['perdio_visitante'][indice_visitante] += 1

        elif resultado == 'gano_visitante':
            data[resultado][indice_visitante] += 1
            data['perdio_local'][indice_local] += 1

        elif resultado == 'empato':
            data['empato_local'][indice_local] += 1
            data['empato_visitante'][indice_visitante] += 1

    data['gano'] = [sum(x) for x in zip(
        data['gano_local'], data['gano_visitante'])]
    data['empato'] = [sum(x) for x in zip(
        data['empato_local'], data['empato_visitante'])]
    data['perdio'] = [sum(x) for x in zip(
        data['perdio_local'], data['perdio_visitante'])]

    lists_of_lists = [data['gano_local'],
                      data['perdio_local'], data['empato_local']]
    data['partidos_local'] = [sum(x) for x in zip(*lists_of_lists)]

    lists_of_lists = [data['gano_visitante'],
                      data['perdio_visitante'], data['empato_visitante']]
    data['partidos_visitante'] = [sum(x) for x in zip(*lists_of_lists)]

    dataframe = pd.DataFrame(data)

    columnas = ['gano', 'perdio', 'empato']
    columnas_local = ['gano_local', 'perdio_local', 'empato_local']
    columnas_visitante = ['gano_visitante',
                          'perdio_visitante', 'empato_visitante']

    for i in range(len(dataframe)):
        total_partidos = dataframe.iloc[i]['gano'] + \
            dataframe.iloc[i]['perdio'] + dataframe.iloc[i]['empato']
        total_partidos_local = dataframe.iloc[i]['gano_local'] + \
            dataframe.iloc[i]['perdio_local'] + \
            dataframe.iloc[i]['empato_local']
        total_partidos_visitante = dataframe.iloc[i]['gano_visitante'] + \
            dataframe.iloc[i]['perdio_visitante'] + \
            dataframe.iloc[i]['empato_visitante']

        for j in columnas:
            dataframe.loc[i, j] = dataframe.loc[i, j] / total_partidos

        for j in columnas_local:
            dataframe.loc[i, j] = dataframe.loc[i, j] / total_partidos_local

        for j in columnas_visitante:
            dataframe.loc[i, j] = dataframe.loc[i, j] / \
                total_partidos_visitante

    return dataframe


'''---------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------- PROBABILIDADES --------------------------------------------------
 -----------------------------------------------------------------------------------------------------------------------------'''

# PROBABILIDAD DE GOLES


def prob_anotar_goles(equipo_A: list, equipo_B: list) -> list:
    """


    Parameters
    ----------
    equipo_A : list
        una lista de dos elementos: goles favor, goles contra.
    equipo_B : list
        una lista de dos elementos: goles favor, goles contra.

    Returns
    -------
    list
        lista con la probabilidad de anotar goles.

    """

    prob_equipo_A = (equipo_A[0] + equipo_B[1]) / \
        (equipo_A[0] + equipo_B[0] + equipo_A[1] + equipo_B[1])
    prob_equipo_B = (equipo_B[0] + equipo_A[1]) / \
        (equipo_A[0] + equipo_B[0] + equipo_A[1] + equipo_B[1])

    lista = [prob_equipo_A, prob_equipo_B]

    return lista


def prob_le_anoten_goles(equipo_A: list, equipo_B: list) -> list:
    """


    Parameters
    ----------
    equipo_A : list
        lista con goles a favor y goles en contra del equipo A.
    equipo_B : list
        lista con goles a favor y goles en contra del equipo B.

    Returns
    -------
    list
        lista con la probabilidad de que le anoten al equipo A y al equipo B.

    """
    resultado = prob_anotar_goles(equipo_A, equipo_B)

    for i in range(len(resultado)):
        resultado[i] = 1 - resultado[i]

    return resultado


def prob_anotar_goles_jornada(tabla, jornada):

    equipos_locales = jornada['equipo_local']
    equipos_visitantes = jornada['equipo_visitante']
    probabilidades_locales = []
    probabilidades_visitantes = []
    for i in range(len(equipos_locales)):
        nombre_equipo_A = equipos_locales[i]
        nombre_equipo_B = equipos_visitantes[i]

        equipo_A = tabla.loc[tabla['equipos'] == nombre_equipo_A]
        equipo_A = [equipo_A.iloc[0]['GF'], equipo_A.iloc[0]['GC']]

        equipo_B = tabla.loc[tabla['equipos'] == nombre_equipo_B]
        equipo_B = [equipo_B.iloc[0]['GF'], equipo_B.iloc[0]['GC']]

        resultado = prob_anotar_goles(equipo_A, equipo_B)

        probabilidades_locales.append(resultado[0])
        probabilidades_visitantes.append(resultado[1])

    jornada['probabilidad_anotar_goles_local'] = probabilidades_locales
    jornada['probabilidad_anotar_goles_visitante'] = probabilidades_visitantes

    return jornada


def prob_le_anoten_goles_jornada(tabla, jornada):

    equipos_locales = jornada['equipo_local']
    equipos_visitantes = jornada['equipo_visitante']
    probabilidades_locales = []
    probabilidades_visitantes = []
    for i in range(len(equipos_locales)):
        nombre_equipo_A = equipos_locales[i]
        nombre_equipo_B = equipos_visitantes[i]

        equipo_A = tabla.loc[tabla['equipos'] == nombre_equipo_A]
        equipo_A = [equipo_A.iloc[0]['GF'], equipo_A.iloc[0]['GC']]

        equipo_B = tabla.loc[tabla['equipos'] == nombre_equipo_B]
        equipo_B = [equipo_B.iloc[0]['GF'], equipo_B.iloc[0]['GC']]

        resultado = prob_le_anoten_goles(equipo_A, equipo_B)

        probabilidades_locales.append(resultado[0])
        probabilidades_visitantes.append(resultado[1])

    jornada['probabilidad_le_anoten_goles_local'] = probabilidades_locales
    jornada['probabilidad_le_anoten_goles_visitante'] = probabilidades_visitantes

    return jornada


# CONDICIONALES PARA PRONOSTICOS (revisar apuntes)

# 1.1
def func1_1(equiporesultado: float, equiporesultadop: float):

    if (equiporesultadop - equiporesultado) < 0.3:
        beta = equiporesultadop / (equiporesultado + equiporesultadop)
        alpha = 1 - beta
        p_ganar = (beta * equiporesultadop) - (alpha * equiporesultado)
        return(p_ganar)

    else:
        a = equiporesultadop / (equiporesultado + equiporesultadop)
        b = equiporesultado / (equiporesultado + equiporesultadop)

        beta = (a + b) / 2
        alpha = 1 - beta
        p_ganar = (beta * equiporesultadop) - (alpha * equiporesultado)
        return(p_ganar)

# 1.2


def func1_2(equiporesultado: float, equiporesultadop: float):
    a = (equiporesultado + equiporesultadop) / 2
    b = equiporesultado - equiporesultadop
    minimo = min(a, b)
    return (minimo)

# 2.1


def func2_1(equiporesultado: float, equiporesultadop: float):
    lim_alpha_neg = 1
    lim_alpha_pos = (1 - equiporesultadop) / \
        (equiporesultado - equiporesultadop)
    alpha = (0.5 * lim_alpha_neg + 0.5 * lim_alpha_pos) / 2
    beta = 1 - alpha

    p_ganar = (alpha * equiporesultado) + (beta * equiporesultadop)
    return(p_ganar)

# 2.2


def func2_2(equiporesultado: float, equiporesultadop: float):
    lim_beta_neg = 1
    lim_beta_pos = (1 - equiporesultado) / (equiporesultadop - equiporesultado)
    beta = (0.6 * lim_beta_neg + 0.4 * lim_beta_pos) / 2
    alpha = 1 - beta

    p_ganar = (alpha * equiporesultado) + (beta * equiporesultadop)
    return(p_ganar)

# 2.3


def func2_3(equiporesultado: float, equiporesultadop: float):

    if equiporesultado < 1:
        lim_inf = 1
        lim_sup = 1 / equiporesultado
        c = (lim_inf + lim_sup) / 2
        p_ganar = (c * equiporesultado)
        return(p_ganar)

    elif equiporesultado == 1:
        return(equiporesultado)

# 4.1 equivalente a 2.1
# 4.2 equivalente a 2.2
# 4.3 equivalente a 2.3 NOOOO

# 5.1 equivalente a 1.1
# 5.2 equivalente a 1.2
# 5.3 equivalente a 1.3


# PRONOSTICOS

'''def PROB_(equipoloc:str, equipovis:str, tabla):
    """
    

    Parameters
    ----------
    equipoloc : str
        el equipo que juega de local.
    equipovis : str
        el equipo que juega de visitante.

    Returns
    -------
    Solo retorna los valores que tiene un equipo de enfrentarse a otro, lo importante es que esta
    función se utilizará después.

    """
          
    if equipoloc not in tabla.values:
        print ('––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')
        print ('El equipo local no se encuentra en la base')
        print ('––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')
    elif equipovis not in tabla.values:
        print ('––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')
        print('El equipo visitante no se encuentra en la base')
        print ('––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')

    else:
        equipo_local      = tabla[tabla.equipo == equipoloc]
        equipo_visitante  = tabla[tabla.equipo == equipovis]
        print ('––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')
        print('')
        print(Back.GREEN + equipoloc +' vs ' + equipovis)
        print(Style.RESET_ALL)
        print ('RESULTADOS PARTICULARES:')
            
        equipo_resultado  = float (equipo_local [ 'gano_local'])    - float (equipo_visitante ['gano_visitante'])
        equipo_resultadoe = float (equipo_local [ 'empato_local'])  + float (equipo_visitante ['empato_visitante'])
        equipo_resultadop = float (equipo_local [ 'perdio_local']) - float (equipo_visitante['perdio_visitante'])
            
        
        if equipo_resultado < 0:
            print (equipovis, 'gana con una probabilidad de', abs(round (equipo_resultado,2)))
        
        elif equipo_resultado > 0:
            print ('')
            print (equipoloc, 'gana con una probabilidad de', round(equipo_resultado,2))
           
        elif equipo_resultado == 0:
            print('no hay probabilidad de ganar para ningún equipo')
            
        print ('El partido queda empatado con una probabilidad de', round (equipo_resultadoe,2))  
         
        
        if equipo_resultadop < 0:
            print (equipovis, 'pierde con una probabilidad de', abs(round (equipo_resultadop,2)))  
      
        elif equipo_resultadop > 0:
            print (equipoloc, 'pierde con una probabilidad de', round(equipo_resultadop,2))
            
        elif equipo_resultadop == 0:
            print('No hay probabilidad de perder de algún equipo')
        
        print('') 
        print ('RESULTADOS GENERALES:')
        print ('')
            

    ##DESDE ACÁ HAY QUE HACER TODOS LOS CONDICIONALES (9)
                
        ## 1. G+, P+ : 
        if (equipo_resultado > 0) and (equipo_resultadop > 0)  :
            
            ### 1.1 G+ < P+     
            if equipo_resultado < equipo_resultadop:
                  
                print (equipovis, 'gana con probabilidad',round ( func1_1(equipo_resultado, equipo_resultadop)),2)
                r1 = (equipovis, round ( func1_1(equipo_resultado, equipo_resultadop)),2)
            ###1.2 G+ > P+
            elif equipo_resultado > equipo_resultadop:
                  
                print (equipoloc, 'gana con una probabilidad de', round ( func1_2 (equipo_resultado, equipo_resultadop)))
                r1 = (equipoloc, round ( func1_2 (equipo_resultado, equipo_resultadop)))
            ### 1.3 G+ = P+    
            else:                  
                print (equipoloc, 'tiene la probabilidad de perder igual a la probabilidad de ganar')
                r1 = (equipoloc, 0)
        ## 2. G+, P- :        
        elif (equipo_resultado > 0) and (equipo_resultadop < 0) :
        
            ### 2.1 G+ > |P-| :
            if equipo_resultado > abs(equipo_resultadop) :
                  
                print (equipoloc, 'gana con una probabilidad de', round ( func2_1(equipo_resultado, abs(equipo_resultadop)),2 ))
                r1 = (equipoloc,round ( func2_1(equipo_resultado, abs(equipo_resultadop)),2 ))
            ### 2.2 G+ < |P-| :
            elif equipo_resultado < abs(equipo_resultadop) :
                  
                print (equipoloc, 'gana con una probabilidad de', round ( func2_2(equipo_resultado, abs(equipo_resultadop)) , 2))
                r1 =(equipoloc, round ( func2_2(equipo_resultado, abs(equipo_resultadop)) , 2))
            ### 2.3 G+ = |P-| :
            else:
                  
                print(equipoloc, 'gana con una probabilidad', round ( func2_3(equipo_resultado, abs (equipo_resultadop)),2))
                r1 = (equipoloc, round ( func2_3(equipo_resultado, abs (equipo_resultadop)),2))
        ## 3. G+, Po :
        elif (equipo_resultado > 0) and (equipo_resultadop == 0) :
            print(equipoloc, 'gana con una probabilidad de', round (equipo_resultado, 2))
            r1 = (equipoloc, round (equipo_resultado, 2))
        
        ## 4. G-, P+ :
        elif (equipo_resultado < 0) and (equipo_resultadop > 0) :
            
            ## 4.1 G- > P+:
            if abs(equipo_resultado) > equipo_resultadop :
                  
                print (equipovis, 'gana con una probabilidad de', round ( func2_1(abs (equipo_resultado), equipo_resultadop), 2))
                r1 = (equipovis,round ( func2_1(abs (equipo_resultado), equipo_resultadop), 2) )
            ## 4.2 G- < P+ :
            elif abs(equipo_resultado) < equipo_resultadop :
                  
                print (equipovis, 'gana con una probabilidad de', round ( func2_2 (abs (equipo_resultado), equipo_resultadop), 2) )
                r1 = (equipovis, round ( func2_2 (abs (equipo_resultado), equipo_resultadop), 2))
            ## 4.3 G- = P+ :
            else:
                  
                print(equipovis, 'gana con una probabilidad', round ( func2_3(abs (equipo_resultado), equipo_resultadop),2))
                r1 = (equipovis, round ( func2_3(abs (equipo_resultado), equipo_resultadop),2) )
        ## 5. G-, P- :
        elif (equipo_resultado < 0) and (equipo_resultadop <= 0) :
                            
            ## 5.1 G- < P-
            if abs (equipo_resultado) < abs (equipo_resultadop) :
                  
                print (equipoloc, 'gana con probabilidad', round ( func1_1(abs (equipo_resultado), abs (equipo_resultadop)), 2))
                r1 = (equipoloc, round ( func1_1(abs (equipo_resultado), abs (equipo_resultadop)), 2))
            ## 5.2 G- > P-
            elif abs (equipo_resultado) > abs (equipo_resultadop) :
                  
                print (equipovis, 'gana con una probabilidad de', round ( func1_2(abs (equipo_resultado), abs(equipo_resultadop)), 2))
                r1 = (equipovis, round ( func1_2(abs (equipo_resultado), abs(equipo_resultadop)), 2) )
            ## 5.3 G- = P-
            elif abs (equipo_resultado) == abs (equipo_resultadop) :
                print(equipovis, 'No tiene probabilidad de ganar')
                r1 = (equipovis, 0)
        ## 6. G-, Po : Se incluyó en 5          
           
        ##7. Go, P+ :
        elif (equipo_resultado == 0) and (equipo_resultadop > 0):
            print(equipovis, 'gana con probabilidad', round (equipo_resultadop, 2))
            r1 = (equipovis,round (equipo_resultadop, 2))
       
        ##8. Go, P- :
        elif (equipo_resultado == 0) and (equipo_resultadop < 0):
            print(equipoloc, 'gana con una probabilidad de ', round (abs (equipo_resultadop), 2))
            r1 = (equipoloc, round (abs (equipo_resultadop), 2))
        ##9. Go, Po :
        elif (equipo_resultado == 0) and (equipo_resultadop == 0):
            print('Ningun equipo tiene probabilidad de ganar')
            r1 = ('Ninguno',0)
        print ('El partido queda empatado con una probabilidad de', round (equipo_resultadoe,2)) 
        r2 = ('empate', round (equipo_resultadoe,2))
        
        print ('')
        print ('––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')
        
        journal = str(equipoloc +' vs ' + equipovis)
        ganador = str(r1[0] +' '+ str(r1[1]))
        empate = str(r2[1])
        
        dicc = {'enfrentamiento': [journal], 'gana': [ganador], 'empata': [empate]}
        
        df = pd.DataFrame(dicc)
        return df
 '''


def PROB_(equipoloc: str, equipovis: str, tabla):

    equipo_local = tabla[tabla.equipo == equipoloc]
    equipo_visitante = tabla[tabla.equipo == equipovis]

    equipo_resultado = float(
        equipo_local['gano_local']) - float(equipo_visitante['gano_visitante'])
    equipo_resultadoe = (float(
        equipo_local['empato_local']) + float(equipo_visitante['empato_visitante'])) / 2
    equipo_resultadop = float(
        equipo_local['perdio_local']) - float(equipo_visitante['perdio_visitante'])

    # DESDE ACÁ HAY QUE HACER TODOS LOS CONDICIONALES (9)

    # 1. G+, P+ :
    if (equipo_resultado > 0) and (equipo_resultadop > 0):

        # 1.1 G+ < P+
        if equipo_resultado < equipo_resultadop:

            r1 = (equipovis, round(func1_1(equipo_resultado, equipo_resultadop)), 2)
        # 1.2 G+ > P+
        elif equipo_resultado > equipo_resultadop:

            r1 = (equipoloc, round(func1_2(equipo_resultado, equipo_resultadop)))
        # 1.3 G+ = P+
        else:
            r1 = (equipoloc, 0)
    # 2. G+, P- :
    elif (equipo_resultado > 0) and (equipo_resultadop < 0):

        # 2.1 G+ > |P-| :
        if equipo_resultado > abs(equipo_resultadop):
            r1 = (equipoloc, round(
                func2_1(equipo_resultado, abs(equipo_resultadop)), 2))

        # 2.2 G+ < |P-| :
        elif equipo_resultado < abs(equipo_resultadop):
            r1 = (equipoloc, round(
                func2_2(equipo_resultado, abs(equipo_resultadop)), 2))

        # 2.3 G+ = |P-| :
        else:
            r1 = (equipoloc, round(
                func2_3(equipo_resultado, abs(equipo_resultadop)), 2))

    # 3. G+, Po :
    elif (equipo_resultado > 0) and (equipo_resultadop == 0):
        r1 = (equipoloc, round(equipo_resultado, 2))

    # 4. G-, P+ :
    elif (equipo_resultado < 0) and (equipo_resultadop > 0):

        # 4.1 G- > P+:
        if abs(equipo_resultado) > equipo_resultadop:
            r1 = (equipovis, round(
                func2_1(abs(equipo_resultado), equipo_resultadop), 2))

        # 4.2 G- < P+ :
        elif abs(equipo_resultado) < equipo_resultadop:
            r1 = (equipovis, round(
                func2_2(abs(equipo_resultado), equipo_resultadop), 2))

        # 4.3 G- = P+ :
        else:
            r1 = (equipovis, round(
                func2_3(abs(equipo_resultado), equipo_resultadop), 2))

    # 5. G-, P- :
    elif (equipo_resultado < 0) and (equipo_resultadop <= 0):

        # 5.1 G- < P-
        if abs(equipo_resultado) < abs(equipo_resultadop):
            r1 = (equipoloc, round(
                func1_1(abs(equipo_resultado), abs(equipo_resultadop)), 2))

        # 5.2 G- > P-
        elif abs(equipo_resultado) > abs(equipo_resultadop):
            r1 = (equipovis, round(
                func1_2(abs(equipo_resultado), abs(equipo_resultadop)), 2))

        # 5.3 G- = P-
        elif abs(equipo_resultado) == abs(equipo_resultadop):
            r1 = (equipovis, 0)

    # 6. G-, Po : Se incluyó en 5

    # 7. Go, P+ :
    elif (equipo_resultado == 0) and (equipo_resultadop > 0):
        r1 = (equipovis, round(equipo_resultadop, 2))

    # 8. Go, P- :
    elif (equipo_resultado == 0) and (equipo_resultadop < 0):
        r1 = (equipoloc, round(abs(equipo_resultadop), 2))

    # 9. Go, Po :
    elif (equipo_resultado == 0) and (equipo_resultadop == 0):
        r1 = ('Ninguno', 0)

    # probabilidad de empate
    r2 = ('empate', round(equipo_resultadoe, 2))

    ganador = str(r1[0] + ' ' + str(r1[1]))
    empate = str(r2[1])

    dicc = {'equipo_local': [equipoloc], 'equipo_visitante': [
        equipovis], 'gana': [r1], 'empata': [empate]}

    df = pd.DataFrame(dicc)

    return df


def pron_prob(liga: int, jornada: str):

    tabla_jornada = journey(liga, jornada)
    base = base_datos(liga, jornada)

    df_t = pd.DataFrame()
    for i in range(len(tabla_jornada)):
        df = PROB_(tabla_jornada.iloc[i]['equipo_local'],
                   tabla_jornada.iloc[i]['equipo_visitante'], base)
        df_t = df_t.append(df)

    df_t.reset_index(inplace=True, drop=True)
    return df_t


# PRUEBA DE ACERTAMIENTOS

def resultado_prueba_bundesliga(jornada: str):
    jornada = int(jornada)
    url = url_jornada_bundesliga(str(jornada))
    resultado_jornada = resultado_por_jornada_bundesliga(url)

    return resultado_jornada


'''jornada = '12'
jornada = int(jornada)    
url = url_jornada_bundesliga(str(jornada))
resultado_jornada = resultado_por_jornada_bundesliga(url)
resultado_jornada['resultado'] = 0

for i in range(len(resultado_jornada)):
    marcador = resultado_jornada.loc[i,'marcador']
    indice = marcador.index(':')
    equipo_local = resultado_jornada.loc[i,'equipo_local']
    equipo_visitante = resultado_jornada.loc[i,'equipo_visitante']
    if int(marcador[: indice]) > int(marcador[indice+1 :]):
        resultado_jornada.loc[i, 'resultado']= equipo_local
    
    
    elif int(marcador[: indice]) < int(marcador[indice+1 :]):
        resultado_jornada.loc[i, 'resultado'] = equipo_visitante
        
        
    else:
        resultado_jornada.loc[i, 'resultado'] = 'empate'


df = pron_prob(2, '12')


df_t = pd.merge(df, resultado_jornada, on=['equipo_local','equipo_visitante'])'''


# el pronostico es una combinación de las dos probabilidades (gana y empata)

# debo calibrar cada una de las probabilidades y luego calibrar el pronóstico

# es decir, si defino el pronostico como: alpha * gana + beta * empata

# primero calibro gana y empata y luego alpha y beta
