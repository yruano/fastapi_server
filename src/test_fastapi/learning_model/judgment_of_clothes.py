# import torch
# import cv2
# from PIL import Image
# import numpy as np

# # 모델 로드
# model = torch.hub.load('ultralytics/yolov5', 'custom', path='/mnt/data/best240506.pt')

# # 이미지 로드 및 전처리
# def load_image(image_path):
#     img = Image.open(image_path)
#     return img

# # 객체 감지 함수
# def detect_objects(image_path):
#     img = load_image(image_path)
#     results = model(img)
#     return results

# # 결과 출력 및 이미지 저장
# def draw_boxes(image_path, results):
#     img = cv2.imread(image_path)
#     for result in results.xyxy[0]:  # results.xyxy[0]에 감지된 객체들이 들어 있음
#         x1, y1, x2, y2, conf, cls = map(int, result)
#         label = f'{model.names[cls]} {conf:.2f}'
#         cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#     cv2.imwrite('output.jpg', img)
#     cv2.imshow('Detected Objects', img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# # 예시 사용법
# image_path = 'input.jpg'  # 입력 이미지 파일 경로
# results = detect_objects(image_path)
# draw_boxes(image_path, results)
