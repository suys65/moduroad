import streamlit as st
import osmnx as ox
import networkx as nx
import pickle
import folium
from shapely.ops import linemerge
from shapely.geometry import MultiLineString
from streamlit_folium import folium_static

def find_shortest_path(start, end, network, speed_kmph=3.7):
    """
    start: 시작점 좌표 (위도, 경도)
    end: 도착점 좌표 (위도, 경도)
    network: 네트워크 그래프
    speed_kmph: 평균 이동 속도(km/h)
    """
    G = network
    G.graph['crs'] = 'epsg:4326'
   
    # 가장 가까운 노드 찾기
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    
    # A* 알고리즘으로 최단 경로 찾기
    route = nx.astar_path(G, start_node, end_node, weight='length')  # 여기서 'weight'를 'length'로 수정해야 합니다.
    
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
            edge_length = edge_data['length']  # 엣지 길이
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
        #print("리스트")
        #print(flat_list)

    if total_length >= 1000:
        total_length = f"{total_length / 1000:.2f}km"
    else:
        total_length = f"{total_length}m"
    
    total_time = f"{total_time:.0f}분"




    return combined_line_string, total_length, total_time

    

#--------------------------------------------------------------------------------------------------------------------#
#test
# 기존에 정의한 find_shortest_path 함수를 사용

# Streamlit 앱 레이아웃 설정
st.title('Shortest Path Finder')

# 입력을 위한 사이드바 설정
st.sidebar.header('Input Coordinates')

# 출발지의 위도와 경도 입력
st.sidebar.subheader('Start Point:')
start_lat = st.sidebar.text_input('Start Latitude', '37.3774689')
start_lon = st.sidebar.text_input('Start Longitude', '126.6349327')

# 도착지의 위도와 경도 입력
st.sidebar.subheader('End Point:')
end_lat = st.sidebar.text_input('End Latitude', '37.3761117')
end_lon = st.sidebar.text_input('End Longitude', '126.6345200')

# 속도 입력 (기본값은 3.7km/h)
speed_kmph = st.sidebar.number_input('Speed (km/h)', value=3.7)

# 경로 계산 버튼
if st.sidebar.button('Find Shortest Path'):
    start = (float(start_lat), float(start_lon))
    end = (float(end_lat), float(end_lon))
    
    # 네트워크 그래프 로딩 
    file_path = 'C:/my_code/moduroad/moduroad_app/cashe_data/api_graph.pickle'
    with open(file_path, 'rb') as file:
        network_g = pickle.load(file)
    
    # 최단 경로 계산
    combined_line_string, total_length, total_time = find_shortest_path(start, end, network_g, speed_kmph=speed_kmph)
    
    # 결과 출력
    st.write(f"총 거리: {total_length}\n소요 시간: {total_time}")
    
    # Folium 지도 생성
    m = folium.Map(location=[(float(start_lat) + float(end_lat)) / 2, (float(start_lon) + float(end_lon)) / 2], zoom_start=14)
    
    # 최단 경로를 지도에 추가
    if not combined_line_string.is_empty:
        folium.GeoJson(combined_line_string, style_function=lambda x: {'color': 'blue', 'weight': 5}).add_to(m)
        
        # 시작과 끝 지점에 마커 추가
        folium.Marker(location=start, popup='Start', icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(location=end, popup='End', icon=folium.Icon(color='red')).add_to(m)
        
        # 지도를 Streamlit에 표시
        folium_static(m)
    else:
        st.error("지도에 추가할 LineString이 없습니다.")
else:
    st.write('Enter the start and end coordinates and press "Find Shortest Path".')

# Streamlit 앱 실행을 위해 커맨드 라인에 'streamlit run app.py' 입력
