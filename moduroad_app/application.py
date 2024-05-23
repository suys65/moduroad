
# 실행할 메인 파일
from flask import Flask, request, jsonify
import math
from algorithm import find_shortest_path
from add_obstacle import register
import pandas as pd
import pickle
from inference_sdk import InferenceHTTPClient
import networkx as nx
from PIL import Image
import io
import osmnx as ox
from shapely.geometry import Point


app = Flask(__name__, static_url_path='')

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TIcrpEjP7QDYM8tnrZG4"
)


global network_g

file_path = 'C:/my_code/moduroad/moduroad_app/cashe_data/Wheelchair_graph.pickle'

with open(file_path, 'rb') as file:
    network_g = pickle.load(file)
    
    


@app.route('/find-path', methods=['POST'])
def find_path_api():
    data = request.json
    start = (data['start_lat'], data['start_lon'])
    end = (data['end_lat'], data['end_lon'])

    type = data['type']
    route ,distance, time, obstacles = find_shortest_path(start, end, network_g, type)
    if not isinstance(obstacles, list):
        obstacles = [obstacles]


    # 여기서는 경로(route)를 직접 반환하고 있으나, 실제로는 경로에 대한 상세 정보를 제공하는 것이 좋습니다.
    return jsonify({'route': route, 'distance' : distance,'time':time, 'obstacles':obstacles})



@app.route('/detect', methods=['POST'])
def detect():
    
    if 'image' not in request.files:
        return '이미지 파일이 없습니다.', 400

    image_file = request.files['image']

    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    result = CLIENT.infer(image, model_id="stairs_detection-9av4i/1")
    result1 = CLIENT.infer(image, model_id="-1-pkbth/2")
    result2 = CLIENT.infer(image, model_id="curbs-bxcqk/1")

    # result["predictions"] 존재 여부에 따라 True 또는 False 반환
    if result.get("predictions") and any(prediction.get("class") == "stairs" for prediction in result["predictions"]): #계단 감지 경우
        return jsonify({
            "success": True,
            "obstacleType": "stair_steep" })
                        
    #계단이 감지되지 않음
    elif result1["predictions"] :
        for prediction in result1["predictions"][:2]:
            if prediction["class"] == "bollard" and prediction["confidence"] >=0.6:
                return jsonify({
                    "success": True,
                    "obstacleType": "bollard"
                    })
            else:
                continue
        return jsonify({"success": False})
            
    elif "predictions" in result2 :
        for prediction in result2["predictions"][:2]:
            if prediction["class"] == "curb" and prediction["confidence"] >=0.6:
                return jsonify({
                    "success": True,
                    "obstacleType": "sidewalk_curb"
                    })
            else:
                continue
        return jsonify({"success": False})
    else :
        return jsonify({"success": False})
    

@app.route('/registerObstacle', methods=['POST'])
def registerObstacle():
    global network_g
    data = request.json
    obstacleType = data['obstacleType']
    longitude = data['longitude']
    latitude = data['latitude']
    longitude = float(longitude)
    latitude = float(latitude)

    local= Point(longitude, latitude)
  
    network_g, result = register(obstacleType, local, G = network_g)

    return result

if __name__ == '__main__':
    app.run(debug=True)