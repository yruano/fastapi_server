import tensorflow as tf
import pandas as pd
from datetime import datetime
from models import Clothes
from sqlalchemy.orm import Session
from sklearn.preprocessing import LabelEncoder


tops = [""]
bottoms = [""]


# 카테고리 영어로 된 데이터 셋을 받아야 하는군
# 그러고 https://namu.wiki/w/%EA%B8%B0%EC%98%A8%EB%B3%84%20%EC%98%B7%EC%B0%A8%EB%A6%BC이걸 기준
# 값을 지정하는 코드를 작성해야함
def create_temperature(category: str):
    # 파이썬에서 맵의 값을 이용해서 키를 구하는 방법이 있는지 확인 해야함
    # 존재하지 않은 값들도 추가적으로 넣어줘야함
    # 값의 변화를 주거나 다른 값들이 들어가는 상황이 나오려나?
    pass

def create_Clothes(db: Session, _clothe: Clothes):
    # 여기서 온도를 확인하는 코드던 모델을 쓰던해서 값을 넣어두자
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

# 옷을 선택하고 그 옷에 맞는 추천이면
# 색 조합을 찾는다
# 색에 맞는 옷들 중 온도에 맞는 옷을들 선별해서 출력

# 온도에 맞는 옷을 추천
# 가능한 조합들을 저장
# 조합들 중 온도에 맞는 조합만 출력

# 너무 추운 겨울에는 외투를 필수로 넣고 거기에 후두티 맨투맨 등으로 조합해서 추가적으로 넣는 방식을 쓰던
# 12~16에 맞추어 선별을 하고 그다음 외투를 추가적을 선정하던 이런 방식
async def Clothes_push(clothe_id: int, user_id: str, db: Session):
    # clothe_push = list(map(Clothes, Clothes))

    # clothe = db.query(Clothes).filter(Clothes.Clothes_Id == clothe_id, Clothes.User_Id == user_id).first()
    # # 색 추천
    # clothe_color = await predict_color(color = clothe.Clothes_Color)
    
    # 여기서 현재 확인하고 있는 옷이 위인지 아래인 확인할 필요가 있음

    # for ca in tops:
    #     clo = db.query(Clothes).filter(Clothes.Clothes_Category == ca, Clothes.Clothes_Color == clothe_color, Clothes.User_Id == user_id).first()
    # sss는 현재의 온도를 의미
    #     if abs(clothe + clo - sss) < 10:
    #         clothe_push[clothe] = clo
    pass