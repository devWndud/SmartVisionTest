#-*- coding:utf-8 -*-
from flask import Flask, request, jsonify, send_file, render_template, Response
import numpy as np
from util.selly_vision_api import *
from util.visualizer import *
from util.object_dection import YOLO
from PIL import Image
import base64
import io
import time
import cv2
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """메인 웹 페이지"""
    return render_template('index.html')

@app.route('/vision_angle', methods=['POST'])
def vision_angle():
    """기존 API: 각도만 반환"""
    if request.method == 'POST':
        img = request.files['img']
        img_bytes = img.read()
        point = request.files['point']
        point_bytes = point.read()
        result = selly_vision(img_bytes, point_bytes)[1]
    return str(result)

@app.route('/vision_process', methods=['POST'])
def vision_process():
    """웹 인터페이스용: 이미지와 포인트 클라우드를 받아서 처리 결과 반환"""
    try:
        # 이미지 파일 받기
        if 'img' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        img_file = request.files['img']
        if img_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # 포인트 클라우드 파일 받기 (선택사항)
        point_file = None
        if 'point' in request.files:
            point_file = request.files['point']
        
        # 이미지 읽기
        img_bytes = img_file.read()
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # 이미지 크기 조정 (480x270)
        img = cv2.resize(img, (480, 270))
        img = img.astype(np.float32)
        
        # 포인트 클라우드 처리
        if point_file and point_file.filename != '':
            point_bytes = point_file.read()
            point_array = np.frombuffer(point_bytes, dtype=np.float32)
            point = np.reshape(point_array, (67, 120, 3))
        else:
            # 포인트 클라우드가 없으면 더미 데이터 생성 (테스트용)
            point = np.ones((67, 120, 3), dtype=np.float32) * 10.0
        
        # 비전 처리
        result_angles = selly_vision_redis(img.copy(), point.copy(), moving_dist=5, fixed_dist=2.5)
        
        # 시각화를 위한 처리
        try:
            # visualize 함수 사용 (더미 파라미터)
            # 실제로는 간단한 시각화만 수행
            obj_frame, moving_object, fixed_object = YOLO(img.copy())
            
            # 결과 이미지 인코딩
            result_img = obj_frame.copy()
            result_img = np.clip(result_img, 0, 255).astype(np.uint8)
            
            # 이미지를 base64로 인코딩
            _, buffer = cv2.imencode('.jpg', result_img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 각도 정보 추출
            angles = []
            if len(result_angles) > 0:
                angles = [float(angle[0]) for angle in result_angles[:5]]  # 상위 5개 각도
            
            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{img_base64}',
                'angles': angles,
                'recommended_angle': float(result_angles[0][0]) if len(result_angles) > 0 else 0.0,
                'moving_objects': len(moving_object),
                'fixed_objects': len(fixed_object)
            })
        except Exception as e:
            return jsonify({
                'success': True,
                'angles': [float(angle[0]) for angle in result_angles[:5]] if len(result_angles) > 0 else [],
                'recommended_angle': float(result_angles[0][0]) if len(result_angles) > 0 else 0.0,
                'error': f'Visualization failed: {str(e)}'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vision_visualize', methods=['POST'])
def vision_visualize():
    """시각화 결과를 이미지로 반환"""
    try:
        img_file = request.files['img']
        point_file = request.files.get('point')
        
        # 이미지 읽기
        img_bytes = img_file.read()
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (480, 270))
        img = img.astype(np.float32)
        
        # 포인트 클라우드 처리
        if point_file and point_file.filename != '':
            point_bytes = point_file.read()
            point_array = np.frombuffer(point_bytes, dtype=np.float32)
            point = np.reshape(point_array, (67, 120, 3))
        else:
            point = np.ones((67, 120, 3), dtype=np.float32) * 10.0
        
        # 시각화
        obj_frame, moving_object, fixed_object = YOLO(img.copy())
        result_img = obj_frame.copy()
        result_img = np.clip(result_img, 0, 255).astype(np.uint8)
        
        # 이미지 반환
        _, buffer = cv2.imencode('.jpg', result_img)
        return Response(buffer.tobytes(), mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import sys
    # 포트를 명령줄 인자로 받거나 기본값 사용
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Starting Flask server on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    app.run(host='0.0.0.0', port=port, debug=True)
