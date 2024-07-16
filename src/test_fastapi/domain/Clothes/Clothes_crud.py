import base64
import asyncio
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
        "misc": ["one-piece_dress"]
    },
    "23~27": {
        "outerwear": [],
        "tops": ["short_sleeve shirt", "long_sleeve shirt", "normalKnit", "short_sleeves", "short_sleeves_knit"],
        "bottoms": ["chino-cotton", "half_pants", "Short_Skirt"],
        "misc": []
    },
    "20~22": {
        "outerwear": [],
        "tops": ["long_sleeve shirt", "hood", "hood_zip-up", "normalKnit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "half_pants", "Long_Skirt"],
        "misc": ["denim-shirts"]
    },
    "17~19": {
        "outerwear": ["Windbreaker", "Blouson", "Zip-Up_Knit","blazer"],
        "tops": ["hood", "sweatshirt", "normalKnit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "Long_Skirt"],
        "misc": ["denim-shirts"]
    },
    "12~16": {
        "outerwear": ["Blouson", "Zip-Up_Knit", "denim-jacket",],
        "tops": ["sweatshirt", "long_sleeve shirt", "hood_zip-up", "fleece_jacket", "normalKnit",],
        "bottoms": ["denim_pants", "chino-cotton", "Long_Skirt"],
        "misc": ["one-piece_dress"]
    },
    "9~11": {
        "outerwear": ["Blouson", "denim-jacket", "blazer"],
        "tops": ["normalKnit"],
        "bottoms": ["denim_pants", "chino-cotton"],
        "misc": ["one-piece_dress"]
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


def image_doublecheck(db: Session, image: bytes, user_id: str):
    encoded_image = base64.b64encode(image)
    double_iamge = db.query(Clothes).filter(Clothes.User_Id == user_id, Clothes.Clothes_Image == encoded_image).first()
    if double_iamge is not None:
        return False
    return True


def create_Clothes(db: Session, _clothe: dict):
    encoded_image = base64.b64encode(_clothe["image"])
    db_Clothe = Clothes(
        Clothes_Create_Date = datetime.now(),
        Clothes_LastFit_Date = datetime.now(),
        Clothes_Category = _clothe["category"],
        Clothes_Image = encoded_image,
        Clothes_Count = 0,
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
    elif category is None and clothe_id is not None:
        clothe = db.query(Clothes).filter(Clothes.Clothes_Id == clothe_id, Clothes.User_Id == user_id).all()
    else:
        clothe = db.query(Clothes).filter(Clothes.Clothes_Category == category, Clothes.User_Id == user_id).all()
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
async def Clothes_push_by_id(clothes_id: int, user_id: str, current_temperature: int, db: Session):
    try:
        clothe = db.query(Clothes).filter(Clothes.Clothes_Id == clothes_id, Clothes.User_Id == user_id).first()
        if not clothe:
            return {"error": "Clothing item not found"}

        # 색 추천
        clothe_color = await predictcolor.predict_color(color = clothe.Clothes_Color)
        if "error" in clothe_color:
            return clothe_color

        # 현재 온도에 맞는 옷 추천
        temperature_range = get_temperature_range(current_temperature)
        recommendations = clothing_recommendations.get(temperature_range, {})
        filtered_recommendations = {"tops": [], "bottoms": [], "outerwear": []}

        # 현재 옷 중에서 잘 맞는 옷 카테고리
        nomination_cody = await cody.predict_category(category = clothe.Clothes_Category)

        for category, items in recommendations.items():
            if category not in filtered_recommendations:
                continue
            for item in items:
                if item == clothe.Clothes_Category:
                    filtered_recommendations[category].append(clothe.Clothes_Id)
                for nomination in nomination_cody:
                    if item == nomination:
                        for predicted_color in clothe_color:
                            nomination_clothe = db.query(Clothes).filter(Clothes.Clothes_Category == item, Clothes.Clothes_Color == predicted_color, Clothes.User_Id == user_id).first()
                            if not nomination_clothe:
                                continue
                            else:
                                filtered_recommendations[category].append(nomination_clothe.Clothes_Id)

        return filtered_recommendations

    finally:
        db.close()


# 온도만 가지고 추천
async def Clothes_push_by_temperature(user_id: str, current_temperature: int, db: Session):
    try:
        # 현재 온도에 맞는 상의 추천
        temperature_range = get_temperature_range(current_temperature)
        tops_recommendations = clothing_recommendations[temperature_range]["tops"]

        # 사용자 상의 목록을 조회하여 카테고리와 색상 저장
        clothe_copy = []

        for top in tops_recommendations:
            clothes = db.query(Clothes).filter(Clothes.Clothes_Category == top, Clothes.User_Id == user_id).all()
            for clothe in clothes:
                if clothe:
                    clothe_copy.append(clothe)

        # 비동기적으로 카테고리 예측 작업 수행
        category_tasks = [(clothe.Clothes_Id, cody.predict_category(category=clothe.Clothes_Category)) for clothe in clothe_copy]
        category_results = await asyncio.gather(*[task for _, task in category_tasks])
        category_results = {clothe_id: result for (clothe_id, _), result in zip(category_tasks, category_results)}

        # 비동기적으로 색상 예측 작업 수행
        color_tasks = [(clothe.Clothes_Id, predictcolor.predict_color(color=clothe.Clothes_Color)) for clothe in clothe_copy]
        color_results = await asyncio.gather(*[task for _, task in color_tasks])
        color_results = {clothe_id: result for (clothe_id, _), result in zip(color_tasks, color_results)}

        # 추천 아이템 필터링
        recommendations = clothing_recommendations.get(temperature_range, {})
        filtered_recommendations = {"tops": [], "bottoms": [], "outerwear": []}

        for category, items in recommendations.items():
            if category not in filtered_recommendations:
                continue
            for item in items:
                for clothe in clothe_copy:
                    if item == clothe.Clothes_Category:
                        filtered_recommendations[category].append(clothe.Clothes_Id)
                    if clothe.Clothes_Id in category_results:
                        for results in category_results[clothe.Clothes_Id]:
                            if item == results and clothe.Clothes_Id in color_results:
                                for color in color_results[clothe.Clothes_Id]:
                                    clothe_match = db.query(Clothes).filter(
                                        Clothes.Clothes_Category == item,
                                        Clothes.Clothes_Color == color,
                                        Clothes.User_Id == user_id
                                    ).first()
                                    if clothe_match:
                                        filtered_recommendations[category].append(clothe_match.Clothes_Id)

        return filtered_recommendations

    finally:
        db.close()