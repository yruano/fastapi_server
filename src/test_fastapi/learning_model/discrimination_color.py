import numpy as np
from PIL import Image
import webcolors
from skimage import color
from rembg import remove
import math
from sklearn.cluster import KMeans
import cv2

color_groups = {
    "white": ["#FFFFFF", "#F8F8FF", "#FFFAFA", "#F0F8FF", "#F5F5F5", "#FFF5EE"],
    "black": ["#000000", "#0C0C0C", "#2F4F4F"],
    "gray": ["#808080", "#A9A9A9", "#696969", "#BEBEBE", "#D3D3D3"],
    "silver": ["#C0C0C0", "#DCDCDC", "#E0E0E0"],
    "light orange": ["#FFA07A", "#FF8C00", "#FA8072", "#FFDAB9"],
    "orange": ["#FFA500", "#FF4500", "#FF6347", "#FF7F50"],
    "yellow": ["#FFFF00", "#FFFFE0", "#FFFACD", "#FFD700"],
    "pink": ["#FFC0CB", "#FF69B4", "#FF1493", "#FFB6C1"],
    "light pink": ["#FFB6C1", "#FF69B4", "#FFC0CB", "#FFE4E1"],
    "ivory": ["#FFFFF0", "#FAF0E6", "#FFF5EE", "#FFF8DC"],
    "beige": ["#F5F5DC", "#F5DEB3", "#FAEBD7", "#EEE8AA","#D1C4AF"],
    "khaki": ["#F0E68C", "#BDB76B", "#EEE8AA", "#F5DEB3"],
    "light green": ["#90EE90", "#98FB98", "#8FBC8F", "#00FF7F"],
    "green": ["#008000", "#006400", "#228B22", "#32CD32"],
    "cyan": ["#00FFFF", "#E0FFFF", "#AFEEEE", "#7FFFD4"],
    "olive": ["#808000", "#6B8E23", "#556B2F", "#8B4513"],
    "light blue": ["#ADD8E6", "#87CEEB", "#87CEFA", "#B0E0E6"],
    "blue": ["#0000FF", "#1E90FF", "#0000CD", "#4169E1"],
    "navy": ["#000080", "#00008B", "#191970", "#00004B", "#1C202E"],
    "light purple": ["#E6E6FA", "#D8BFD8", "#DDA0DD", "#EE82EE"],
    "purple": ["#800080", "#8A2BE2", "#9370DB", "#9400D3","#CF919F"],
    "red purple": ["#C71585", "#FF00FF", "#DA70D6", "#D87093"],
    "light red": ["#FF6347", "#FF7F50", "#FA8072", "#E9967A"],
    "red": ["#FF0000", "#DC143C", "#B22222", "#CD5C5C"],
    "brown": ["#A52A2A", "#8B4513", "#A0522D", "#D2691E"]
}


def extract_rgb_values(image):
    if len(image.shape) == 3:
        height, width, _ = image.shape
    else:
        height, width = image.shape  # 흑백 이미지의 경우

    # 이미지 중앙 값 계산
    center_y, center_x = height // 2, width // 2

    # 사각형 영역 지정
    region_size_y, region_size_x = height // 8, width // 6

    # 샘플링 영역의 시작 및 종료 지점을 계산
    start_y, end_y = center_y - region_size_y, center_y + region_size_y
    start_x, end_x = center_x - region_size_x, center_x + region_size_x

    # 사각형 영역의 rgb 값 추출
    if len(image.shape) == 3:
        rgb_values = [image[y, x] for y in range(start_y, end_y) for x in range(start_x, end_x)]
    else:  # 흑백 이미지의 경우, 모든 채널 값이 동일하므로 하나의 값만 사용
        rgb_values = [[image[y, x], image[y, x], image[y, x]] for y in range(start_y, end_y) for x in range(start_x, end_x)]
    return rgb_values


def find_optimal_clusters(image, max_clusters=10, sample_size=1000):
    rgb_values = extract_rgb_values(image)
    rgb_array = np.array(rgb_values)

    # 데이터 샘플링
    if len(rgb_array) > sample_size:
        rgb_array = rgb_array[np.random.choice(rgb_array.shape[0], sample_size, replace=False)]

    inertias = []

    # KMeans 클러스터링 수행
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, n_init=10, init='k-means++', random_state=42)
        kmeans.fit(rgb_array)
        inertias.append(kmeans.inertia_)

    # 최적 클러스터 수 결정
    optimal_clusters = inertias.index(min(inertias)) + 1
    kmeans = KMeans(n_clusters=optimal_clusters, n_init=10, init='k-means++', random_state=42)
    kmeans.fit(rgb_array)

    # 지배적인 클러스터의 색상
    labels = kmeans.labels_
    dominant_cluster_index = np.argmax(np.bincount(labels))
    dominant_color_center = kmeans.cluster_centers_[dominant_cluster_index]

    print(dominant_color_center)
    return dominant_color_center


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def color_distance(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def find_closest_color(input_rgb):
    min_distance = float('inf')
    closest_color_name = None

    for color_name, hex_values in color_groups.items():
        for hex_value in hex_values:
            current_rgb = hex_to_rgb(hex_value)
            distance = color_distance(input_rgb, current_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_color_name = color_name

    return closest_color_name


def color_extraction(file):
    img = Image.open(file.file)
    img = remove(img)
    img_rgb = img.convert("RGB")
    img_np = np.array(img_rgb)
    img_np = cv2.convertScaleAbs(img_np, alpha=1, beta=0)
    dominant_color_center = find_optimal_clusters(img_np)
    print(dominant_color_center)
    general_color_name = find_closest_color(dominant_color_center)

    return general_color_name