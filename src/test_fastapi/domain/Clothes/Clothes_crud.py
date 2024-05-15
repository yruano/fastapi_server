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
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

def rgb_to_hsl(rgb_color):
    return colorsys.rgb_to_hls(rgb_color[0] / 255, rgb_color[1] / 255, rgb_color[2] / 255)

def determine_tone(hsl_color):
    h, l, s = hsl_color

    if l > 0.8:
        return 'pastel tone'
    elif l < 0.2 and s > 0.2:
        return 'deep tone'
    elif s < 0.2:
        return 'mono tone'
    else:
        return 'vivid tone'

def show_color_and_tone(hex_color):
    rgb_color = hex_to_rgb(hex_color)
    hsl_color = rgb_to_hsl(rgb_color)
    tone = determine_tone(hsl_color)

    return tone