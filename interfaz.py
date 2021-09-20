import logic as log
import pandas as pd
from tabulate import tabulate


def ejecutar_prob_anotar_goles(liga: int):
    tabla = ejecutar_tabla_de_posiciones(liga)
    jornada = ejecutar_jornada(liga)
    tabla_probabilidades = log.prob_anotar_goles_jornada(tabla, jornada)

    for i in range(len(tabla_probabilidades)):
        print('')
        print('\033[42m' + " Partido " + str(i + 1) + '\x1b[0m')
        print('')
        print(tabla_probabilidades.iloc[i, 0],
              ':', tabla_probabilidades.iloc[i, 2])
        print(tabla_probabilidades.iloc[i, 1],
              ':', tabla_probabilidades.iloc[i, 3])
        print('')
    df = tabla_probabilidades.sort_values(
        'probabilidad_anotar_goles_local', ascending=False, ignore_index=True)

    df1 = df[["equipo_local", "probabilidad_anotar_goles_local"]]

    df = tabla_probabilidades.sort_values(
        'probabilidad_anotar_goles_visitante', ascending=False, ignore_index=True)

    df2 = df[["equipo_visitante", "probabilidad_anotar_goles_visitante"]]

    result = pd.concat([df1, df2], axis=1, join='inner')
    result.rename(columns={'equipo_local': 'local', 'equipo_visitante': 'visitante',
                  'probabilidad_anotar_goles_local': 'prob', 'probabilidad_anotar_goles_visitante': 'prob'}, inplace=True)

    print('\033[42m' + " PROBABILIDAD DE ANOTAR GOLES " + '\x1b[0m')
    print(tabulate(result, headers='keys', tablefmt='psql', showindex='never'))


def ejecutar_prob_le_anoten_goles(liga: int):
    tabla = ejecutar_tabla_de_posiciones(liga)
    jornada = ejecutar_jornada(liga)
    tabla_probabilidades = log.prob_le_anoten_goles_jornada(tabla, jornada)

    for i in range(len(tabla_probabilidades)):
        print('')
        print('\033[42m' + " Partido " + str(i + 1) + '\x1b[0m')
        print('')
        print(tabla_probabilidades.iloc[i, 0],
              ':', tabla_probabilidades.iloc[i, 2])
        print(tabla_probabilidades.iloc[i, 1],
              ':', tabla_probabilidades.iloc[i, 3])
        print('')

    df = tabla_probabilidades.sort_values(
        'probabilidad_le_anoten_goles_local', ascending=True, ignore_index=True)
    df1 = df[["equipo_local", "probabilidad_le_anoten_goles_local"]]

    df = tabla_probabilidades.sort_values(
        'probabilidad_le_anoten_goles_visitante', ascending=True, ignore_index=True)
    df2 = df[["equipo_visitante", "probabilidad_le_anoten_goles_visitante"]]

    result = pd.concat([df1, df2], axis=1, join='inner')
    result.rename(columns={'equipo_local': 'local', 'equipo_visitante': 'visitante',
                  'probabilidad_le_anoten_goles_local': 'prob', 'probabilidad_le_anoten_goles_visitante': 'prob'}, inplace=True)
    print('\033[42m' + " PROBABILIDAD DE QUE LE ANOTEN GOLES " + '\x1b[0m')
    print(tabulate(result, headers='keys', tablefmt='psql', showindex='never'))


def ejecutar_tabla_de_posiciones(liga: int):
    tabla = log.tabla_de_posiciones(liga)
    return tabla


def ejecutar_pron_prob(liga: int):
    jornada = input('jornada: ')
    respuesta = log.pron_prob(liga, jornada)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print('')
    print(tabulate(respuesta, headers='keys', tablefmt='psql'))


def ejecutar_jornada(liga: int):
    jornada = input('jornada: ')
    respuesta = log.journey(liga, jornada)
    return respuesta


def imprimir_jornada(liga) -> None:
    jornada = ejecutar_jornada(liga)
    partidos = []
    for i in range(len(jornada)):
        partido = str(jornada.iloc[i, 0] + " vs " + jornada.iloc[i, 1])
        partidos.append(partido)

    partidos = pd.DataFrame({"Partidos": partidos})
    partidos.index = list(range(1, len(partidos) + 1))
    print('')
    print(tabulate(partidos, headers='keys', tablefmt='psql'))


def imprimir_tabla(liga):
    tabla = ejecutar_tabla_de_posiciones(liga)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print('')
    print(tabulate(tabla, headers='keys', tablefmt='psql'))


def MENU() -> None:
    print('')
    print("Ligas disponibles")
    print("1. Premier League")
    print("2. Bundesliga")
    print("3. Salir del menu")


def submenu() -> None:
    print('')
    print("MENÚ DE OPCIONES")
    print("1. Mirar tabla de posiciones")
    print("2. Mirar jornada")
    print("3. Mirar probabilidades")
    print("4. Salir del submenu")


def inicializar():
    respuesta = True

    while respuesta == True:
        MENU()
        opcion = int(input("Escoja la opcion: "))

        if opcion == 1 or opcion == 2:
            liga = opcion
            respuesta2 = True
            while respuesta2 == True:
                submenu()
                opcion2 = int(input("Escoja la opcion: "))
                if opcion2 == 1:
                    imprimir_tabla(liga)

                elif opcion2 == 2:
                    imprimir_jornada(liga)

                elif opcion2 == 3:
                    print('')
                    print('1. Anotar goles')
                    print('2. Le anoten goles')
                    print('3. Pronosticos')
                    print('')
                    opcion3 = input("Escoja opción: ")
                    if opcion3 == "1":
                        ejecutar_prob_anotar_goles(liga)

                    elif opcion3 == "2":
                        ejecutar_prob_le_anoten_goles(liga)

                    elif opcion3 == "3":
                        ejecutar_pron_prob(liga)

                elif opcion2 == 4:
                    respuesta2 = False

        elif opcion == 3:
            respuesta = False


inicializar()
