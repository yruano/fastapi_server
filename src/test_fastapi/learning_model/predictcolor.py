import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import LabelEncoder


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