import base64
import asyncio
from datetime import datetime
from models import Clothes
from sqlalchemy.orm import Session
from learning_model import predictcolor, cody
from typing import Dict, List, Union


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
        "bottoms": ["chino-cotton", "half_pants", "Short_Skirt","training-jogger_pants"],
        "misc": []
    },
    "20~22": {
        "outerwear": [],
        "tops": ["long_sleeve shirt", "hood", "hood_zip-up", "normalKnit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "half_pants", "Long_Skirt","training-jogger_pants"],
        "misc": ["denim-shirts"]
    },
    "17~19": {
        "outerwear": ["Windbreaker", "Blouson", "Zip-Up_Knit","blazer"],
        "tops": ["hood", "sweatshirt", "normalKnit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "Long_Skirt","training-jogger_pants"],
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
    double_iamge = db.query(Clothes).filter(Clothes.User_Id == user_id, Clothes.Clothes_Image == image).first()
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
async def Clothes_push_by_id(
    clothes_id: int, 
    user_id: str, 
    current_temperature: int, 
    db: Session
) -> Union[Dict[str, Union[str, int]], Dict[str, List[int]]]:
    async def fetch_predict_color(clothe_color: str) -> Dict[str, str]:
        try:
            return await predictcolor.predict_color(color=clothe_color)
        except Exception as e:
            return {"error": str(e)}

    async def fetch_predict_category(category: str) -> List[str]:
        try:
            return await cody.predict_category(category=category)
        except Exception as e:
            return {"error": str(e)}

    try:
        # 옷 아이템 조회
        clothe = db.query(Clothes).filter(
            Clothes.Clothes_Id == clothes_id,
            Clothes.User_Id == user_id
        ).first()
        
        if not clothe:
            return {"error": "Clothing item not found"}

        # 색상 예측
        clothe_color_result = await fetch_predict_color(clothe.Clothes_Color)
        if "error" in clothe_color_result:
            return clothe_color_result

        # 현재 온도에 맞는 옷 추천 범위 조회
        temperature_range = get_temperature_range(current_temperature)
        recommendations = clothing_recommendations.get(temperature_range, {})
        filtered_recommendations = {"tops": [], "bottoms": [], "outerwear": []}

        # 현재 옷이 추천 리스트에 포함되는지 확인
        if clothe.Clothes_Category not in [item for sublist in recommendations.values() for item in sublist]:
            return 0

        # 옷 카테고리 예측
        nomination_cody = await fetch_predict_category(clothe.Clothes_Category)
        if "error" in nomination_cody:
            return nomination_cody

        # 사용자의 모든 옷 데이터 조회
        all_clothes = db.query(Clothes).filter(
            Clothes.User_Id == user_id
        ).all()

        # 카테고리와 색상별 옷 데이터를 딕셔너리에 저장
        clothes_lookup = {}
        for cloth in all_clothes:
            key = (cloth.Clothes_Category, cloth.Clothes_Color)
            if key not in clothes_lookup:
                clothes_lookup[key] = []
            clothes_lookup[key].append(cloth.Clothes_Id)

        # 추천 리스트 필터링
        for category, items in recommendations.items():
            if category not in filtered_recommendations:
                continue
            for item in items:
                # 현재 옷 카테고리와 직접 매칭
                if item == clothe.Clothes_Category:
                    filtered_recommendations[category].append(clothe.Clothes_Id)
                
                # 추천 카테고리와 예측된 색상 매칭
                if item in nomination_cody:
                    for predicted_color in clothe_color_result:
                        key = (item, predicted_color)
                        if key in clothes_lookup:
                            filtered_recommendations[category].extend(clothes_lookup[key])

        return filtered_recommendations

    except Exception as e:
        return {"error": str(e)}
    
    finally:
        db.close()


# 온도만 가지고 추천
async def Clothes_push_by_temperature(user_id: str, current_temperature: int, db: Session):
    try:
        # 현재 온도에 맞는 상의 추천
        temperature_range = get_temperature_range(current_temperature)
        tops_recommendations = clothing_recommendations.get(temperature_range, {}).get("tops", [])

        # 사용자 상의 목록을 조회하여 카테고리와 색상 저장
        clothe_copy = []
        for top in tops_recommendations:
            clothes = db.query(Clothes).filter(
                Clothes.Clothes_Category == top, 
                Clothes.User_Id == user_id
            ).all()
            clothe_copy.extend(clothes)

        # 비동기적으로 카테고리 예측 작업 수행
        category_results = await asyncio.gather(
            *(cody.predict_category(category=clothe.Clothes_Category) for clothe in clothe_copy)
        )
        category_results_dict = dict(zip((clothe.Clothes_Id for clothe in clothe_copy), category_results))

        # 비동기적으로 색상 예측 작업 수행
        color_results = await asyncio.gather(
            *(predictcolor.predict_color(color=clothe.Clothes_Color) for clothe in clothe_copy)
        )
        color_results_dict = dict(zip((clothe.Clothes_Id for clothe in clothe_copy), color_results))

        # 추천 아이템 필터링
        recommendations = clothing_recommendations.get(temperature_range, {})
        filtered_recommendations = {}

        for category, items in recommendations.items():
            for item in items:
                for clothe in clothe_copy:
                    if clothe.Clothes_Id not in filtered_recommendations and clothe.Clothes_Category == item:
                        filtered_recommendations[clothe.Clothes_Id] = {"tops": [], "bottoms": [], "outerwear": []}
                        filtered_recommendations[clothe.Clothes_Id][category].append(clothe.Clothes_Id)

                    if clothe.Clothes_Id in category_results_dict:
                        predicted_categories = category_results_dict.get(clothe.Clothes_Id, [])
                        if item in predicted_categories and clothe.Clothes_Id in color_results_dict:
                            predicted_colors = color_results_dict.get(clothe.Clothes_Id, [])
                            for color in predicted_colors:
                                clothe_match = db.query(Clothes).filter(
                                    Clothes.Clothes_Category == item,
                                    Clothes.Clothes_Color == color,
                                    Clothes.User_Id == user_id
                                ).first()
                                if clothe_match:
                                    if clothe.Clothes_Id not in filtered_recommendations:
                                        filtered_recommendations[clothe.Clothes_Id] = {"tops": [], "bottoms": [], "outerwear": []}
                                    if clothe_match.Clothes_Id not in filtered_recommendations[clothe.Clothes_Id][category]:
                                        filtered_recommendations[clothe.Clothes_Id][category].append(clothe_match.Clothes_Id)

        # bottoms 리스트가 비어있는 항목 제거
        filtered_recommendations = {
            id: items for id, items in filtered_recommendations.items() if len(items["bottoms"]) > 0
        }

        return filtered_recommendations

    finally:
        db.close()