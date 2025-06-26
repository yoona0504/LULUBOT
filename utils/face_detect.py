import face_recognition, cv2

def extract_face(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    if not locations: return None
    top, right, bottom, left = locations[0]
    return frame[top:bottom, left:right]
