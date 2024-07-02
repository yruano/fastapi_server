import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import LabelEncoder


async def predict_category(category: str):
    # 레이블 인코더 로드
    le_tops = LabelEncoder()
    le_bottoms = LabelEncoder()

    # CSV 파일에서 데이터 읽기
    data = pd.read_csv('CodyDataSet2.csv')

    # 레이블 인코더 학습
    le_tops.fit(data['tops'])
    le_bottoms.fit(data['bottoms'])
    # 모델 로드
    CategoryCombination_model = tf.keras.models.load_model('Cody_model240702_v1.h5')
    
    # 학습 데이터에 없는 카테고리가 입력되면 오류를 방지
    if category not in le_tops.classes_:
        return {"error": "category not in training data"}

    # 카테고리를 숫자로 변환
    test_category_encoded = le_tops.transform([category])

    # 예측
    predicted_probabilities = CategoryCombination_model.predict(test_category_encoded.reshape(-1, 1))

    # 가장 높은 확률의 클래스로 변환
    predictions = tf.argsort(predicted_probabilities, direction='DESCENDING')[:, :3].numpy()

    # 숫자를 다시 카테고리로 변환
    predicted_bottoms = le_bottoms.inverse_transform(predictions[0])

    return predicted_bottoms.tolist()
