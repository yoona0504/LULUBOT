import csv
from datetime import datetime

CSV_FILE = 'emotion_log.csv'

def save_emotion_log(emotion_dict):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for emotion, value in emotion_dict.items():
            writer.writerow([now, emotion, round(value * 100, 2)])

def load_recent_logs(limit=10):
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            logs = reader[-limit:]
            return [
                {"time": row[0], "emotion": row[1], "score": float(row[2])}
                for row in reversed(logs)
            ]
    except FileNotFoundError:
        return []
    