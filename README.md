# 장애물 탐지를 위한 이미지 분석 (Obstacle detection)
#### [개발 일지](https://jgrammer.tistory.com/category/Embedded/%EC%9E%90%EC%9C%A8%20%EC%A3%BC%ED%96%89%20%EB%B0%B0%EB%8B%AC%20%EB%A1%9C%EB%B4%87)

## 설치 방법 (Installation)

### 1. Git LFS 설치
이 저장소는 큰 파일들(모델 가중치 등)을 Git LFS로 관리합니다. 저장소를 클론하기 전에 Git LFS를 설치해야 합니다.

```bash
# Git LFS 설치 (Windows)
# https://git-lfs.github.com/ 에서 다운로드하거나
winget install Git.GitLFS

# Git LFS 설치 (Linux - Ubuntu/Debian)
sudo apt-get update
sudo apt-get install git-lfs

# Git LFS 설치 (Linux - CentOS/RHEL 7)
sudo yum install git-lfs

# Git LFS 설치 (Linux - CentOS/RHEL 8+ / Fedora)
sudo dnf install git-lfs

# Git LFS 설치 (Linux - 공식 스크립트 사용, 모든 배포판)
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash  # Debian/Ubuntu
# 또는
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash  # CentOS/RHEL/Fedora
sudo apt-get install git-lfs  # 또는 sudo yum install git-lfs

# Git LFS 설치 (macOS)
brew install git-lfs
```

### 2. 저장소 클론 및 LFS 파일 다운로드

**처음 클론하는 경우:**
```bash
# 저장소 클론
git clone https://github.com/devWndud/SmartVisionTest.git
cd SmartVisionTest

# Git LFS 초기화
git lfs install

# LFS 파일 다운로드 (가중치 파일 등)
git lfs pull
```

**이미 클론한 경우 (업데이트):**
```bash
# 프로젝트 디렉토리로 이동
cd SmartVisionTest

# Git LFS 초기화 (처음 한 번만 필요)
git lfs install

# LFS 파일 다운로드 (가중치 파일 등) - 필수!
git lfs pull

# 최신 코드 업데이트
git pull
```

**참고:** 
- `.weights` 파일과 `.pb` 파일은 Git LFS로 관리되므로, `git lfs pull`을 실행해야 실제 파일이 다운로드됩니다.
- `git pull`만으로는 코드만 업데이트되고 큰 파일은 다운로드되지 않습니다.
- LFS 파일이 제대로 다운로드되었는지 확인: `ls -lh darknet/yolov3_obj.weights` (약 235MB 파일이어야 함)

## 리눅스 서버에서 실행하기 (Running on Linux Server)

### 1. 시스템 요구사항
- **Python 3.7 이상**
- **NVIDIA GPU** (CUDA 지원, TensorRT 모델 사용)
- **CUDA 및 cuDNN** (TensorFlow GPU 지원)
- **최소 4GB RAM** (권장: 8GB 이상)
- **최소 10GB 디스크 공간** (모델 파일 포함)

### 2. 시스템 패키지 설치

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev
sudo apt-get install -y build-essential cmake git
sudo apt-get install -y libopencv-dev python3-opencv

# CUDA 및 cuDNN 설치 (GPU 사용 시)
# NVIDIA 공식 사이트에서 설치: https://developer.nvidia.com/cuda-downloads
```

### 3. Python 가상환경 설정 (권장)

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

### 4. Python 패키지 설치

```bash
# 프로젝트 디렉토리로 이동
cd SmartVisionTest

# 필수 패키지 설치
pip install -r requirements.txt

# GPU 지원 TensorFlow 설치 (선택사항, GPU가 있는 경우)
pip install tensorflow[and-cuda]
# 또는
pip install tensorflow-gpu
```

### 5. Darknet 설치 (YOLO 객체 탐지용)

Darknet은 Python 패키지가 아닌 C 라이브러리이므로 별도로 빌드해야 합니다:

```bash
# Darknet 클론
cd ~
git clone https://github.com/AlexeyAB/darknet.git
cd darknet

# GPU 지원으로 빌드 (GPU가 있는 경우)
# Makefile 수정: GPU=1, CUDNN=1, OPENCV=1
sed -i 's/GPU=0/GPU=1/' Makefile
sed -i 's/CUDNN=0/CUDNN=1/' Makefile
sed -i 's/OPENCV=0/OPENCV=1/' Makefile

# 빌드
make

# Python 바인딩 설치
cd python
python3 setup.py build
python3 setup.py install

# 또는 pip로 설치 (간단한 방법, 제한적)
pip install darknetpy
```

**중요:** `util/object_dection.py`에서 Darknet 경로를 확인하고 필요시 수정하세요.

### 6. 모델 파일 확인

```bash
# 가중치 파일 확인
ls -lh darknet/yolov3_obj.weights
# 출력: 약 235MB 파일이 있어야 함

