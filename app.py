import streamlit as st
import av
import cv2
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase

class QRVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        self.last_qr_data = None
        self.last_detected_time = 0.0
        self.detect_threshold = 3.0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # 1) OpenCV QR 디텍터
        data, points, _ = self.detector.detectAndDecode(img)

        # 2) 인식 성공하면 `data`가 ""가 아닌 문자열이 됨
        if points is not None:
            pts = points[0].astype(int)
            # 초록색 박스로 QR 영역 표시
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)

        current_time = time.time()
        if data:
            # data != "" 이면 QR코드가 인식된 것
            if self.last_qr_data == data:
                # 3초 유지 체크
                elapsed = current_time - self.last_detected_time
                if elapsed >= self.detect_threshold:
                    st.session_state["qr_detected"] = data
            else:
                # 새로 인식된 QR
                self.last_qr_data = data
                self.last_detected_time = current_time
        else:
            # 인식 안 되면 리셋
            self.last_qr_data = None
            self.last_detected_time = 0.0

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("QR 코드 인식 테스트 (OpenCV)")

    if "qr_detected" not in st.session_state:
        st.session_state["qr_detected"] = None

    webrtc_streamer(
        key="qr-scanner",
        mode=WebRtcMode.SENDRECV,  # LIVE가 없으면 SENDRECV 사용
        video_processor_factory=QRVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )

    if st.session_state["qr_detected"]:
        st.success(f"인식된 QR코드: {st.session_state['qr_detected']}")
        st.write("3초 이상 동일 QR코드가 유지되었습니다!")

if __name__ == "__main__":
    main()
