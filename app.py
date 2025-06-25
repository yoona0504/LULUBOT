
from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
import cv2
from flask import Flask, render_template
from emotion_analysis import analyze_emotion
from log_utils import save_emotion_log, load_recent_logs
from emotion_response import get_emotion_response


app = Flask(__name__)

from flask import Flask, render_template
from emotion_analysis import analyze_emotion  # 기존 로직
from log_utils import save_emotion_log, load_recent_logs

app = Flask(__name__)

@app.route('/dashboard')
def dashboard():
    # 감정 분석 결과 가져오기 (테스트용으로 고정값)
    emotion_result = {
        "Happy": 0.65,
        "Sad": 0.20,
        "Angry": 0.10,
        "Neutral": 0.05
    }

    # 로그 저장 및 불러오기
    save_emotion_log(emotion_result)
    logs = load_recent_logs(limit=6)

    return render_template("dashboard.html", emotions=emotion_result, logs=logs)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json['image']
        _, encoded = data.split(",", 1)
        img_data = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        emotions, dominant = analyze_emotion(frame)
        response = get_emotion_response(dominant)

        return jsonify({'emotions': emotions, 'response': response, 'dominant': dominant})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