# TensorRT 모델 확인
ls -lh trt_fp16/saved_model.pb
# 출력: 약 77MB 파일이 있어야 함
```

### 7. Flask 웹 서버 실행

```bash
# 개발 모드로 실행
python3 app.py

# 또는 프로덕션 환경에서는 Gunicorn 사용 권장
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**접속:** `http://서버IP:5000`

### 8. 소켓 서버 실행 (선택사항)

```bash
# 소켓 서버 실행
python3 soket_server.py
```

### 9. Redis 사용 (선택사항)

Redis를 사용하는 경우:

```bash
# Redis 설치
sudo apt-get install redis-server  # Ubuntu/Debian
sudo yum install redis            # CentOS/RHEL

# Redis 시작
sudo systemctl start redis
sudo systemctl enable redis

# Redis 처리 스크립트 실행
python3 redis_processing.py
```

### 10. 시스템 서비스로 등록 (프로덕션)

`/etc/systemd/system/smartvision.service` 파일 생성:

```ini
[Unit]
Description=SmartVision Flask Application
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/SmartVisionTest
Environment="PATH=/path/to/SmartVisionTest/venv/bin"
ExecStart=/path/to/SmartVisionTest/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartvision
sudo systemctl start smartvision
sudo systemctl status smartvision
```

### 문제 해결 (Troubleshooting)

**GPU가 인식되지 않는 경우:**
```bash
# CUDA 확인
nvidia-smi

# TensorFlow에서 GPU 확인
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

**Darknet import 오류:**
- Darknet이 제대로 빌드되고 설치되었는지 확인
- Python 경로에 darknet 모듈이 있는지 확인
- `util/object_dection.py`의 import 경로 확인

**메모리 부족 오류:**
- GPU 메모리 제한 설정 확인 (`util/selly_vision_api.py`의 `memory_limit` 조정)
- 배치 크기 줄이기
- 이미지 해상도 낮추기

![ezgif com-gif-maker (5)](https://user-images.githubusercontent.com/52908154/83791845-3a9f8880-a6d5-11ea-9430-b7e8c5af6c97.gif)


![ezgif com-video-to-gif (11)](https://user-images.githubusercontent.com/52908154/83790159-b4824280-a6d2-11ea-9675-6f9889b3a2b5.gif)

#### We will use [object detection](https://github.com/JunHyeok96/object-dection), [image segmentation](https://github.com/JunHyeok96/Road-Segmentation), and depth images to make judgments to avoid objects.  
  
 
### 1. Receive image and point cloud from camera.

<img src= "https://user-images.githubusercontent.com/52908154/83318785-f9415000-a272-11ea-940f-f129740a45a6.png" width="30%"></img>

### 2. Use object detection, image segmentation, depth images to determine obstacles.

<img src= "https://user-images.githubusercontent.com/52908154/83318927-699ca100-a274-11ea-94d5-7509acbe4ca4.png" width="80%"></img>


* #### Obstacle detection begins with the assumption that the portion of the segmentation that is not recognized as a sidewalk is an obstacle.

* #### However, considering errors in segmentation, it is more efficient to detect obstacles by object detection. Object detection was designated as the first priority.

<img src= "https://user-images.githubusercontent.com/52908154/83318934-889b3300-a274-11ea-8244-ae132426f4fc.png" width="80%"></img>

* #### The y-value of the point cloud was used to limit the effective range of obstacles.

### 3. We need to know which direction these obstacles are located.

<img src= "https://user-images.githubusercontent.com/52908154/83318705-2e00d780-a272-11ea-9742-ccf78f5603e9.png" width="40%"></img>

* #### Calculate the angle corresponding to each pixel with the x and z coordinates of the point cloud.

### 4. It is now time to distinguish the types of obstacles.

<img src= "https://user-images.githubusercontent.com/52908154/83318991-1d059580-a275-11ea-9887-1d738c98220d.png" width="80%"></img>

* #### Generally, for mobile devices, avoiding preparations should be made from a distance. 
* #### however,  For fixed things,  a closer distance can be accommodated.


![image](https://user-images.githubusercontent.com/52908154/83319146-b4b7b380-a276-11ea-868c-3b00d490db66.png)

* #### This part can be modified fluidly. 

### 5. Determine the path

![ezgif com-video-to-gif (10)](https://user-images.githubusercontent.com/52908154/83789689-0aa2b600-a6d2-11ea-8da6-2430c98cb9ce.gif)

* #### The number of pixels per angle was calculated for obstacles detected within 25 meters.
* #### And averaged the number of obstacle pixels between -10 and 10 degrees from each angle.
* #### The angle was selected by ordering the number of obstacle pixels low and close to 0 degrees.
* #### Among them, the angle with the least obstacles was selected.

#### The test environment is RTX2060 super (fps 15)
