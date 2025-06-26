import cv2, numpy as np
from tensorflow.keras.models import load_model

labels = ['angry', 'happy', 'neutral', 'sad', 'surprise']
model = load_model('emotion_model.h5')

def predict_emotion(face_img):
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    input_data = resized.reshape(1, 48, 48, 1) / 255.0
    preds = model.predict(input_data)[0]
    return dict(zip(labels, preds)), labels[np.argmax(preds)]
