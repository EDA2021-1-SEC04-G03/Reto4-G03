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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Utils import error as error
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'landingPoints': None,
                    'connections': None,
                    'components': None,
                    'paths': None,
                    'landingPointsGeo': None,
                    'countries': None
                    }

        analyzer['landingPoints'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareStopIds)

        analyzer['landingPointsGeo'] = m.newMap(1300,
                                   maptype='PROBING',
                                   comparefunction=None)
        
        analyzer['countries'] = m.newMap(250,
                                   maptype='PROBING',
                                   comparefunction=None)
        
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al catalogo

def addStopConnection(analyzer, connection):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        origin = formatVertex(connection['\ufefforigin'],connection)
        destination = formatVertex(connection['destination'],connection)
        cable_length=connection['cable_length']
        if cable_length=='n.a.':
            distance=0.0
        else:
            distance = float(connection['cable_length'].replace(' km','').replace(',', ''))
        addStop(analyzer, origin)
        addStop(analyzer, destination)
        addConnection(analyzer, origin, destination, distance)
        addRouteStop(analyzer, connection, connection['\ufefforigin'])
        addRouteStop(analyzer, connection, connection['destination'])
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addStopConnection')


def addStop(analyzer, landingpointid):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['connections'], landingpointid):
            gr.insertVertex(analyzer['connections'], landingpointid)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addstop')


def addRouteStop(analyzer, service, landingPointId):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    entry = m.get(analyzer['landingPoints'], landingPointId)
    if entry is None:
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, service['cable_id'])
        m.put(analyzer['landingPoints'], landingPointId, lstroutes)
    else:
        lstroutes = entry['value']
        info = service['cable_id']
        if not lt.isPresent(lstroutes, info):
            lt.addLast(lstroutes, info)
    return analyzer


def addRouteConnections(analyzer):
    """
    Por cada vertice (cada estacion) se recorre la lista
    de rutas servidas en dicha estación y se crean
    arcos entre ellas para representar el cambio de ruta
    que se puede realizar en una estación.
    """
    lststops = m.keySet(analyzer['landingPoints'])
    for key in lt.iterator(lststops):
        lstroutes = m.get(analyzer['landingPoints'], key)['value']
        prevrout = None
        for route in lt.iterator(lstroutes):
            route = key + '-' + route
            if prevrout is not None:
                addConnection(analyzer, prevrout, route, 0.1)
                addConnection(analyzer, route, prevrout, 0.1)
            prevrout = route


def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, distance)
    return analyzer

def addLandingPoint(analyzer, landingPoint):
    m.put(analyzer['landingPointsGeo'], landingPoint['landing_point_id'], landingPoint)
    return

def addCountry(analyzer, country):
    m.put(analyzer['countries'], country['CountryName'], country)
    return

# Funciones para creacion de datos

# Funciones de consulta

def landingPointsSize(analyzer):
    """
    Numero de autores en el catalogo
    """
    return m.size(analyzer['landingPointsGeo'])

def countriesSize(analyzer):
    """
    Numero de autores en el catalogo
    """
    return m.size(analyzer['countries'])

def totalStops(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento

# Funciones helper

def formatVertex(landingPoint, connection):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = landingPoint + '-'
    name = name + connection['cable_id']
    return name

# Funciones de comparación

def compareStopIds(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1


def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1