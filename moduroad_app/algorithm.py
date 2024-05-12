
import osmnx as ox
import networkx as nx
import pandas as pd
import math
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
from shapely.geometry import MultiLineString
import json
# 여기에 길찾기 로직을 함수로 구현합니다.
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
def point_to_dict(point):
    print(type(point.y))
    return [point.x, point.y]

def find_shortest_path(start, end, network, types):
    speed_kmph = 0
    weights = ''
    #설정 값
    #type: general/wheel/elder
    if types == 'normal':
        speed_kmph = 3.7
        weights = 'length'
    elif types == 'wheelchair':
        speed_kmph = 2.7
        weights = 'w_weight'
    elif types == 'elderly':
        speed_kmph = 2.7
        weights = 'e_weight'
    
    G = network
    G.graph['crs'] = 'epsg:4326'    
    # 가장 가까운 노드 찾기
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    # 가중치 속성이 각 간선에 실제로 존재하는지 확인
    weight_exists = all(weights in data for _, _, data in G.edges(data=True))

    if weight_exists:
        # 모든 간선에 가중치 속성이 존재하면 A* 알고리즘 실행
        route = nx.astar_path(G, start_node, end_node, weight=weights)
        #print("경로 찾기 성공:", route)
    else:
        # 가중치 속성이 없는 간선이 있으면 경고 메시지 출력
        raise AttributeError(f"경고: '{weights}' 속성이 모든 간선에 존재하지 않습니다.")
    # A* 알고리즘으로 최단 경로 찾기
    route = nx.astar_path(G, start_node, end_node, weight = weights)  
    
    # 라인 출력 및 거리, 시간 계산
    line_strings = []
    obstacles = []
    total_length = 0  # 총 이동 거리
    total_time = 0  # 총 이동 시간
    obstacle_keys = ['slope', 'stair_steep', 'bollard','crosswalk_curb', 'sidewalk_curb']  # 장애물 키 목록

    for i in range(len(route)-1):  # 루트 내 엣지 반복
        source = route[i]
        target = route[i+1]
        edge_data = G.get_edge_data(source, target, 0)
        
        if edge_data !=0:
            line_strings.append(edge_data['geometry'])
            edge_length = edge_data['length']  # 엣지 길이
            total_length += edge_length

            for key in obstacle_keys:
                if key in edge_data:
                    # 장애물 키가 이미 obstacles 내의 어떤 사전에도 존재하지 않는 경우, 새 사전을 추가합니다.
                    found = False
                    for obstacle_dict in obstacles:
                        if key in obstacle_dict:
                            if edge_data[key] !=0:
                                obstacle_points = []
                                for point in edge_data[key]:
                                    # Point 객체를 직렬화 가능한 딕셔너리로 변환합니다.
                                    point_dict = point_to_dict(point)
                                    obstacle_points.append(point_dict)
                                if not found:
                                    # 이미 변환된 딕셔너리 리스트를 obstacles에 추가합니다.
                                    obstacles.append({key: obstacle_points})
                                else:
                                    # 기존에 key가 존재하는 경우, 해당 키에 대한 리스트를 업데이트합니다.
                                    obstacle_dict[key].extend(obstacle_points)

                                found = True
                                break
                    if not found:
                        if edge_data[key] !=0:
                            obstacle_points = []
                            for point in edge_data[key]:
                                # Point 객체를 직렬화 가능한 딕셔너리로 변환합니다.
                                point_dict = point_to_dict(point)
                                obstacle_points.append(point_dict)
                            if not found:
                                # 이미 변환된 딕셔너리 리스트를 obstacles에 추가합니다.
                                obstacles.append({key: obstacle_points})
                            else:
                                # 기존에 key가 존재하는 경우, 해당 키에 대한 리스트를 업데이트합니다.
                                obstacle_dict[key].extend(obstacle_points)
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




    return flat_list, total_length, total_time, obstacles
    
    

#--------------------------------------------------------------------------------------------------------------------#
#test

