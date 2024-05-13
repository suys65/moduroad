
# 실행할 메인 파일
from flask import Flask, request, jsonify
import math
from algorithm import find_shortest_path
from add_obstacle import add_obstacles
import pandas as pd
import pickle
from inference_sdk import InferenceHTTPClient
import networkx as nx
#from PIL import Image
import io
import osmnx as ox



app = Flask(__name__, static_url_path='')
network_g = None

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TIcrpEjP7QDYM8tnrZG4"
)
@app.before_first_request
def load_cache_data():
    global network_g
    file_path = 'C:/my_code/moduroad/moduroad_app/cashe_data/Wheelchair_graph.pickle'

    with open(file_path, 'rb') as file:
        network_g = pickle.load(file)
    # 캐시 데이터 로드 로직
    


@app.route('/find-path', methods=['POST'])
def find_path_api():
    data = request.json
    start = (data['start_lat'], data['start_lon'])
    end = (data['end_lat'], data['end_lon'])

    type = data['type']
    route ,distance, time, obstacle = find_shortest_path(start, end, network_g, type)

    # 여기서는 경로(route)를 직접 반환하고 있으나, 실제로는 경로에 대한 상세 정보를 제공하는 것이 좋습니다.
    return jsonify({'route': route, 'distance' : distance,'time':time, 'obstacle':obstacle})



@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return '이미지 파일이 없습니다.', 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    network_g, result = add_obstacles(image, local, G = network_g)

    return result
    



if __name__ == '__main__':
    app.run(debug=True)