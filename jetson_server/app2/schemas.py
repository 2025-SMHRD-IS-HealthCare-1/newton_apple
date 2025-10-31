from typing import List, Tuple
from pydantic import BaseModel

# 개별 탐지 결과 (객체 하나에 해당)
class Detection(BaseModel):
    cls: str                     # 탐지된 객체의 클래스명 (예: 'person', 'dog')
    score: float                 # 신뢰도 점수 (0.0 ~ 1.0 사이 부동소수점)
    box: Tuple[int, int, int, int]  # 바운딩박스 좌표 (x1, y1, x2, y2)
                                  # - 좌상단(x1, y1), 우하단(x2, y2)

# 전체 추론 결과 (한 장의 이미지 단위)
class PredictOut(BaseModel):
    filename: str                # 업로드된 파일 이름
    width: int                   # 원본 이미지의 너비 (픽셀 단위)
    height: int                  # 원본 이미지의 높이 (픽셀 단위)
    device: str                  # 모델이 실행된 디바이스 (예: 'cpu', 'cuda:0')
    conf: float                  # 서버에서 설정한 최소 신뢰도 임계값
    detections: List[Detection]  # 탐지된 객체들의 리스트
                                  # - 비어있을 수도 있고, 여러 개가 들어올 수도 있음