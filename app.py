navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        const video = document.getElementById('video');
        video.srcObject = stream;
        video.onloadedmetadata = () => {
            document.getElementById('captureBtn').disabled = false;
        };
    });

function capture() {
    const video = document.getElementById('video');
    if (video.videoWidth === 0 || video.videoHeight === 0) {
        alert("카메라 준비 중입니다. 잠시 후 다시 시도해주세요.");
        return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg');
    document.getElementById('photo').src = dataUrl;

    fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataUrl })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('response').innerText = data.response;

        const ctx = document.getElementById('emotionChart').getContext('2d');
        const labels = Object.keys(data.emotions);
        const values = Object.values(data.emotions).map(v => v * 100);

        if (window.emotionChart) window.emotionChart.destroy();
        window.emotionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '감정 확률 (%)',
                    data: values,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    });
}