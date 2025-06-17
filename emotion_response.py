
def get_emotion_response(emotion):
    responses = {
        'happy': "루루봇: 기분이 좋아 보여요! 같이 신나볼까요?",
        'sad': "루루봇: 울고 싶을 땐 울어도 괜찮아요. 내가 옆에 있을게요.",
        'angry': "루루봇: 천천히 숨 쉬어요. 같이 진정해봐요.",
        'surprise': "루루봇: 오! 무슨 일이 있었어요?",
        'fear': "루루봇: 무서웠군요. 제가 곁에 있어줄게요.",
        'disgust': "루루봇: 싫은 일이 있었군요. 털어버려요!",
        'neutral': "루루봇: 평온한 하루네요. 함께 여유를 즐겨요.",
    }
    return responses.get(emotion, "루루봇: 오늘도 당신을 응원해요!")
