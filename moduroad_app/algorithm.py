
import osmnx as ox
import networkx as nx
import pandas as pd
import math
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
from shapely.geometry import MultiLineString
# 여기에 길찾기 로직을 함수로 구현합니다.
def find_shortest_path(start, end, network):
    
    G = network
    G.graph['crs'] = 'epsg:4326'
   
    # 가장 가까운 노드 찾기
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    
    # A* 알고리즘으로 최단 경로 찾기
    route = nx.astar_path(G, start_node, end_node, weight='weight')
    #라인 출력
    line_strings = []
    
    # 경로에 포함된 노드 쌍을 순회하면서 해당 엣지의 기하학적 형태를 추출
    for i in range(len(route)-1):
        source = route[i]
        target = route[i+1]
        edge_data = G.get_edge_data(source, target, 0)
        
        if edge_data and 'geometry' in edge_data:
            line_strings.append(edge_data['geometry'])
        else:
            print(f"경로상의 노드 쌍 {source} -> {target} 사이의 엣지를 찾을 수 없습니다.")
    
    # 모든 LineString 객체들을 하나로 합침
    combined_line_string = linemerge(line_strings)


    if isinstance(combined_line_string, MultiLineString):
        # MultiLineString 내의 각 LineString에 대한 좌표를 추출
        line_list = [list(line.coords) for line in combined_line_string.geoms]
        # 다중 리스트를 단일 리스트로 평탄화
        flat_list = [item for sublist in line_list for item in sublist]
    else:
        # LineString 객체인 경우 직접 좌표 추출
        line_list = list(combined_line_string.coords)
        flat_list = line_list
    

    return flat_list
    

#--------------------------------------------------------------------------------------------------------------------#
#test

