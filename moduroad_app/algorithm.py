
import osmnx as ox
import networkx as nx
import pandas as pd
import math
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
from shapely.geometry import MultiLineString
# 여기에 길찾기 로직을 함수로 구현합니다.
def find_shortest_path(start, end, network, speed_kmph=3.7):
   
    G = network
    G.graph['crs'] = 'epsg:4326'
   
    # 가장 가까운 노드 찾기
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    
    # A* 알고리즘으로 최단 경로 찾기
    route = nx.astar_path(G, start_node, end_node, weight='weight')  # 여기서 'weight'를 'length'로 수정해야 합니다.
    
    # 라인 출력 및 거리, 시간 계산
    line_strings = []
    total_length = 0  # 총 이동 거리
    total_time = 0  # 총 이동 시간
    
    for i in range(len(route)-1):
        source = route[i]
        target = route[i+1]
        edge_data = G.get_edge_data(source, target, 0)
        
        if edge_data and 'geometry' in edge_data:
            line_strings.append(edge_data['geometry'])
            edge_length = edge_data['weight']  # 엣지 길이
            total_length += edge_length
        else:
            print(f"경로상의 노드 쌍 {source} -> {target} 사이의 엣지를 찾을 수 없습니다.")
    
    # 시간 계산 (시간 = 거리 / 속도)
    # 속도를 m/s로 변환
    speed_mps = (speed_kmph * 1000) / 3600
    total_time = (total_length / speed_mps) //60
    
    # 모든 LineString 객체들을 하나로 합침
    combined_line_string = linemerge(line_strings)

    if isinstance(combined_line_string, MultiLineString):
        line_list = [list(line.coords) for line in combined_line_string.geoms]
        flat_list = [item for sublist in line_list for item in sublist]
    else:
        line_list = list(combined_line_string.coords)
        flat_list = line_list

    if total_length >= 1000:
        total_length = f"{total_length / 1000:.1f}km"
    else:
        total_length = f"{total_length:.0f}m"
    
    total_time = f"{total_time:.0f}분"




    return flat_list, total_length, total_time
    
    

#--------------------------------------------------------------------------------------------------------------------#
#test

