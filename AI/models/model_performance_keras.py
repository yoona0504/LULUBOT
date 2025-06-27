import cv2
import dlib
import numpy as np
from tensorflow.keras.models import load_model


model = load_model('./models/emotion_model_v3.h5')
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./models/face_landmarks.dat")

def align_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if len(faces) == 0:
        print("얼굴 못 찾음")
        return None

    face = faces[0] 
    landmarks = predictor(gray, face)

    left_eye = np.array([landmarks.part(36).x, landmarks.part(36).y])
    right_eye = np.array([landmarks.part(45).x, landmarks.part(45).y])
    eye_center = (left_eye + right_eye) / 2

    dy = right_eye[1] - left_eye[1]
    dx = right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(dy, dx))

    M = cv2.getRotationMatrix2D(tuple(eye_center), angle, scale=1)
    aligned = cv2.warpAffine(gray, M, (gray.shape[1], gray.shape[0]))

    aligned = aligned[face.top():face.bottom(), face.left():face.right()]
    aligned = cv2.resize(aligned, (48, 48))
    return aligned

img = cv2.imread("")
aligned = align_face(img)

if aligned is not None:
    x = aligned.astype('float32') / 255.0
    x = np.expand_dims(x, axis=0)
    x = np.expand_dims(x, axis=-1) 

    pred = model.predict(x)[0]
    for i, p in enumerate(pred):
        print(f"{emotion_labels[i]}: {p:.4f}")

    print("예측:", emotion_labels[np.argmax(pred)])
