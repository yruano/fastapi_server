# 학습 시킨 코드가 필요
# 흠 무슨 코드가 필요한거지
# ??? 이거 하려면 데이터셋이 필요하네 ??????????????????????????????????
# https://github.com/Recircle2000/autolookbook_YOLO/blob/master/train_lib/YOLOv8/yoloTrain.ipynb
# 이거는 모델 설정이 잘못 되었던 내가 잘못 쓰던
# 일단 스스로 무언가 학습을 하고 무언가 만들고 있어 이게 맞나?
import cv2
from rembg import remove
from PIL import Image
from ultralytics import YOLO
import extcolors
import numpy as np
from sklearn.cluster import KMeans
from fastapi import File

async def analyze_image(file: File):
    # 이미지를 numpy 배열로 변환
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 배경 제거
    img_no_bg = remove(img_np)

    # 그레이스케일로 변환
    gray_img = cv2.cvtColor(img_no_bg, cv2.COLOR_BGR2GRAY)
    
    # 히스토그램 평활화
    equalized_img = cv2.equalizeHist(gray_img)
    
    # YOLO 모델 로드
    model = YOLO("best240506.pt")
    
    # 결과 저장할 임시 파일 경로 설정
    temp_output_path = "temp_output.png"
    cv2.imwrite(temp_output_path, equalized_img)
    
    # YOLO 모델로 분석
    results = model(temp_output_path)
    print("\n")
    print(results[0])

    # 라벨이 없음 이거는 ai를 확인 하는게 좋겠군
    
    # # 분석 결과 출력 (옷의 카테고리)
    # categories = results[0].names  # 클래스 이름을 포함한 딕셔너리
    # detected_labels = results.labels  # 감지된 객체의 레이블 리스트
    
    # # "hood" 카테고리를 찾아서 출력
    # for label in detected_labels:
    #     category = categories[label]
    #     if category == "hood":
    #         print("Detected category: hood")

    # return results

def color_extraction(file: File):
    # 색상 추출
    img = Image.open(file.file)
    colors, pixel_count = extcolors.extract_from_image(img)
    
    pixel_output = 0
    for c in colors:
        pixel_output += c[1]
        print(f'{c[0]} : {round((c[1] / pixel_count) * 100, 2)}% ({c[1]})')
    
    print(f'Pixels in output: {pixel_output} of {pixel_count}')