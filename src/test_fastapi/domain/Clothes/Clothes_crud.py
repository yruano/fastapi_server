import tensorflow as tf
import pandas as pd
from datetime import datetime
from models import Clothes
from sqlalchemy.orm import Session
from sklearn.preprocessing import LabelEncoder


def create_Clothes(db: Session, _clothe: Clothes):
    db_Clothe = Clothes(
                    Clothes_Create_Date = datetime.now(),
                    Clothes_LastFit_Date = datetime.now(),
                    Clothes_Category = _clothe.Clothes_Category,
                    Clothes_Image = _clothe.Clothes_Image,
                    Clothes_Count = 0,
                    Clothes_Score = 0,
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


async def predict_color(color: str):
    # 모델 로드
    ColorCombination_model = tf.keras.models.load_model('color_model240603.h5')

    # CSV 파일에서 데이터 읽기
    data = pd.read_csv('colorsDataSet240602.csv')
    
    # LabelEncoder를 만들기 위해 상의와 바지 색상을 합침
    combined_colors = pd.concat([data['tops'], data['bottoms']])

    # 색상을 숫자로 변환
    le = LabelEncoder()
    colors_encoded = le.fit_transform(combined_colors)
    
    # 학습 데이터에 없는 색상이 입력되면 오류를 방지
    if color not in le.classes_:
        return {"error": "Color not in training data"}

    # 색상을 숫자로 변환
    test_top_encoded = le.transform([color])

    # 예측
    predicted_bottom_probabilities = ColorCombination_model.predict(test_top_encoded.reshape(-1, 1))

    # 가장 높은 확률의 클래스로 변환
    top_n_predictions = tf.math.top_k(predicted_bottom_probabilities, k=3).indices.numpy()

    # 숫자를 다시 색상으로 변환
    predicted_bottoms = le.inverse_transform(top_n_predictions[0])

    print(predicted_bottoms.tolist())
    return predicted_bottoms.tolist()
