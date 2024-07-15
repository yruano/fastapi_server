import numpy as np
from PIL import Image
import webcolors
from skimage import color
from sklearn.cluster import KMeans

color_groups_custom = {
    "white": ["lavender", "aliceblue", "honeydew", "azure", "whitesmoke", "mintcream", "gainsboro", "ghostwhite", "oldlace", "mistyrose", "lavenderblush", "seashell", "snow", "white"],
    "black": ["black"],
    "gray": ["darkslategray", "darkslategrey", "dimgray", "dimgrey", "slategray", "slategrey", "lightslategrey", "lightslategray", "gray", "grey", "darkgray", "darkgrey"],
    "silver": ["silver", "lightgray", "lightgrey"],
    "light orange": ["sandybrown", "orangered"],
    "orange": ["sandybrown", "orangered", "darkorange", "orange"],
    "yellow": ["gold", "yellow", "goldenrod", "darkgoldenrod"],
    "pink": ["deeppink"],
    "light pink": ["hotpink", 'lightpink', "pink"],
    "ivory": ["lightgoldenrodyellow", "cornsilk", "lemonchiffon", "floralwhite", "lightyellow", "ivory"],
    "beige": ["papayawhip", "blanchedalmond", "bisque", "moccasin", "navajowhite", "peachpuff", "tan", "goldenrod", "burlywood", "palegoldenrod", "wheat", "beige", "antiquewhite", "linen"],
    "khaki": ["darkkhaki", "khaki"],
    "light green": ['mediumspringgreen', 'springgreen', "lawngreen", "chartreuse", "darkseagreen", "lightgreen", "palegreen", "greenyellow"],
    "green": ["darkgreen", 'green', 'lime', "forestgreen", "seagreen", "limegreen", "mediumseagreen", "yellowgreen"],
    "cyan": ['teal', 'darkcyan', 'darkturquoise', 'cyan', 'lightseagreen', "turquoise", "mediumturquoise", "mediumaquamarine", "aquamarine"],
    "olive": ["darkolivegreen", "olivedrab", "olive"],
    "light blue": ['deepskyblue', 'aqua', "cadetblue", "cornflowerblue", "skyblue", "lightskyblue", "lightblue", "paleturquoise", "lightsteelblue", "powderblue", "lightcyan"],
    "blue": ["darkslateblue", "mediumblue", "blue", "dodgerblue", "royalblue", "steelblue"],
    "navy": ["navy", "darkblue", "midnightblue"],
    "light purple": ["slateblue", "mediumslateblue", "mediumpurple", "thistle", "plum", "violet"],
    "purple": ["indigo", "rebeccapurple", "purple", "blueviolet", "darkviolet", "darkorchid", "mediumorchid", "orchid"],
    "red purple": ["darkmagenta", "mediumvioletred", "palevioletred", "fuchsia", "magenta"],
    "light red": ["rosybrown", "indianred", "darksalmon", 'lightcoral', "salmon", "tomato", "coral", "lightsalmon"],
    "red": ["maroon", "darkred", "firebrick", "crimson", "red"],
    "brown": ["saddlebrown", "sienna", "brown", "peru", "chocolate"],
}


def extract_rgb_values(image):
    if len(image.shape) == 3:
        height, width, _ = image.shape
    else:
        height, width = image.shape  # 흑백 이미지의 경우

    # 이미지 중앙 값 계산
    center_y, center_x = height // 2, width // 2

    # 사각형 영역 지정
    region_size_y, region_size_x = height // 6, width // 6

    # 샘플링 영역의 시작 및 종료 지점을 계산
    start_y, end_y = center_y - region_size_y, center_y + region_size_y
    start_x, end_x = center_x - region_size_x, center_x + region_size_x

    # 사각형 영역의 rgb 값 추출
    if len(image.shape) == 3:
        rgb_values = [image[y, x] for y in range(start_y, end_y) for x in range(start_x, end_x)]
    else:  # 흑백 이미지의 경우, 모든 채널 값이 동일하므로 하나의 값만 사용
        rgb_values = [[image[y, x], image[y, x], image[y, x]] for y in range(start_y, end_y) for x in range(start_x, end_x)]
    return rgb_values


def find_optimal_clusters(image, max_clusters=100):
    rgb_values = extract_rgb_values(image)
    rgb_array = np.array(rgb_values)
    inertias = []
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(rgb_array)
        inertias.append(kmeans.inertia_)

    optimal_clusters = inertias.index(min(inertias)) + 1
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    kmeans.fit(rgb_array)
    labels = kmeans.labels_
    dominant_cluster_index = np.argmax(np.bincount(labels))
    dominant_color_center = kmeans.cluster_centers_[dominant_cluster_index]
    return dominant_color_center


def hex_to_rgb(hex_code):
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def closest_color(requested_color):
    def rgb_to_lab(rgb):
        rgb = np.array(rgb, dtype=np.uint8).reshape(1, 1, 3)
        lab = color.rgb2lab(rgb)
        return lab[0, 0]
    requested_lab = rgb_to_lab(requested_color)
    min_distance = float('inf')
    closest_color_name = None
    for hex_value, color_name in webcolors.CSS3_HEX_TO_NAMES.items():
        rgb = webcolors.hex_to_rgb(hex_value)
        lab = rgb_to_lab(rgb)
        distance = color.deltaE_ciede2000(requested_lab, lab)
        if distance < min_distance:
            min_distance = distance
            closest_color_name = color_name
    return closest_color_name


def get_general_color_name(requested_color):
    try:
        closest_name = webcolors.rgb_to_name(tuple(int(c) for c in requested_color))
    except ValueError:
        closest_name = closest_color(requested_color)
    for group, colors in color_groups_custom.items():
        if closest_name in colors:
            return group
    return "unknown"


def color_extraction(file):
    img = Image.open(file.file)
    img_np = np.array(img)
    dominant_color_center = find_optimal_clusters(img_np)
    general_color_name = get_general_color_name(dominant_color_center)

    return general_color_name