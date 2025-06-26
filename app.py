from flask import Flask, render_template, request, jsonify
from utils.decode import decode_base64_image
from utils.face_detect import extract_face
from utils.predict import predict_emotion

app = Flask(__name__)

# 웹 페이지 렌더링
@app.route('/')
def index():
    return render_template('index.html')  # templates/index.html 불러옴

# 감정 분석 요청 처리
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        base64_img = data.get('image', None)
        if not base64_img:
            return jsonify({'error': '이미지 데이터가 없습니다.'}), 400

        # base64 → OpenCV 이미지로 디코딩
        frame = decode_base64_image(base64_img)

        # 얼굴 인식
        face = extract_face(frame)
        if face is None:
            return jsonify({'error': '얼굴을 찾을 수 없습니다.'}), 400

        # 감정 예측
        emotions, dominant = predict_emotion(face)

        return jsonify({
            'emotions': emotions,
            'dominant': dominant,
            'response': f"루루봇이 감지한 감정은 '{dominant}'입니다."
        })

    except Exception as e:
        return jsonify({'error': f"서버 오류: {str(e)}"}), 500

if __name__ == '__main__':
    # Pi에서도 외부에서 접속 가능하도록 host='0.0.0.0'
    app.run(host='0.0.0.0', port=5000, debug=True)