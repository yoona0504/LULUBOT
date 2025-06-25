// 웹캠 연결
const video = document.getElementById('video');
const photo = document.getElementById('photo');
const responseText = document.getElementById('response');
const captureBtn = document.getElementById('captureBtn');
const emotionChartCtx = document.getElementById('emotionChart').getContext('2d');

let stream = null;
let emotionChart = null;

// 1. 웹캠 시작
navigator.mediaDevices.getUserMedia({ video: true })
  .then(s => {
    stream = s;
    video.srcObject = stream;
    captureBtn.disabled = false;
  })
  .catch(err => {
    console.error("웹캠 접근 실패:", err);
    captureBtn.disabled = true;
  });

// 2. 버튼 클릭 시 캡처 + 분석
function capture() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // 이미지 표시
  const imageDataURL = canvas.toDataURL('image/jpeg');
  photo.src = imageDataURL;

  // 서버로 전송
  fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageDataURL })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      responseText.textContent = '오류: ' + data.error;
      return;
    }

    responseText.textContent = `루루봇: ${data.response} (감정: ${data.dominant})`;

    // 차트 업데이트
    updateChart(data.emotions);
  })
  .catch(err => {
    console.error(err);
    responseText.textContent = '분석 실패';
  });
}

// 3. 감정 차트 그리기
function updateChart(emotions) {
  const labels = Object.keys(emotions);
  const values = labels.map(label => Math.round(emotions[label] * 100));

  if (emotionChart) emotionChart.destroy();

  emotionChart = new Chart(emotionChartCtx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: '감정 분석 (%)',
        data: values,
        backgroundColor: 'rgba(54, 162, 235, 0.6)'
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  });
}
