"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import sys
import controller
import model
from DISClib.ADT import list as lt
from DISClib.ADT import stack
from DISClib.ADT import map as m
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("Bienvenido")
    print("1- Cargar información en el catálogo")
    print("2- Identificar los clústeres de comunicación")
    print("3- Identificar los puntos de conexión críticos de la red")
    print("4- La ruta de menor distancia")
    print("5- Identificar la Infraestructura Crítica de la Red")
    print("6- Análisis de fallas")
    print("7- Los mejores canales para transmitir")
    print("8- La mejor ruta para comunicarme")
    print("9- Graficando los Grafos")

catalog = None
sys.setrecursionlimit(2 ** 20)

"""
Menu principal
"""


while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("Cargando información de los archivos ....")

        cont = controller.init()
        print("\nNumero de landing points cargados:",controller.landingPointsSize(cont))
        print('Total de conexiones entre landing points:',controller.totalConnections(cont))
        print("Numero de paises cargados:",controller.countriesSize(cont))
        
        firstLandingPoint=controller.getFirstLandingPoint(cont)
        print("\nPrimer landing point cargado:")
        print("-Landing point id:",firstLandingPoint['landing_point_id'])
        print("-Nombre:",firstLandingPoint['name'])
        print("-Latitud:",firstLandingPoint['latitude'])
        print("-Longitud:",firstLandingPoint['longitude'])

        lastLandingPoint=controller.getLastCountryInfo(cont)
        print("\nÚltimo país cargado:")
        print("-Pais:",lastLandingPoint['CountryName'])
        print("-Población:",lastLandingPoint['Population'])
        print("-Números de usuarios de internet:",lastLandingPoint['Internet users'],"\n")

        #print('Numero de vertices:',controller.totalStops(cont))

    elif int(inputs[0]) == 2:

        lp1 = input("Nombre del landing point 1: ")
        lp2 = input("Nombre del landing point 2: ")

        print('\nEl número de clusters en la red es de: '+ str(controller.connectedComponents(cont)))
        result = controller.areLpInSameCluster(cont, lp1, lp2)
        if result:
            print("Los landing points están en el mismo clúster\n")
        else:
            print("Los landing points no comparten clúster\n")
    
    elif int(inputs[0]) == 3:
        print('Calculando...')
        result = controller.maxLandPoints(cont)
        if(len(result[0]) > 1):
            print('Los landing points con mas conexiones son:')
        else:
            print('El landing point con mas conexiones es:')
        for i in result[0]:
            print(m.get(cont['landingPoints'],i))
    
    elif int(inputs[0]) == 4:
        countryA = input("Nombre del pais A: ")
        countryB = input("Nombre del pais B: ")

        lps=controller.getCapitalLps(cont, countryA, countryB)
        #lps=('3036-2Africa','3066-Balalink')

        controller.minimumCostPaths(cont, lps[0])
        path = controller.minimumCostPath(cont, lps[1])

        if path is not None:
            pathlen = stack.size(path)
            pesototal=0
            print('El camino pasa por',str(pathlen),'rutas')
            while (not stack.isEmpty(path)):
                stop = stack.pop(path)
                pesototal+=stop['weight']
                print(stop)
            print('La distancia total de la ruta fue de aprox',round(pesototal,2),'km')
        else:
            print('No hay camino')
    
    elif int(inputs[0]) == 6:
        
        lp = input("Nombre del landing point: ")
        countriesAffected = controller.getCountriesInLp(cont, lp)
        print('Calculando...\n')
        print(len(countriesAffected),"paises son afectados por este landing point:")
        for country in countriesAffected:
            print(country[0],"a",country[1],"km")
        print()
    
    else:
        sys.exit(0)
sys.exit(0)
