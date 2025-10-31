from typing import List, Tuple, Dict  # 타입 힌트용: 리스트, 튜플, 딕셔너리 자료형 명시
import numpy as np  # 이미지/수치 데이터를 다룰 때 필수 라이브러리

# Torch(CUDA) 사용 여부 체크
try:
    import torch
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'  
    # GPU(cuda)가 가능하면 cuda, 아니면 cpu로 설정
except Exception:
    DEVICE = 'cpu'  # torch 설치 안 되어 있거나 에러 발생 시 cpu 강제

from ultralytics import YOLO  # YOLOv8/11 모델 로딩 및 추론 라이브러리

# ===============================
# YOLO 추론 서비스 클래스 정의
# ===============================
class YoloService:
    def __init__(self, weights_path: str = 'app2/yolo11n.pt', conf: float = 0.35):
        """
        초기화 메서드
        :param weights_path: YOLO 모델 가중치 파일 경로
        :param conf: 최소 confidence threshold (0~1)
        """
        self.conf = conf
        self.model = YOLO(weights_path)  # 지정된 가중치 로딩
        self.device = DEVICE  # cuda 또는 cpu 기록

    def predict(self, img_rgb: np.ndarray) -> Dict:
        """
        YOLO 모델 추론 수행
        :param img_rgb: RGB 형태의 입력 이미지 (numpy 배열)
        :return: 추론 결과(JSON/dict) - device, conf, detections 목록
        """
        res = self.model.predict(source=img_rgb, conf=self.conf, verbose=False)  
        # source: 이미지, conf: 임계값, verbose: 로그 최소화

        dets: List[Dict] = []  # 탐지 결과 저장 리스트
        if res:  
            r = res[0]  # 단일 이미지이므로 첫 결과만 사용
            boxes = r.boxes  # 바운딩 박스 정보
            if boxes is not None:
                xyxy = boxes.xyxy.cpu().numpy()  # (x1, y1, x2, y2) 좌표
                conf = boxes.conf.cpu().numpy()  # confidence 값
                cls  = boxes.cls.cpu().numpy()   # 클래스 ID
                for i in range(len(xyxy)):
                    x1, y1, x2, y2 = xyxy[i].astype(int).tolist()  # 픽셀 좌표 int 변환
                    score = float(conf[i])  # confidence 스코어
                    cid = int(cls[i])       # 클래스 ID 숫자
                    name = r.names.get(cid, str(cid))  # 클래스 이름 (예: person, dog 등)
                    dets.append({
                        'cls': name,
                        'score': score,
                        'box': [x1, y1, x2, y2]
                    })
        return {'device': self.device, 'conf': self.conf, 'detections': dets}

    def draw(self, img_rgb: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        추론된 결과를 이미지에 시각적으로 그려주는 함수
        :param img_rgb: 원본 RGB 이미지 (numpy 배열)
        :param detections: predict() 결과의 detections 리스트
        :return: 바운딩 박스, 라벨이 그려진 이미지
        """
        import cv2
        vis = img_rgb.copy()  # 원본 이미지 복사본에 그림
        for d in detections:
            x1, y1, x2, y2 = map(int, d['box'])  # 바운딩 박스 좌표
            label = f"{d['cls']} ({d['score']:.2f})"  # 라벨 + confidence
            # 바운딩 박스 그리기 (주황색, 두께 2)
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 165, 255), 2)
            # 라벨 배경 크기 계산
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            y_text = max(20, y1 - 8)  # 글자가 이미지 위로 안 넘어가도록 보정
            # 라벨 배경 박스 (주황색, 채움)
            cv2.rectangle(vis, (x1, y_text - th - 6), (x1 + tw + 4, y_text + 4), (0, 165, 255), -1)
            # 라벨 텍스트 (검정색 글자)
            cv2.putText(vis, label, (x1 + 2, y_text),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        return vis