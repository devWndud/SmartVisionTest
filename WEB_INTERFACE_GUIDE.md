# 웹 인터페이스 사용 가이드

## 🚀 실행 방법

### 1. 서버 시작
```bash
python app.py
```

서버가 시작되면 다음 메시지가 표시됩니다:
```
Starting Flask server...
Open http://localhost:5000 in your browser
```

### 2. 웹 브라우저에서 접속
- 로컬 접속: `http://localhost:5000`
- 서버에서 실행 시: `http://서버IP:5000`

## 📋 기능

### 주요 기능
1. **이미지 업로드**: 카메라 이미지 업로드
2. **포인트 클라우드 업로드**: 선택사항 (없으면 더미 데이터 사용)
3. **실시간 분석**: 객체 탐지 및 경로 계획
4. **결과 시각화**: 웹에서 결과 확인

### 분석 결과 표시
- **객체 탐지 결과 이미지**: YOLO로 탐지된 객체 표시
- **권장 주행 각도**: 장애물이 가장 적은 방향
- **이동 객체 수**: 탐지된 이동 객체 개수
- **고정 객체 수**: 탐지된 고정 객체 개수
- **추천 각도 목록**: 상위 5개 각도

## 🔧 API 엔드포인트

### 1. 웹 인터페이스
- `GET /`: 메인 웹 페이지
- `POST /vision_process`: 이미지 처리 및 결과 반환

### 2. 기존 API (호환성 유지)
- `POST /vision_angle`: 각도만 반환 (기존 API)
- `POST /vision_visualize`: 시각화 이미지만 반환

## 📤 요청 형식

### 웹 인터페이스
- 이미지: `multipart/form-data` 형식으로 `img` 필드에 이미지 파일
- 포인트 클라우드: 선택사항, `point` 필드에 포인트 클라우드 파일

### API 요청 예시 (curl)
```bash
curl -X POST http://localhost:5000/vision_process \
  -F "img=@image.jpg" \
  -F "point=@pointcloud.npy"
```

## 🖥️ 서버 배포

### 고사양 서버에서 실행

1. **방화벽 설정**
   ```bash
   # 포트 5000 열기 (Ubuntu/Debian)
   sudo ufw allow 5000
   ```

2. **프로덕션 모드 실행**
   ```python
   # app.py 마지막 줄 수정
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```

3. **Gunicorn 사용 (권장)**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Nginx 리버스 프록시 (선택사항)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## ⚠️ 주의사항

1. **GPU 필요**: TensorRT 모델 사용으로 인해 NVIDIA GPU 필요
2. **메모리**: 최소 4GB GPU 메모리 권장
3. **파일 크기**: 최대 50MB까지 업로드 가능
4. **포트**: 기본 포트 5000 사용 (변경 가능)

## 🐛 문제 해결

### 이미지 업로드 실패
- 이미지 형식 확인 (JPEG, PNG 지원)
- 파일 크기 확인 (50MB 이하)

### 처리 오류
- GPU 메모리 부족 시 배치 크기 줄이기
- Darknet 모델 파일 확인

### 웹 페이지 접속 불가
- 방화벽 설정 확인
- 포트가 다른 프로세스에 사용 중인지 확인

## 📝 예제 사용법

1. 웹 브라우저에서 `http://localhost:5000` 접속
2. 이미지 파일 선택 (필수)
3. 포인트 클라우드 파일 선택 (선택사항)
4. "분석 시작" 버튼 클릭
5. 결과 확인

