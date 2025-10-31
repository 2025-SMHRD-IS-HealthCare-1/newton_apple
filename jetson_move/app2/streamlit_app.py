# streamlit_app.py

import os
import io
import requests
import streamlit as st

# ✅ 기본 서버 주소 설정
# - 환경변수 SERVER_URL이 있으면 그 값을 사용
# - 없으면 기본값으로 "http://127.0.0.1:8000" (로컬호스트) 사용
DEFAULT_SERVER = os.getenv("SERVER_URL", "http://127.0.0.1:8000")

# ✅ Streamlit 페이지 기본 설정
st.set_page_config(page_title="Jetson FastAPI Client", layout="centered")
st.title("📤 이미지 업로드 → 📡 서버 추론 → 📥 결과 보기")

# ======================
# 🔹 사이드바 (서버 설정 & 헬스체크)
# ======================
with st.sidebar:
    st.subheader("서버 설정")
    # 서버 URL 입력칸 (기본값은 DEFAULT_SERVER)
    server = st.text_input("서버 URL", value=DEFAULT_SERVER, help="예: http://192.168.219.64:8000")
    
    # 버튼 클릭 시 서버의 /health 엔드포인트 호출
    if st.button("헬스체크"):
        try:
            r = requests.get(f"{server}/health", timeout=10)  # 10초 안에 응답 없으면 실패
            if r.ok:
                st.success(f"연결 성공: {r.json()}")  # JSON 결과 표시 (서버 상태 확인)
            else:
                st.error(f"연결 실패: {r.status_code} {r.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"요청 실패: {e}")

# 현재 사용 중인 서버 주소 표시
st.caption(f"현재 서버: {server}")

# ======================
# 🔹 업로드 UI
# ======================
uploaded = st.file_uploader(
    "이미지 선택 (JPG/PNG, 최대 200MB)",  # 파일 업로드 창
    type=["jpg", "jpeg", "png"],          # 허용 확장자
    accept_multiple_files=False           # 여러 파일 업로드 비활성화
)

# 응답 형태 선택: JSON or 시각화 이미지
mode = st.radio("응답 형태", ["시각화 이미지", "JSON"], horizontal=True)

# ======================
# 🔹 전송 버튼 동작
# ======================
if uploaded and st.button("서버로 전송"):
    # Streamlit의 UploadedFile 객체 → bytes 로 변환
    file_bytes = uploaded.read()
    # requests.post에 전달할 파일 형식 맞추기
    files = {"file": (uploaded.name, io.BytesIO(file_bytes), uploaded.type or "image/jpeg")}

    try:
        if mode == "JSON":
            # 서버의 /predict 엔드포인트 호출 (JSON 응답)
            resp = requests.post(f"{server}/predict", files=files, timeout=60)
            st.write("/predict 상태:", resp.status_code)
            if resp.ok:
                st.json(resp.json())   # JSON 응답 예쁘게 표시
            else:
                st.error(resp.text)

        else:  # 시각화 이미지 모드
            # 서버의 /predict/image 엔드포인트 호출 (이미지 응답)
            resp = requests.post(f"{server}/predict/image", files=files, timeout=60)
            st.write("/predict/image 상태:", resp.status_code)
            if resp.ok:
                img_bytes = resp.content  # 서버에서 받은 이미지 바이트
                st.image(img_bytes, caption="서버 시각화 결과")  # Streamlit에 이미지 출력
                # 다운로드 버튼 제공 (예: prediction.jpg로 저장)
                st.download_button("결과 이미지 다운로드", data=img_bytes, file_name="prediction.jpg")
            else:
                st.error(resp.text)

    except requests.exceptions.RequestException as e:
        # 네트워크 오류 등 예외 처리
        st.error(f"요청 실패: {e}")