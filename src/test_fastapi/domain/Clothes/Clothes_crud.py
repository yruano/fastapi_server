import matplotlib.pyplot as plt
import colorsys
from datetime import datetime

from models import Clothes, User
from sqlalchemy.orm import Session


def create_Clothes(db: Session, _clothe: Clothes):
    db_Clothe = Clothes(
                    Clothes_Create_Date = datetime.now(),
                    Clothes_LastFit_Date = datetime.now(),
                    Clothes_Category = _clothe.Clothes_Category,
                    Clothes_Image = _clothe.Clothes_Image,
                    Clothes_Count = 0,
                    Clothes_Score = 0,
                    Clothes_Color = _clothe.Clothes_Color,
                    Clothes_Tone = _clothe.Clothes_Tone,
                    User_Id = _clothe.User_Id,
                    User = _clothe.User,
                )
    db.add(db_Clothe)
    db.commit()


def modify_Clothes(clothe_id: int, user_id: str, modify_clothe: Clothes, db: Session):
    original_user = db.query(Clothes).filter(Clothes.User_Id == user_id, Clothes.Clothes_Id == clothe_id).first()
    
    for attr in ['Clothes_Category', 'Clothes_Image']:
        new_value = getattr(modify_clothe, attr)
        if new_value != "" and new_value is not None:
            setattr(original_user, attr, new_value)
    
    db.add(original_user)
    db.commit()
    return check_Clothes_data(db = db, category = None, clothe_id = clothe_id, user_id = user_id)


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


def hex_to_rgb(hex_color):
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    max_value = max(r, g, b)
    min_value = min(r, g, b)
    mid_value = r + g + b - max_value - min_value

    # #7ebc8f이런 느낌의 계열의 색은 어떻게 처리 해야하는거지 톤을 하나 더 찾아야하나
    if abs(r - g) < 30 and abs(g - b) < 30 and abs(b - r) < 30:
        return "pastel tone"
    elif min_value <= 40 and min_value < max_value and min_value <= mid_value:
        return "deep tone"
    elif r == g == b:
        return "mono tone"
    # elif max_value == 255 and min_value < 255:
    #     return "vivid tone"
    else:
        # 여기에 들어오면 그 값을 근사 톤을 찾아서 넣어주는 형식으로 하는게 제일 좋은데
        # 그러면 그 근사톤을 구하는 알고리즘을 만들어야함
        return "vivid tone"

def show_color_and_tone(hex_color):
    return hex_to_rgb(hex_color)