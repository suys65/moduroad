
# 실행할 메인 파일
from flask import Flask, request, jsonify
import math
from algorithm import find_shortest_path
import pandas as pd
import pickle
from inference_sdk import InferenceHTTPClient
import networkx as nx
#from PIL import Image
import io
import osmnx as ox


app = Flask(__name__, static_url_path='')

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TIcrpEjP7QDYM8tnrZG4"
)


#file_path = 'moduroad_app\cashe_data\graph.graphml'
#network_g = nx.read_graphml(file_path)

file_path_spe = 'moduroad_app/cashe_data/graph_spe.graphml'
 # .pickle 파일 경로 유지

file_path = 'moduroad_app/cashe_data/api_graph.graphml'
with open(file_path, 'rb') as file:
    network_g = pickle.load(file)


@app.route('/find-path', methods=['POST'])
def find_path_api():
    data = request.json
    start = (data['start_lat'], data['start_lon'])
    end = (data['end_lat'], data['end_lon'])
    
    route = find_shortest_path(start, end, network_g)

    # 여기서는 경로(route)를 직접 반환하고 있으나, 실제로는 경로에 대한 상세 정보를 제공하는 것이 좋습니다.
    return jsonify({'route': route})

@app.route('/find-path_spe', methods=['POST'])
def find_path_spe_api():
    data = request.json
    start = (data['start_lat'], data['start_lon'])
    end = (data['end_lat'], data['end_lon'])
    
    route = find_shortest_path(start, end, network_spe)

    # 여기서는 경로(route)를 직접 반환하고 있으나, 실제로는 경로에 대한 상세 정보를 제공하는 것이 좋습니다.
    return jsonify({'route': route})

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return '이미지 파일이 없습니다.', 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # 이미지 파일을 모델에 전달하여 객체 탐지 수행
    result = CLIENT.infer(image, model_id="stairs_detection-jaj7e/2")
    
    # result["predictions"] 존재 여부에 따라 True 또는 False 반환
    if "predictions" in result and result["predictions"]:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 200

if __name__ == '__main__':
    app.run(debug=True)