
from deepface import DeepFace

def analyze_emotion(frame):
    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
    raw = result[0]['emotion']
    emotions = {k: float(v) for k, v in raw.items()}
    dominant = result[0]['dominant_emotion']
    return emotions, dominant
