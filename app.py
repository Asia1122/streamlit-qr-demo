import streamlit as st
import av
import cv2
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase

class QRVideoProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        super().__init__()
        self.detector = cv2.QRCodeDetector()
        self.last_qr_data = None
        self.last_detected_time = 0.0
        self.detect_threshold = 3.0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # 1) OpenCV QR 디텍터로 인식
        data, points, _ = self.detector.detectAndDecode(img)

        if points is not None:
            # points는 QR코드 꼭짓점 좌표. 사각형 그려주기
            pts = points[0].astype(int)  # float -> int 변환
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)

        current_time = time.time()
        if data:  # QR코드 인식 성공 (data != "")
            if self.last_qr_data == data:
                # 같은 데이터가 연속 감지될 경우 시간 체크
                elapsed = current_time - self.last_detected_time
                if elapsed >= self.detect_threshold:
                    st.session_state["qr_detected"] = data
            else:
                # 새 QR코드 인식
                self.last_qr_data = data
                self.last_detected_time = current_time
        else:
            # 인식되지 않으면 리셋
            self.last_qr_data = None
            self.last_detected_time = 0.0

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("QR 코드 인식 (OpenCV 내장)")

    if "qr_detected" not in st.session_state:
        st.session_state["qr_detected"] = None

    webrtc_streamer(
        key="qr-scanner",
        mode=WebRtcMode.LIVE,
        video_processor_factory=QRVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )

    if st.session_state["qr_detected"]:
        st.success(f"인식된 QR코드: {st.session_state['qr_detected']}")
        st.write("3초 이상 유지되었습니다!")

if __name__ == "__main__":
    main()
