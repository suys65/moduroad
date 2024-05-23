import osmnx as ox
import networkx as nx
import pandas as pd
import math
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
from shapely.geometry import MultiLineString

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
def point_to_dict(point):
    return [point.x, point.y]

def find_shortest_path(start, end, network, types):
    speed_kmph = 0
    weights = ''
    
    # 설정 값
    if types == 'normal':
        speed_kmph = 3.7
        weights = 'length'
    elif types == 'wheelchair':
        speed_kmph = 2.7
        weights = 'w_weight'
    elif types == 'elderly':
        speed_kmph = 2.7
        weights = 'e_weight'
    else:
        raise ValueError(f"Unknown type: {types}")
    
    G = network
    G.graph['crs'] = 'epsg:4326'
    
    # 가장 가까운 노드 찾기
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    
    # 가중치 속성이 각 간선에 실제로 존재하는지 확인
    for _, _, data in G.edges(data=True):
        if weights not in data:
            raise AttributeError(f"경고: '{weights}' 속성이 모든 간선에 존재하지 않습니다.")
    
    # A* 알고리즘으로 최단 경로 찾기
    route = nx.astar_path(G, start_node, end_node, weight=weights)
    
    # 라인 출력 및 거리, 시간 계산
    line_strings = []
    obstacles = []
    total_length = 0  # 총 이동 거리
    total_time = 0  # 총 이동 시간
    obstacle_keys = ['slope', 'stair_steep', 'bollard', 'crosswalk_curb', 'sidewalk_curb']  # 장애물 키 목록

    for i in range(len(route)-1):  # 루트 내 엣지 반복
        source = route[i]
        target = route[i+1]
        edge_data = G.get_edge_data(source, target, 0)

        if edge_data != 0:
            line_strings.append(edge_data['geometry'])
            edge_length = edge_data['length']  # 엣지 길이
            total_length += edge_length

            for key in obstacle_keys:
                if key in edge_data and edge_data[key] != 0:
                    obstacle_points = []
                    for point in edge_data[key]:
                        point_dict = point_to_dict(point)
                        obstacle_points.append(point_dict)
                    obstacles.append({"type": key, "points": obstacle_points})  # 장애물 타입을 명시적으로 추가
        else:
            print(f"경로상의 노드 쌍 {source} -> {target} 사이의 엣지를 찾을 수 없습니다.")

    
    # 시간 계산 (시간 = 거리 / 속도)
    speed_mps = (speed_kmph * 1000) / 3600
    total_time = (total_length / speed_mps) // 60
    
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

    return flat_list, total_length, total_time, obstacles