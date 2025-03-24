import streamlit as st
import av
import cv2
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase

class QRVideoProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        super().__init__()
        self.last_qr_data = None
        self.last_detected_time = 0.0
        self.detect_threshold = 3.0

    def recv(self, frame):
        # QR코드 인식 로직 (OpenCV or Pyzbar)...
        # 생략하고 바운딩박스 및 st.session_state 처리만 간단히 예시
        img = frame.to_ndarray(format="bgr24")
        # QR 인식 및 처리 로직 ...
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("QR 코드 인식 (SENDRECV 모드)")

    if "qr_detected" not in st.session_state:
        st.session_state["qr_detected"] = None

    webrtc_ctx = webrtc_streamer(
        key="qr-scanner",
        # 원래 mode=WebRtcMode.LIVE 였던 부분을 SENDRECV로 교체
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=QRVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )

    if st.session_state["qr_detected"]:
        st.success(f"인식된 QR코드: {st.session_state['qr_detected']}")
        st.write("3초 이상 동일 QR코드가 감지되었습니다!")

if __name__ == "__main__":
    main()
