# 가중치 파일 다운로드 가이드

## 가중치 파일 필요

프로젝트 실행을 위해 YOLOv3 가중치 파일이 필요합니다.

## 다운로드 방법

### Google Drive 링크
원작자가 제공한 가중치 파일:
```
https://drive.google.com/uc?id=1IefZF697bfpGyChBy8qqesA_FxoZs6nW&export=download
```

### 다운로드 후 위치

다운로드한 파일을 다음 중 하나의 이름으로 `darknet/` 폴더에 저장하세요:

**옵션 1 (권장):**
- 파일명: `obj_last_yolov3.weights`
- 위치: `./darknet/obj_last_yolov3.weights`

**옵션 2:**
- 파일명: `yolov3_obj.weights`
- 위치: `./darknet/yolov3_obj.weights`

코드는 두 파일명을 모두 지원합니다.

## 파일 크기

가중치 파일은 보통 200MB 이상입니다.

## 확인 방법

다운로드 후 다음 명령어로 확인:
```bash
dir darknet\*.weights
```

