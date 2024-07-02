# 학습 시킨 코드가 필요
# 흠 무슨 코드가 필요한거지
# ??? 이거 하려면 데이터셋이 필요하네 ??????????????????????????????????
# https://github.com/Recircle2000/autolookbook_YOLO/blob/master/train_lib/YOLOv8/yoloTrain.ipynb
# 이거는 모델 설정이 잘못 되었던 내가 잘못 쓰던
# 일단 스스로 무언가 학습을 하고 무언가 만들고 있어 이게 맞나?
import cv2
import json
import extcolors
import webcolors
import numpy as np
from rembg import remove
from PIL import Image
from ultralytics import YOLO
from sklearn.cluster import KMeans
from fastapi import File
from skimage import color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor

color_groups_custom = {
    "white": ["lavender","aliceblue","honeydew","azure","whitesmoke","mintcream","gainsboro","ghostwhite","oldlace","mistyrose","lavenderblush","seashell","snow","white",],  #흰색
    "black": ["black",],  #검정색(굉장히 어두운 회색
    "gray": ["darkslategray","darkslategrey","dimgray","dimgrey","slategray","slategrey","lightslategrey","lightslategray","gray","grey","darkgray","darkgrey",],  #회색
    "silver": ["silver","lightgray","lightgrey",],  # 밝은 회색(light gray)
    "light orange": ["sandybrown", "orangered", ],  # 주황색
    "orange": ["sandybrown","orangered","darkorange","orange",],  #주황색
    "yellow": ["gold","yellow","goldenrod","darkgoldenrod",],  #노랑색
    "pink": ["deeppink",],  # 노랑색
    "light pink": ["hotpink",'lightpink',"pink",],  # 핑크
    "ivory": ["lightgoldenrodyellow","cornsilk","lemonchiffon","floralwhite","lightyellow","ivory",],  # 아이보리색(light yellow)
    "beige": ["papayawhip","blanchedalmond","bisque","moccasin","navajowhite","peachpuff","tan","goldenrod","burlywood","palegoldenrod","wheat","beige","antiquewhite","linen",],  # 회색빛 노랑색
    "khaki": ["darkkhaki","khaki",],  # 카키
    "light green": ['mediumspringgreen','springgreen',"lawngreen","chartreuse","darkseagreen","lightgreen","palegreen","greenyellow",],  #블루그린, 연두색
    "green": ["darkgreen",'green','lime',"forestgreen","seagreen","limegreen","mediumseagreen","yellowgreen",],  #초록색
    "cyan": ['teal','darkcyan','darkturquoise','cyan','lightseagreen',"turquoise","mediumturquoise","mediumaquamarine","aquamarine",],  #청록색
    "olive": ["darkolivegreen","olivedrab","olive",],  # 갈록색(사람들이 흔히 생각하는 카키색)
    "light blue": ['deepskyblue','aqua',"cadetblue","cornflowerblue","skyblue","lightskyblue","lightblue","paleturquoise","lightsteelblue","powderblue","lightcyan",],  # 밝은 파랑색
    "blue": ["darkslateblue","mediumblue","blue","dodgerblue","royalblue","steelblue",],  #파랑색
    "navy": ["navy","darkblue","midnightblue",],  #남색
    "light purple": ["slateblue", "mediumslateblue","mediumpurple","thistle","plum","violet",],  # 연한 보라색
    "purple": ["indigo","rebeccapurple","purple","blueviolet","darkviolet","darkorchid","mediumorchid","orchid",],  #보라색
    "red purple": ["darkmagenta","mediumvioletred","palevioletred","fuchsia","magenta",], #자주색
    "light red": ["rosybrown","indianred","darksalmon",'lightcoral',"salmon","tomato","coral","lightsalmon",],  # 빨강색
    "red": ["maroon","darkred","firebrick","crimson","red",], #빨강색
    "brown": ["saddlebrown","sienna","brown","peru","chocolate",],  # 갈색
}


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
    model = YOLO("best240702v10.pt")
    
    # 결과 저장할 임시 파일 경로 설정
    temp_output_path = "temp_output.png"
    cv2.imwrite(temp_output_path, equalized_img)
    
    # YOLO 모델로 분석
    results = model(temp_output_path)
    print("\n")

    # 분석 결과를 JSON 형식으로 변환
    results_json = results[0].tojson()
    
    # JSON 데이터 파싱
    results_data = json.loads(results_json)
    
    # name 필드만 추출하여 출력
    detected_names = [item["name"] for item in results_data]
    
    
    return detected_names[0]


def hex_to_rgb(hex_code):
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def closest_color(requested_color):
    # RGB to L*a*b* 변환 함수
    def rgb_to_lab(rgb):
        rgb = np.array(rgb, dtype=np.uint8).reshape(1, 1, 3)
        lab = color.rgb2lab(rgb)
        return lab[0, 0]

    # 주어진 색상의 L*a*b* 값 계산
    requested_lab = rgb_to_lab(requested_color)

    min_distance = float('inf')
    closest_color_name = None

    for hex_value, color_name in webcolors.CSS3_HEX_TO_NAMES.items():
        rgb = webcolors.hex_to_rgb(hex_value)
        lab = rgb_to_lab(rgb)

        # CIEDE2000 색상차 계산
        distance = color.deltaE_ciede2000(requested_lab, lab)

        if distance < min_distance:
            min_distance = distance
            closest_color_name = color_name

    return closest_color_name


def get_general_color_name(requested_color):
    try:
        closest_name = webcolors.rgb_to_name(requested_color)
    except ValueError:
        closest_name = closest_color(requested_color)

    for group, colors in color_groups_custom.items():
        if closest_name in colors:
            return group
    return "unknown"


def color_extraction(file):
    img = Image.open(file.file)
    colors, pixel_count = extcolors.extract_from_image(img)
    print(colors)
    most_common_color = colors[1][0]
    
    # 일반 색상 이름 반환
    general_color_name = get_general_color_name(most_common_color)
    print(general_color_name)
    return general_color_name