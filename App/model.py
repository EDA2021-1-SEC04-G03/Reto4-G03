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
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from math import radians, cos, sin, asin, sqrt
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
                    'landingPointsCapital': None,
                    'countries': None
                    }

        analyzer['landingPoints'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareStopIds)

        analyzer['landingPointsGeo'] = lt.newList('ARRAY_LIST')

        analyzer['landingPointsCapital'] = lt.newList('ARRAY_LIST')
        
        analyzer['countries'] = lt.newList('ARRAY_LIST')
        
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
        addRouteStop(analyzer, connection['cable_name'], connection['\ufefforigin'])
        addRouteStop(analyzer, connection['cable_name'], connection['destination'])
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


def addRouteStop(analyzer, cable_name, landingPointId):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    entry = m.get(analyzer['landingPoints'], landingPointId)
    if entry is None:
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, cable_name)
        m.put(analyzer['landingPoints'], landingPointId, lstroutes)
    else:
        lstroutes = entry['value']
        info = cable_name
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
    return

def createGroundConnections(analyzer, origin, destination, originIndex, destIndex, distance, cable_name):
    addStop(analyzer, destination)
    addConnection(analyzer, origin, destination, distance)
    addConnection(analyzer, destination, origin, distance)
    addRouteStop(analyzer, cable_name, originIndex)
    addRouteStop(analyzer, cable_name, destIndex)
    return

def addCapitalToList(analyzer, country, vertexname):
    lt.addLast(analyzer['landingPointsCapital'], (country,vertexname))
    return

def addGroundConnections(analyzer):
    """
    Por cada vertice (cada estacion) se recorre la lista
    de rutas servidas en dicha estación y se crean
    arcos entre ellas para representar el cambio de ruta
    que se puede realizar en una estación.
    """
    originIndex=20000
    cableNamePreffix='Ground Connections '

    for country in lt.iterator(analyzer['countries']):

        cableName=cableNamePreffix + country['CountryName']
        origin = str(originIndex) + '-' + cableName
        addStop(analyzer, origin)
        addCapitalToList(analyzer, country['CountryName'], origin)
        foundLpInCountry=False

        #se crean conexiones desde el nuevo lp en la capital hasta todas las que haya en el pais
        for landingpoint in lt.iterator(analyzer['landingPointsGeo']):
            if landingpoint['name'].split(', ')[-1]==country['CountryName']:
                destination=landingpoint['landing_point_id']+'-'+cableName
                distance=haversine(float(country['CapitalLatitude']),float(country['CapitalLongitude']),
                    float(landingpoint['latitude']),float(landingpoint['longitude']))
                createGroundConnections(analyzer, origin, destination, str(originIndex),
                    landingpoint['landing_point_id'], distance, cableName)
                foundLpInCountry=True
        
        #si no hay lp en el pais busca la más cercana y se crea conexión
        if foundLpInCountry==False and country['CountryName']!='':
            closestLp=None
            minDistance=10000000
            for landingpoint in lt.iterator(analyzer['landingPointsGeo']):
                distance=haversine(float(country['CapitalLatitude']),float(country['CapitalLongitude']),
                    float(landingpoint['latitude']),float(landingpoint['longitude']))
                if distance<minDistance:
                    closestLp=landingpoint
                    minDistance=distance
            destination=closestLp['landing_point_id']+'-'+cableName
            createGroundConnections(analyzer, origin, destination, str(originIndex),
                    closestLp['landing_point_id'], minDistance, cableName)

        originIndex+=1
    return

def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, distance)
    return analyzer

def addLandingPoint(analyzer, landingPoint):
    lt.addLast(analyzer['landingPointsGeo'], landingPoint)
    #m.put(analyzer['landingPointsGeo'], landingPoint['landing_point_id'], landingPoint)
    return

def addCountry(analyzer, country):
    lt.addLast(analyzer['countries'], country)
    #m.put(analyzer['countries'], country['CountryName'], country)
    return

def connectedComponents(analyzer):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    return scc.connectedComponents(analyzer['components'])

# Funciones para creacion de datos

# Funciones de consulta

def minimumCostPaths(analyzer, initialStation):
    """
    Calcula los caminos de costo mínimo desde la estacion initialStation
    a todos los demas vertices del grafo
    """
    analyzer['paths'] = djk.Dijkstra(analyzer['connections'], initialStation)
    return analyzer

def minimumCostPath(analyzer, destStation):
    """
    Retorna el camino de costo minimo entre la estacion de inicio
    y la estacion destino
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    path = djk.pathTo(analyzer['paths'], destStation)
    return path

def areLpInSameCluster(analyzer, lp1, lp2):
    foundLp1=False
    foundLp2=False
    lp1Id=''
    lp2Id=''

    for landingpoint in lt.iterator(analyzer['landingPointsGeo']):
            if not foundLp1 and landingpoint['name'].split(', ')[0]==lp1:
                lp1Id=landingpoint['landing_point_id']
                foundLp1=True
                if foundLp2:
                    break
            elif not foundLp2 and landingpoint['name'].split(', ')[0]==lp2:
                lp2Id=landingpoint['landing_point_id']
                foundLp2=True
                if foundLp1:
                    break
    
    lp1List=m.get(analyzer['landingPoints'], lp1Id)['value']
    lp2List=m.get(analyzer['landingPoints'], lp2Id)['value']

    haveSameCluster=False

    for route in lt.iterator(lp1List):
        for route2 in lt.iterator(lp2List):
            if route==route2:
                print("Pasan por la misma ruta:",route)
                haveSameCluster=True
    
    return haveSameCluster

def getCapitalLps(analyzer, countryA, countryB):
    capitalVertexA=''
    capitalVertexB=''
    
    foundLp1=False
    foundLp2=False
    #0 country 1 vertex name
    for country in lt.iterator(analyzer['landingPointsCapital']):
        if not foundLp1 and country[0]==countryA:
            capitalVertexA=country[1]
            foundLp1=True
            if foundLp2:
                break
        elif not foundLp2 and country[0]==countryB:
            capitalVertexB=country[1]
            foundLp2=True
            if foundLp1:
                break

    return capitalVertexA, capitalVertexB

def getFirstLandingPoint(analyzer):
    #lt.lastElement(m.valueSet(analyzer['landingPointsGeo']))
    return lt.firstElement(analyzer['landingPointsGeo'])

def getLastCountryInfo(analyzer):
    #lt.lastElement(m.valueSet(analyzer['countries']))
    return lt.lastElement(analyzer['countries'])

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

def maxLandPoints(analyzer):
    landingPoints = analyzer['landingPoints']
    keyList = m.keySet(landingPoints)
    currentMax = 0
    maxList = []

    
    for key in lt.iterator(keyList):
        keySize = m.get(landingPoints,key)['value']['size']
        if(currentMax > keySize):
            continue
        elif(currentMax < keySize):
            currentMax = keySize
            maxList = [key]
        elif(currentMax == keySize):
            maxList.append(key) 

    results = (maxList,currentMax)
    
    return results


    



# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento

# Funciones helper

def haversine(lat1,lon1, lat2,lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def formatVertex(landingPoint, connection):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = landingPoint + '-'
    name = name + connection['cable_name']
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