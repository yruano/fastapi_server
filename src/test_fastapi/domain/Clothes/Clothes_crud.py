import base64
from datetime import datetime
from models import Clothes
from sqlalchemy.orm import Session
from learning_model import predictcolor, cody


# 기준 : https://namu.wiki/w/%EA%B8%B0%EC%98%A8%EB%B3%84%20%EC%98%B7%EC%B0%A8%EB%A6%BC
clothing_recommendations = {
    "28~": {
        "outerwear": [],
        "tops": ["sleeveless", "short_sleeve shirt", "short_sleeves", "short_sleeves_knit"],
        "bottoms": ["half_pants", "Short_Skirt"],
        "misc": ["Linen Dress", "one-piece_dress"]
    },
    "23~27": {
        "outerwear": [],
        "tops": ["short_sleeve shirt", "long_sleeve shirt", "normalKnit", "thin_shirt", "short_sleeves", "short_sleeves_knit"],
        "bottoms": ["chino-cotton", "half_pants", "Short_Skirt"],
        "misc": []
    },
    "20~22": {
        "outerwear": ["thin_cardigan"],
        "tops": ["long_sleeve shirt", "hood", "hood_zip-up", "blouse", "normalKnit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "cropped_pants", "Long_Skirt"],
        "misc": ["denim-shirts"]
    },
    "17~19": {
        "outerwear": ["Windbreaker", "Blouson", "Zip-Up_Knit", "thin_jacket"],
        "tops": ["hood", "sweatshirt", "blazer", "normalKnit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "skinny_pants", "Long_Skirt"],
        "misc": ["denim-shirts"]
    },
    "12~16": {
        "outerwear": ["Blouson", "Zip-Up_Knit", "denim-jacket", "cardigan", "field_jacket"],
        "tops": ["sweatshirt", "long_sleeve shirt", "hood_zip-up", "fleece_hoodie"],
        "bottoms": ["denim_pants", "chino-cotton", "Long_Skirt"],
        "misc": ["stockings", "normalKnit", "one-piece_dress"]
    },
    "9~11": {
        "outerwear": ["Blouson", "denim-jacket", "blazer", "trench_coat", "field_jacket", "jumper"],
        "tops": ["normalKnit"],
        "bottoms": ["denim_pants", "chino-cotton", "layered", "fleece"],
        "misc": ["one-piece_dress", "denim-shirts"]
    },
    "5~8": {
        "outerwear": ["wool_coat", "leather jacket"],
        "tops": ["normalKnit", "fleece_jacket"],
        "bottoms": ["leggings", "denim_pants", "thick_pants", "fleece_pants"],
        "misc": ["scarf", "fleece", "thermal_underwear"]
    },
    "~4": {
        "outerwear": ["padding", "thick_coat", "long-padded-coat", "padded-coat"],
        "tops": ["normalKnit"],
        "bottoms": ["denim_pants", "training/jogger_pants"],
        "misc": ["scarf", "thermal_underwear"]
    }
}


def find_temperature_for_clothing(clothing_item):
    results = []
    for temperature, categories in clothing_recommendations.items():
        for category, items in categories.items():
            if clothing_item in items:
                results.append(temperature)
    return results


async def create_Clothes(db: Session, _clothe: dict):
    contents = await _clothe["image"].read()
    encoded_image = base64.b64encode(contents)
    db_Clothe = Clothes(
        Clothes_Create_Date = datetime.now(),
        Clothes_LastFit_Date = datetime.now(),
        Clothes_Category = _clothe["category"],
        Clothes_Image = encoded_image,
        Clothes_Count = 0,  # 예시 값, 필요에 따라 수정
        Clothes_Score = find_temperature_for_clothing(_clothe["category"]),
        Clothes_Color = _clothe["color"],
        User_Id = _clothe["user_id"],
        User = _clothe["user"]
    )
    db.add(db_Clothe)
    db.commit()


def modify_Clothes(user_id: str, modify_clothe: Clothes, db: Session):
    original_user = db.query(Clothes).filter(Clothes.User_Id == user_id, Clothes.Clothes_Id == modify_clothe.Clothes_Id).first()
    
    for attr in ['Clothes_Category', 'Clothes_Image', 'Clothes_Color', 'Clothes_Count']:
        new_value = getattr(modify_clothe, attr)
        if new_value != "" and new_value is not None:
            setattr(original_user, attr, new_value)
    
    db.add(original_user)
    db.commit()
    return check_Clothes_data(db = db, category = None, clothe_id = modify_clothe.Clothes_Id, user_id = user_id)


def check_Clothes_data(category: str, clothe_id: int, db: Session, user_id: str):
    if category is None and clothe_id is None:
        clothe = db.query(Clothes).filter(Clothes.User_Id == user_id).all()
    else:
        clothe = db.query(Clothes).filter(Clothes.Clothes_Category == category, Clothes.Clothes_Id == clothe_id, Clothes.User_Id == user_id).all()
    return clothe


def delete_Clothes_data(db: Session, user_id: str, Clothes_id: int):
    clothe = db.query(Clothes).filter(Clothes.Clothes_Id == Clothes_id, Clothes.User_Id == user_id).first()

    if clothe is not None:
        db.delete(clothe)
        db.commit()
        return True
    else:
        return False


def get_temperature_range(current_temperature):
    if current_temperature >= 28:
        return "28~"
    elif 23 <= current_temperature <= 27:
        return "23~27"
    elif 20 <= current_temperature <= 22:
        return "20~22"
    elif 17 <= current_temperature <= 19:
        return "17~19"
    elif 12 <= current_temperature <= 16:
        return "12~16"
    elif 9 <= current_temperature <= 11:
        return "9~11"
    elif 5 <= current_temperature <= 8:
        return "5~8"
    elif current_temperature <= 4:
        return "~4"
    return None


# 특정 옷에 대해서 추천
async def Clothes_push(clothe_id: int, user_id: str, current_temperature: int, db: Session):
    clothe = db.query(Clothes).filter(Clothes.Clothes_Id == clothe_id, Clothes.User_Id == user_id).first()
    if not clothe:
        return {"error": "Clothing item not found"}

    # 색 추천
    clothe_color = await predictcolor.predict_color(color=clothe.Clothes_Color)
    if "error" in clothe_color:
        return clothe_color

    # 현재 온도에 맞는 옷 추천
    temperature_range = get_temperature_range(current_temperature)
    recommendations = clothing_recommendations.get(temperature_range, {})
    filtered_recommendations = {"tops": [], "bottoms": [], "outerwear": []}

    # 현재 옷 중에서 잘 맞는 옷 카테고리
    nomination_cody = await cody.predict_category(category=clothe.Clothes_Category)
    
    for category, items in recommendations.items():
        if category not in filtered_recommendations:
            continue
        for item in items:
            if any(predicted_color in item for predicted_color in clothe_color):
                if category in nomination_cody:
                    filtered_recommendations[category].append(item)
    
    return filtered_recommendations


# 온도만 가지고 추천
async def Clothes_push(user_id: str, current_temperature: int, db: Session):
    # 현재 온도에 맞는 바지 추천
    temperature_range = get_temperature_range(current_temperature)
    bottoms_recommendations = clothing_recommendations[temperature_range]["bottoms"]

    # 사용자 바지 목록을 조회하여 카테고리와 색상 저장
    clothe_category = {}
    clothe_color = {}

    for bottom in bottoms_recommendations:
        clothe = db.query(Clothes).filter(Clothes.Clothes_Category == bottom, Clothes.User_Id == user_id).first()
        if clothe:
            if bottom not in clothe_category:
                clothe_category[bottom] = []
                clothe_color[bottom] = []
            nomination_cody = await cody.predict_category(category=clothe.Clothes_Category)
            clothe_category[bottom].append(nomination_cody)
            clothe_color[bottom].append(clothe.Clothes_Color)

    # 온도에 맞는 전체 추천 목록 필터링
    recommendations = clothing_recommendations.get(temperature_range, {})
    filtered_recommendations = {"tops": [], "bottoms": [], "outerwear": []}

    for bottom, colors in clothe_color.items():
        for color in colors:
            predicted_colors = await predictcolor.predict_color(color=color)
            if "error" in predicted_colors:
                return predicted_colors

            for category, items in recommendations.items():
                filtered_items = []
                for item in items:
                    if any(predicted_color in item for predicted_color in predicted_colors):
                        filtered_items.append(item)
                if filtered_items:
                    filtered_recommendations[category].extend(filtered_items)

    return filtered_recommendations