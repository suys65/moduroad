import streamlit as st
import osmnx as ox
import networkx as nx
import pickle
import folium
from shapely.ops import linemerge
from shapely.geometry import MultiLineString
from streamlit_folium import folium_static

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
def point_to_dict(point):
    return {'x': point.x, 'y': point.y}

def find_shortest_path(start, end, network, type):
   
    #설정 값
    #type: general/wheel/elder
    if type == 'general':
        speed_kmph = 3.7
        weights = 'length'
    elif type == 'wheel':
        speed_kmph = 4
        weights = 'w_weight'
    elif type == 'elder':
        speed_kmph = 2.5
        weights = 'e_weight'

    G = network
    G.graph['crs'] = 'epsg:4326'    
    # 가장 가까운 노드 찾기
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    
    # A* 알고리즘으로 최단 경로 찾기
    route = nx.astar_path(G, start_node, end_node, weight=weights)  # 여기서 'weight'를 'length'로 수정해야 합니다.
    
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

    return combined_line_string, total_length, total_time , obstacles   

#--------------------------------------------------------------------------------------------------------------------#
#test
# 기존에 정의한 find_shortest_path 함수를 사용

# Streamlit 앱 레이아웃 설정
st.title('Shortest Path Finder')

# 입력을 위한 사이드바 설정
st.sidebar.header('Input Coordinates')

# 출발지의 위도와 경도 입력
st.sidebar.subheader('Start Point:')
start_lat = st.sidebar.text_input('Start Latitude', '37.3741001')
start_lon = st.sidebar.text_input('Start Longitude', '126.6342350')

# 도착지의 위도와 경도 입력
st.sidebar.subheader('End Point:')
end_lat = st.sidebar.text_input('End Latitude', '37.3743460')
end_lon = st.sidebar.text_input('End Longitude', '126.6338622')

network_file_path2 = 'C:/my_code/moduroad/moduroad_app/cashe_data/Wheelchair_graph.pickle'

# 경로 계산 버튼
if st.sidebar.button('Find Shortest Path'):
    start = (float(start_lat), float(start_lon))
    end = (float(end_lat), float(end_lon))
    with open(network_file_path2, 'rb') as file:
        network_g = pickle.load(file)
    # 네트워크 그래프 로딩 및 최단 경로 계산 (첫 번째 네트워크)
   
    combined_line_string1, total_length1, total_time1, obstacles1 = find_shortest_path(start, end, network_g, 'general')
    
    # 네트워크 그래프 로딩 및 최단 경로 계산 (두 번째 네트워크)
    combined_line_string2, total_length2, total_time2 ,obstacles2 = find_shortest_path(start, end, network_g, 'wheel')
    
    # 결과 비교 및 출력
    st.write(f"네트워크 1 - 총 거리: {total_length1}, 소요 시간: {total_time1}")
    st.write(f"네트워크 2 - 총 거리: {total_length2}, 소요 시간: {total_time2}")
    
    # Folium 지도 생성
    m = folium.Map(location=[(float(start_lat) + float(end_lat)) / 2, (float(start_lon) + float(end_lon)) / 2], zoom_start=14)
    
    # 첫 번째 네트워크의 최단 경로를 지도에 추가
    if not combined_line_string1.is_empty:
        folium.GeoJson(combined_line_string1, style_function=lambda x: {'color': 'blue', 'weight': 5, 'dashArray': '5, 5'}).add_to(m)
        
    # 두 번째 네트워크의 최단 경로를 지도에 추가
    if not combined_line_string2.is_empty:
        folium.GeoJson(combined_line_string2, style_function=lambda x: {'color': 'red', 'weight': 5}).add_to(m)
        
    # 시작과 끝 지점에 마커 추가
    folium.Marker(location=start, popup='Start', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=end, popup='End', icon=folium.Icon(color='red')).add_to(m)
    
    # 지도를 Streamlit에 표시
    folium_static(m)
    
else:
    st.write('Enter the start and end coordinates and press "Find Shortest Path".')

# Streamlit 앱 실행을 위해 커맨드 라인에 'streamlit run app.py' 입력
