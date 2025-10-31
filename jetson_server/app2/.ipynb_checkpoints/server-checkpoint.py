from fastapi import FastAPI, UploadFile, File, HTTPException # FastAPI의 핵심 클래스와 파일 업로드 관련 타입 불러오기
from fastapi.middleware.cors import CORSMiddleware # CORS(Cross-Origin Resource Sharing) 허용을 위한 미들웨어
from fastapi.responses import StreamingResponse    # 이미지 응답을 스트리밍으로 내보낼 때 사용

# 파일 <-> 바이트 변환, 이미지 처리 라이브러리
from io import BytesIO
from PIL import Image
import numpy as np
import time   # 응답 지연(latency) 측정용

# YOLO 추론 모듈과 데이터 스키마 불러오기
from .yolo_service import YoloService
from .schemas import PredictOut, Detection
# from jetbot import Robot

# FastAPI 앱 객체 생성 (자동 문서화 /docs 에 표시될 제목/버전 지정)
app = FastAPI(title="Jetson FastAPI (YOLO)", version="1.0.0")

# CORS 설정 (다른 클라이언트(브라우저, Streamlit)에서 접근 가능하게 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 모든 도메인에서 접근 허용
    allow_credentials=True,
    allow_methods=["*"],        # 모든 HTTP 메소드 허용 (GET, POST, ...)
    allow_headers=["*"],        # 모든 헤더 허용
)

# YOLO 서비스 초기화 (가중치 파일 경로와 최소 신뢰도(conf) 지정)
yolo = YoloService(weights_path='app2/best_model.pt', conf=0.35)

# 서버 상태 확인용 엔드포인트
@app.get("/health")
def health():
    # yolo.device → CPU 또는 CUDA 장치 정보
    return {"status": "ok", "device": yolo.device}


# # 이미지 파일을 읽어 PIL 이미지와 NumPy 배열로 변환하는 유틸 함수
def _read_image(file: UploadFile):
    if not file.content_type:  # 콘텐츠 타입이 없을 경우
        raise HTTPException(status_code=400, detail="콘텐츠 타입이 없습니다.")
    if not (file.content_type.startswith("image/") or file.content_type == "application/octet-stream"):
        # 이미지가 아닌 파일은 거부
        raise HTTPException(status_code=400, detail="이미지 파일만 허용됩니다.")
    data = file.file.read()    # 파일을 바이트로 읽음
    if not data:               # 내용이 비어있으면 에러
        raise HTTPException(status_code=400, detail="빈 파일입니다.")
    pil = Image.open(BytesIO(data)).convert("RGB")  # PIL 이미지로 변환 (RGB 통일)
    arr = np.array(pil)                             # NumPy 배열로 변환 (모델 입력용)
    return pil, arr

# 1️⃣ JSON 응답을 주는 엔드포인트
@app.post("/predict", response_model=PredictOut)  # response_model → 자동 문서화/검증
async def predict(file: UploadFile = File(...)):  # File(...) → Swagger UI에서 업로드 버튼 자동 생성
    t0 = time.time()              # 시작 시간 (지연 측정)
    pil, arr = _read_image(file)  # 업로드 파일 읽기
    h, w = arr.shape[:2]          # 이미지 크기
    result = yolo.predict(arr)    # YOLO 추론 실행
    print(f"[Latency] /predict {((time.time()-t0)*1000):.1f} ms on {result['device']}")

    # 감지 결과를 Detection 모델 리스트로 변환
    det_objs = [
        Detection(cls=d['cls'], score=d['score'], box=tuple(d['box']))
        for d in result['detections']
    ]

    # PredictOut 형식으로 반환 (JSON)
    return PredictOut(
        filename=file.filename,
        width=w,
        height=h,
        device=result['device'],
        conf=result['conf'],
        detections=det_objs
    )

# 2️⃣ 시각화된 이미지를 반환하는 엔드포인트
@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    import cv2
    pil, arr = _read_image(file)                # 업로드 이미지 읽기
    result = yolo.predict(arr)                  # YOLO 추론 실행
    vis = yolo.draw(arr, result['detections'])  # 바운딩 박스 그리기

    # OpenCV로 JPEG 인코딩 (85% 품질)
    ok, encoded = cv2.imencode('.jpg', vis, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not ok:
        raise HTTPException(status_code=500, detail="이미지 인코딩 실패")

    # StreamingResponse로 바이트 스트림 반환 (Swagger나 클라이언트에서 바로 이미지 확인 가능)
    return StreamingResponse(BytesIO(encoded.tobytes()), media_type='image/jpeg')