from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib.patches as patches

#터미널에 "pip install inference-sdk" 입력

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TIcrpEjP7QDYM8tnrZG4"
)

#원하는 이미지 경로 - 계단 있/없 탐지
image_path = "KakaoTalk_20240312_001355174.jpg"
result = CLIENT.infer(image_path, model_id="stairs_detection-jaj7e/2")
print(result["predictions"])
image = Image.open(image_path)

# 탐지된 객체 정보 (여기서는 예제 데이터 사용)
detections = [
    {'x': result["predictions"][0]['x'], 'y': result["predictions"][0]['y'], 'width': result["predictions"][0]['width'], 'height': result["predictions"][0]['height'], 'class': result["predictions"][0]['class']}
]

# 이미지에 객체 표시하기
fig, ax = plt.subplots(1)
ax.imshow(image)

# 탐지된 각 객체에 대한 반복 처리
for detection in detections:
    # 탐지된 객체의 경계 상자 생성
    rect = patches.Rectangle((detection['x'], detection['y']), detection['width'], detection['height'], linewidth=2, edgecolor='r', facecolor='none')
    
    # 객체의 클래스 이름 표시
    ax.text(detection['x'], detection['y'], detection['class'], style='italic', bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 10})
    
    # 경계 상자를 그림에 추가
    ax.add_patch(rect)

plt.show()