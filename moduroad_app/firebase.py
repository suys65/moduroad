from google.cloud import firestore
import os
import pandas as pd

# 환경 변수 설정으로 Firebase 인증 정보 제공
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "moduroad-firebase-adminsdk-6trb9-9ef3e5f55a.json"

# Firestore 클라이언트 초기화
db = firestore.Client()

# 컬렉션 생성 및 DataFrame 데이터 삽입 함수
def insert_dataframe_to_firestore(collection_name, dataframe):
    collection_ref = db.collection(collection_name)
    for record in dataframe.to_dict(orient="records"):
        # 새 문서 ID를 자동으로 생성하여 데이터 삽입
        collection_ref.add(record)
#-------------------------------------------------------------------------------------------------------------------#
import pandas as pd

# CSV 파일 읽기
file_path = 'data\_facility\에스컬레이터_휠체어리프트.pkl'
df = pd.read_pickle(file_path)
# DataFrame 데이터를 Firestore에 삽입
insert_dataframe_to_firestore("escalator_Wheelchairlift", df)

