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


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsl(rgb_color):
    return colorsys.rgb_to_hls(rgb_color[0]/255, rgb_color[1]/255, rgb_color[2]/255)

def determine_tone(hsl_color):
    h, l, s = hsl_color

    if l > 0.8:
        return 'pastel tone'
    elif l < 0.2:
        return 'deep tone'
    elif s < 0.2:
        return 'mono tone'
    else:
        return 'vivid tone'

def show_color_and_tone(hex_color):
    rgb_color = hex_to_rgb(hex_color)
    hsl_color = rgb_to_hsl(rgb_color)
    return determine_tone(hsl_color)


def Coordination_Recommendation(db: Session, user_id: str):
    clothe = check_Clothes_data(category = None, clothe_id = None, db = db, user_id = user_id)
    # 빨강
    # 핑크
    # 노랑
    # 그린
    # 파란
    # 남색
    # 회색
    # 검정
    # 이거를 두가지 테이블로 만들어서 그테이블을 가지고 조합하는 형식으로 하는게 제일 좋은 방식 같은데
    # 그러면 테이블을 생성해야 한다
    # 생성 되어있다고 가정하면
    
    # 톤온톤
    # 1. 색 조합에 맞게 선별
    # 2. 같은 톤끼리 묶는다
    # 3. 톤별 배열에 값을 저장
    # 3. 그중 온도에 맞는 것들만 추출해서 추천

    # 톤인톤
    # 1. 색 조합에 맞게 선별
    # 2. 다른 톤끼리 묶는다
    # 4. 배열에 값을 저장
    # 5. 그중 온도에 맞는 것들만 추출해서 추천
    
    for c in clothe:
        color = getattr(c, 'Clothes_Color')
        clothe_id = getattr(c, 'Clothes_Id')
        
        

    pass