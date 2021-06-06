"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
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
import model
import csv


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de libros

def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    loadLandingPoints(analyzer,'landing_points.csv')
    loadCountries(analyzer,'countries.csv')
    loadServices(analyzer,'connections.csv')
    return analyzer

# Funciones para la carga de datos

def loadLandingPoints(analyzer, servicesfile):
    """
    Carga los libros del archivo.  Por cada libro se indica al
    modelo que debe adicionarlo al catalogo.
    """
    videosfile = cf.data_dir + servicesfile
    input_file = csv.DictReader(open(videosfile, encoding='utf-8'))

    for landingPoint in input_file:
        model.addLandingPoint(analyzer, landingPoint)
    return analyzer

def loadCountries(analyzer, servicesfile):
    """
    Carga los libros del archivo.  Por cada libro se indica al
    modelo que debe adicionarlo al catalogo.
    """
    videosfile = cf.data_dir + servicesfile
    input_file = csv.DictReader(open(videosfile, encoding='utf-8'))

    for country in input_file:
        model.addCountry(analyzer, country)
    return analyzer

def loadServices(analyzer, servicesfile):
    """
    Carga los datos de los archivos CSV en el modelo.
    Se crea un arco entre cada par de estaciones que
    pertenecen al mismo servicio y van en el mismo sentido.

    addRouteConnection crea conexiones entre diferentes rutas
    servidas en una misma estación.
    """
    servicesfile = cf.data_dir + servicesfile
    input_file = csv.DictReader(open(servicesfile, encoding="utf-8"),
                                delimiter=",")

    for connection in input_file:
        model.addStopConnection(analyzer, connection)
        model.addConnectionList(analyzer, connection)
    model.addGroundConnections(analyzer)
    model.addRouteConnections(analyzer)
    return analyzer

def getIPCountry(ip):
    return model.getIPCountry(ip)

def createMap(analyzer):
    return model.createMap(analyzer)

# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo

def getCapitalLps(analyzer, countryA, countryB):
    return model.getCapitalLps(analyzer, countryA, countryB)

def minimumCostPaths(analyzer, initialStation):
    """
    Calcula todos los caminos de costo minimo de initialStation a todas
    las otras estaciones del sistema
    """
    return model.minimumCostPaths(analyzer, initialStation)

def minimumCostPath(analyzer, destStation):
    """
    Retorna el camino de costo minimo desde initialStation a destStation
    """
    return model.minimumCostPath(analyzer, destStation)

def connectedComponents(analyzer):
    """
    Numero de componentes fuertemente conectados
    """
    return model.connectedComponents(analyzer)

def areLpInSameCluster(analyzer, lp1, lp2):
    return model.areLpInSameCluster(analyzer, lp1, lp2)

def hasPath(analyzer, destStation):
    """
    Informa si existe un camino entre initialStation y destStation
    """
    return model.hasPath(analyzer, destStation)

def getFirstLandingPoint(analyzer):
    return model.getFirstLandingPoint(analyzer)

def getLastCountryInfo(analyzer):
    return model.getLastCountryInfo(analyzer)

def landingPointsSize(analyzer):
    return model.landingPointsSize(analyzer)

def countriesSize(catalog):

    return model.countriesSize(catalog)

def totalStops(analyzer):
    """
    Total de paradas de autobus
    """
    return model.totalStops(analyzer)

def totalConnections(analyzer):
    """
    Total de enlaces entre las paradas
    """
    return model.totalConnections(analyzer)

def maxLandPoints(analyzer):
    return model.maxLandPoints(analyzer)

def getCountriesInLp(analyzer, lp):
    return model.getCountriesInLp(analyzer, lp)