from inference_sdk import InferenceHTTPClient
from PIL import Image
from flask import Flask, request, jsonify
import osmnx as ox

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TIcrpEjP7QDYM8tnrZG4"
)


def calculate_edge_weights(edge_data, e_length_weight, e_obstacle_weights, w_length_weight, w_obstacle_weights):
  
    # e_weight 계산
    e_total_weight = edge_data.get('length', 0) * e_length_weight
    for obstacle, weight in e_obstacle_weights.items():
        if obstacle in edge_data and edge_data[obstacle] != 0:
            num_obstacles = len(edge_data[obstacle]) if isinstance(edge_data[obstacle], list) else 0
            e_total_weight += num_obstacles * weight
    edge_data['e_weight'] = e_total_weight

    # w_weight 계산
    w_total_weight = edge_data.get('length', 0) * w_length_weight
    for obstacle, weight in w_obstacle_weights.items():
        if obstacle in edge_data and edge_data[obstacle] != 0:
            num_obstacles = len(edge_data[obstacle]) if isinstance(edge_data[obstacle], list) else 0
            w_total_weight += num_obstacles * weight
    edge_data['w_weight'] = w_total_weight

    return edge_data
#---------------------------------------------------------------------------------------------------------------------------#
# e_weight 계산을 위한 가중치
e_length_weight = 0.164
e_obstacle_weights = {
    'slope': 0.195,
    'stair_steep': 0.268,
    'bollard': 0.069,
    'crosswalk_curb': 0.069,
    'sidewalk_curb': 0.069
}

# w_weight 계산을 위한 가중치 (예시로 임의의 값을 사용함)
w_length_weight = 0.045
w_obstacle_weights = {
    'slope': 0.182,
    'stair_steep': 10,
    'bollard': 0.253,
    'crosswalk_curb': 0.253,
    'sidewalk_curb': 0.253
}


#------------------------------------------------------------------------------------------------------------------------------------------#
# 장애물 가까이에 있는 엣지 가중치 증가 함수 정의
def update_edge_weights(G, point, attribute_name):
    # 가장 가까운 엣지 찾기
    G.graph['crs'] = 'epsg:4326'
    nearest_edge_nodes = ox.distance.nearest_edges(G, X=point.x, Y=point.y)  # OSMnx는 (y, x) 형식으로 좌표를 사용합니다.
    # nearest_edge_nodes는 (u, v, key) 형태의 튜플입니다.
    u, v, key = nearest_edge_nodes
    # 해당 엣지의 데이터 가져오기
    nearest_edge = G[u][v][key]   #edge_data
    print(nearest_edge)
    # 가장 가까운 엣지의 가중치 업데이트
    # 시작 지점에 마커 추가
    
    if attribute_name in nearest_edge:
    # 속성 값이 0인지 확인합니다.
        if nearest_edge[attribute_name] == 0:
            # 속성 값이 0이라면, 새로운 포인트를 포함하는 리스트로 변경합니다.
            nearest_edge[attribute_name] = [point]
        elif isinstance(nearest_edge[attribute_name], list):
            # 속성 값이 리스트인 경우, 새로운 포인트를 리스트에 추가합니다.
            nearest_edge[attribute_name].append(point)
        else:
            # 속성 값이 0이 아니고 리스트도 아닌 다른 값인 경우, 그 값을 리스트에 넣고 새로운 포인트도 추가합니다.
            current_value = nearest_edge[attribute_name]
            nearest_edge[attribute_name] = [current_value, point]
            #print("change")
        print(nearest_edge)
        # 함수 호출
        nearest_edge = calculate_edge_weights(nearest_edge, e_length_weight, e_obstacle_weights, w_length_weight, w_obstacle_weights)
        print(nearest_edge)
        return G, jsonify({"success": True,
                           "obstacles": attribute_name})
#-----------------------------------------------------------------------------------------------------------------------------------#
    

def add_obstacles(image, local, G):
    G.graph['crs'] = 'epsg:4326'
    result = CLIENT.infer(image, model_id="stairs_detection-jaj7e/2")
    result1 = CLIENT.infer(image, model_id="wheelchair-g2qh2/1")
    print(result)
    print("222", result1)
    # result["predictions"] 존재 여부에 따라 True 또는 False 반환
    if "predictions" in result and result["predictions"]: #계단 감지 경우
        return update_edge_weights(G, local, attribute_name = 'stair_steep')
    
    #계단이 감지되지 않음
    elif "predictions" in result1 :
        for prediction in result1["predictions"]:
            if prediction["class"] == "bollard":
                return update_edge_weights(G, local, attribute_name='bollard')
            elif prediction["class"] == "sidewalk chin":
                return update_edge_weights(G, local, attribute_name='sidewalk_curb')
            else :
                continue
        return G, jsonify({"success": False})
    
    else : 
        return G, jsonify({"success": False})

