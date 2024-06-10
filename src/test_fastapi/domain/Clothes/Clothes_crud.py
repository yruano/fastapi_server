from datetime import datetime
from models import Clothes
from sqlalchemy.orm import Session
from learning_model import predictcolor


clothing_recommendations = {
    "28~": {
        "outerwear": [],
        "tops": ["sleeveless", "short_sleeve shirt", "short_sleeves"],
        "bottoms": ["half_pants", "Short_Skirt"],
        "misc": ["Linen Dress"]
    },
    "23~27": {
        "outerwear": [],
        "tops": ["short_sleeve shirt", "long_sleeve shirt", "halfKnit", "thin_shirt", "short_sleeves"],
        "bottoms": ["chino-cotton", "half_pants"],
        "misc": []
    },
    "20~22": {
        "outerwear": ["thin_cardigan"],
        "tops": ["long_sleeve shirt", "hood", "hood_zip-up", "blouse", "V-neck_knit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "cropped_pants", "Long_Skirt"],
        "misc": []
    },
    "17~19": {
        "outerwear": ["Windbreaker", "Blouson", "Zip-Up_Knit", "thin_jacket"],
        "tops": ["hood", "sweatshirt", "blazer", "thin_knit"],
        "bottoms": ["chino-cotton", "denim_pants", "slacks", "skinny_pants", "Long_Skirt"],
        "misc": []
    },
    "12~16": {
        "outerwear": ["Blouson", "Zip-Up_Knit", "denim-jacket", "cardigan", "field_jacket"],
        "tops": ["sweatshirt", "long_sleeve shirt", "hood_zip-up", "fleece_hoodie", "Long_Skirt"],
        "bottoms": ["denim_pants", "chino-cotton"],
        "misc": ["stockings", "normalKnit"]
    },
    "9~11": {
        "outerwear": ["Blouson", "denim-jacket", "blazer", "trench_coat", "field_jacket", "jumper"],
        "tops": [],
        "bottoms": ["denim_pants", "chino-cotton", "layered", "fleece"],
        "misc": ["normalKnit"]
    },
    "5~8": {
        "outerwear": ["wool_coat", "leather_jacket"],
        "tops": [],
        "bottoms": ["leggings", "denim_pants", "thick_pants", "fleece_pants"],
        "misc": ["scarf", "fleece", "thermal_underwear", "normalKnit"]
    },
    "~4": {
        "outerwear": ["padding", "thick_coat"],
        "tops": [],
        "bottoms": [],
        "misc": []
    }
}


# 그러고 https://namu.wiki/w/%EA%B8%B0%EC%98%A8%EB%B3%84%20%EC%98%B7%EC%B0%A8%EB%A6%BC 이걸 기준
def find_temperature_for_clothing(clothing_item):
    results = []
    for temperature, categories in clothing_recommendations.items():
        for category, items in categories.items():
            if clothing_item in items:
                results.append(temperature)
    return results

def create_Clothes(db: Session, _clothe: Clothes):
    db_Clothe = Clothes(
                    Clothes_Create_Date = datetime.now(),
                    Clothes_LastFit_Date = datetime.now(),
                    Clothes_Category = _clothe.Clothes_Category,
                    Clothes_Image = _clothe.Clothes_Image,
                    Clothes_Count = 0,
                    Clothes_Score = find_temperature_for_clothing(_clothe.Clothes_Category),
                    Clothes_Color = _clothe.Clothes_Color,
                    User_Id = _clothe.User_Id,
                    User = _clothe.User,
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

# 옷을 선택하고 그 옷에 맞는 추천이면
# 색 조합을 찾는다
# 색에 맞는 옷들 중 온도에 맞는 옷을들 선별해서 출력

# 온도에 맞는 옷을 추천
# 가능한 조합들을 저장
# 조합들 중 온도에 맞는 조합만 출력

# 너무 추운 겨울에는 외투를 필수로 넣고 거기에 후두티 맨투맨 등으로 조합해서 추가적으로 넣는 방식을 쓰던
# 12~16에 맞추어 선별을 하고 그다음 외투를 추가적을 선정하던 이런 방식
async def Clothes_push(clothe_id: int, user_id: str, current_temperature: int, db: Session):
    clothe = db.query(Clothes).filter(Clothes.Clothes_Id == clothe_id, Clothes.User_Id == user_id).first()
    # 색 추천
    clothe_color = await predictcolor.predict_color(color=clothe.Clothes_Color)
    
    if "error" in clothe_color:
        return clothe_color
    
    # 현재 온도에 맞는 옷 추천
    temperature_range = get_temperature_range(current_temperature)
    recommendations = clothing_recommendations.get(temperature_range, {})
    filtered_recommendations = {"tops": [], "bottoms": [], "outerwear": []}
    
    for category, items in recommendations.items():
        filtered_items = []
        for item in items:
            for predicted_color in clothe_color:
                if predicted_color in item:
                    filtered_items.append(item)
        if filtered_items:
            if category in ["tops"]:
                filtered_recommendations["tops"].extend(filtered_items)
            elif category in ["bottoms"]:
                filtered_recommendations["bottoms"].extend(filtered_items)
            elif category in ["outerwear"]:
                filtered_recommendations["outerwear"].extend(filtered_items)
    
    return filtered_recommendations