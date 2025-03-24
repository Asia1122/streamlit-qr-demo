import streamlit as st
import av
import cv2
import time
from pyzbar import pyzbar
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase

class QRVideoProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        super().__init__()
        self.last_qr_data = None
        self.last_detected_time = 0.0
        self.detect_threshold = 3.0  # 3초 유지 시 동작

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        decoded_objs = pyzbar.decode(img)
        current_time = time.time()

        found_qr_data = None
        for obj in decoded_objs:
            (x, y, w, h) = obj.rect
            # 초록색 박스
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            qr_data = obj.data.decode("utf-8")
            # 박스 위에 텍스트 표시
            cv2.putText(img, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2)
            found_qr_data = qr_data

        if found_qr_data:
            if self.last_qr_data == found_qr_data:
                # 같은 QR이 계속 감지되는 중
                elapsed = current_time - self.last_detected_time
                if elapsed >= self.detect_threshold:
                    # 3초 이상 유지 -> 세션 상태에 기록
                    st.session_state["qr_detected"] = found_qr_data
            else:
                # 새 QR 인식 -> 시간 리셋
                self.last_qr_data = found_qr_data
                self.last_detected_time = current_time
        else:
            # QR이 안 보이면 리셋
            self.last_qr_data = None
            self.last_detected_time = 0.0

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("QR 코드 인식 데모")
    if "qr_detected" not in st.session_state:
        st.session_state["qr_detected"] = None

    webrtc_ctx = webrtc_streamer(
        key="qr-scanner",
        mode=WebRtcMode.LIVE,
        video_processor_factory=QRVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )

    if st.session_state["qr_detected"]:
        st.success(f"인식된 QR코드: {st.session_state['qr_detected']}")
        st.write("3초 이상 동일 QR코드가 감지되었습니다!")
        # 원하면 아래에 특정 동작(링크 이동 등) 추가
        # e.g. st.markdown(f"[이동하기]({st.session_state['qr_detected']})")

if __name__ == "__main__":
    main()
