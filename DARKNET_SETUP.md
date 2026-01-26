# Darknet 파일 획득 가이드

## 방법 1: 원작자 저장소에서 확인 (가장 권장)

README에 따르면 원작자가 별도 저장소를 사용합니다:
- **Object Detection 저장소**: https://github.com/JunHyeok96/object-dection

이 저장소에 필요한 파일들이 있을 가능성이 높습니다:
- `darknet/cfg/obj.cfg`
- `darknet/obj_last_yolov3.weights`
- `darknet/cfg/obj.data`

## 방법 2: Darknet 직접 설치 및 설정

### 2-1. Darknet 설치 (Windows)

```bash
# 1. Darknet 클론
git clone https://github.com/AlexeyAB/darknet.git
cd darknet

# 2. Windows용 빌드 (Visual Studio 필요)
# build\darknet\yolo_cpp_dll.sln 파일을 Visual Studio로 열어서 빌드
# 또는 CMake 사용
```

### 2-2. Python 바인딩 설치

```bash
# 방법 A: pjreddie의 darknet (간단하지만 오래됨)
pip install darknetpy

# 방법 B: AlexeyAB의 darknet Python 바인딩
# https://github.com/AlexeyAB/darknet#how-to-compile-on-windows
```

### 2-3. 필요한 파일 구조 생성

프로젝트 루트에 다음 구조 생성:
```
./darknet/
├── cfg/
│   ├── obj.cfg
│   └── obj.data
└── obj_last_yolov3.weights
```

### 2-4. 커스텀 모델 파일 생성

이 프로젝트는 **커스텀 학습된 모델**을 사용하므로:
- **29개 클래스** 탐지 (이동 객체 13개 + 고정 객체 16개)
- 표준 COCO 모델로는 대체 불가능
- 원작자에게 파일 요청하거나 직접 학습 필요

## 방법 3: 임시 해결책 - 객체 탐지 비활성화

객체 탐지 없이 segmentation만으로 테스트하려면:

`util/object_dection.py`를 수정하여 빈 결과 반환:

```python
def YOLO(frame):
    # 임시로 빈 결과 반환
    return frame, [], []
```

## 방법 4: OpenCV DNN으로 대체 (고급)

표준 YOLOv3를 OpenCV DNN으로 사용 (클래스는 다름):

```python
# COCO 클래스만 탐지 가능 (person, car, bicycle 등 일부만)
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
```

하지만 이 프로젝트의 커스텀 클래스들(barricade, bollard, kiosk 등)은 탐지 불가.

## 추천 순서

1. **원작자 저장소 확인**: https://github.com/JunHyeok96/object-dection
2. **원작자에게 이슈/이메일로 파일 요청**
3. **임시로 객체 탐지 비활성화하여 segmentation만 테스트**
4. **필요시 커스텀 모델 직접 학습**

## 필요한 클래스 목록

### 이동 객체 (13개)
bicycle, bus, car, carrier, cat, dog, motorcycle, movable_signage, person, scooter, stroller, truck, wheelchair

### 고정 객체 (16개)
barricade, bench, bollard, chair, fire_hydrant, kiosk, parking_meter, pole, potted_plant, power_controller, stop, table, traffic_light, traffic_light_controller, traffic_sign, tree_trunk

