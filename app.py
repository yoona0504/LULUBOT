
from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
import cv2
from emotion_analysis import analyze_emotion
from emotion_response import get_emotion_response

app = Flask(__name__)

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
