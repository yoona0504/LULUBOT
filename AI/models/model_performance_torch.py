import cv2
import dlib
import torch
import numpy as np
from torchvision import transforms
from model import EmotionNet, CBAM 
from config import EMOTION_LABELS 
from PIL import Image

MODEL_PATH = ''
PREDICTOR_PATH = './face_landmarks.dat'
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def align_face(gray, predictor):
    detector = dlib.get_frontal_face_detector()
    rects = detector(gray, 1)
    if len(rects) == 0:
        raise Exception("얼굴이 감지되지 않았습니다.")

    shape = predictor(gray, rects[0])
    landmarks = np.array([[p.x, p.y] for p in shape.parts()])

    left_eye = landmarks[36]
    right_eye = landmarks[45]

    left_eye_center = (int(left_eye[0]), int(left_eye[1]))
    right_eye_center = (int(right_eye[0]), int(right_eye[1]))

    dx = right_eye_center[0] - left_eye_center[0]
    dy = right_eye_center[1] - left_eye_center[1]
    angle = np.degrees(np.arctan2(dy, dx))

    center_x = (left_eye_center[0] + right_eye_center[0]) / 2
    center_y = (left_eye_center[1] + right_eye_center[1]) / 2
    center = (float(center_x), float(center_y))

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    aligned = cv2.warpAffine(gray, M, (gray.shape[1], gray.shape[0]), flags=cv2.INTER_CUBIC)
    return aligned

img = Image.open("").convert("RGB")
img_np = np.array(img)
img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#img = cv2.imread(IMAGE_PATH)
# if img is None:
#     raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {IMAGE_PATH}")
gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

predictor = dlib.shape_predictor(PREDICTOR_PATH)
aligned = align_face(gray, predictor)
face = cv2.resize(aligned, (224, 224))
face_rgb = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])
input_tensor = transform(face_rgb).unsqueeze(0).to(DEVICE)

model = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
model.to(DEVICE)
model.eval()


with torch.no_grad():
    output = model(input_tensor)
    probs = torch.softmax(output, dim=1).cpu().numpy()[0]

print("\n[softmax]")
for i, prob in enumerate(probs):
    print(f"{EMOTION_LABELS[i]}: {prob:.4f}")
print(f"예측된 감정: {EMOTION_LABELS[np.argmax(probs)]} (index: {np.argmax(probs)})")
