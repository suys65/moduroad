'''
입력 : 사진, 현위치
1. 사진에 장애물이 있는지? true,false
2. 장애물 = point(현위치)
3. 현위치 - 엣지 찾기 (nearest_edge 함수)
4. G/firebase - 그 엣지의 특성 업데이트( 어떤 장애물이냐에따라)

출력 True/False


result = CLIENT.infer(image, model_id="stairs_detection-jaj7e/2")
    
    # result["predictions"] 존재 여부에 따라 True 또는 False 반환
    if "predictions" in result and result["predictions"]:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 200
'''
from inference_sdk import InferenceHTTPClient
from PIL import Image
from flask import Flask, request, jsonify
import osmnx as ox

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TIcrpEjP7QDYM8tnrZG4"
)
# 장애물 가까이에 있는 엣지 가중치 증가 함수 정의
def update_edge_weights(G, point, attribute_name):
    # 가장 가까운 엣지 찾기
    
    nearest_edge_nodes = ox.distance.nearest_edges(G, X=point.x, Y=point.y)  # OSMnx는 (y, x) 형식으로 좌표를 사용합니다.
    print(nearest_edge_nodes)
    # nearest_edge_nodes는 (u, v, key) 형태의 튜플입니다.
    u, v, key = nearest_edge_nodes
    print(nearest_edge_nodes)
    # 해당 엣지의 데이터 가져오기
    nearest_edge = G[u][v][key]
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
    
        return jsonify({"success": True}), 200
    

def find_shortest_path(image, local, G):
    G.graph['crs'] = 'epsg:4326'
    result = CLIENT.infer(image, model_id="stairs_detection-jaj7e/2")
    
    # result["predictions"] 존재 여부에 따라 True 또는 False 반환
    if "predictions" in result and result["predictions"]: #계단 감지 경우
        return update_edge_weights(G, local, attribute_name = 'stair')
    
    else:#계단이 감지되지 않음
        return jsonify({"success": False}), 200






    return 