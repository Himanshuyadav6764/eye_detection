import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av
import threading
import time

# Streamlit page configuration
st.set_page_config(
    page_title="Eye Detection Alert System",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Global variables
alert_counter = 0
last_alert_time = 0

def eye_aspect_ratio(landmarks, eye_indices):
    """Calculate Eye Aspect Ratio (EAR)"""
    # Get 6 key points for each eye
    p1 = landmarks[eye_indices[0]]  # Left corner
    p2 = landmarks[eye_indices[1]]  # Top-left
    p3 = landmarks[eye_indices[2]]  # Top-right
    p4 = landmarks[eye_indices[3]]  # Right corner
    p5 = landmarks[eye_indices[4]]  # Bottom-right
    p6 = landmarks[eye_indices[5]]  # Bottom-left
    
    # Calculate vertical distances (eye height)
    vertical_1 = abs(p2.y - p6.y)
    vertical_2 = abs(p3.y - p5.y)
    
    # Calculate horizontal distance (eye width)
    horizontal = abs(p1.x - p4.x)
    
    # EAR formula: (vertical_1 + vertical_2) / (2 * horizontal)
    if horizontal == 0:
        return 0
    ear = (vertical_1 + vertical_2) / (2 * horizontal)
    return ear

class EyeDetectionTransformer(VideoTransformerBase):
    def __init__(self):
        self.closed_eye_counter = 0
        self.threshold = 0.22
        self.consecutive_frames = 5
        self.alert_active = False
        
    def transform(self, frame):
        global alert_counter, last_alert_time
        
        img = frame.to_ndarray(format="bgr24")
        
        # Flip frame horizontally for mirror effect
        img = cv2.flip(img, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                
                # Eye landmark indices
                LEFT_EYE = [362, 385, 387, 263, 373, 380]
                RIGHT_EYE = [33, 160, 158, 133, 153, 144]
                
                # Calculate EAR for both eyes
                left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
                right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
                avg_ear = (left_ear + right_ear) / 2
                
                # Display EAR value
                cv2.putText(img, f"EAR: {avg_ear:.3f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Check if eyes are closed
                if avg_ear < self.threshold:
                    self.closed_eye_counter += 1
                    cv2.putText(img, f"Closed frames: {self.closed_eye_counter}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    # Alert after consecutive closed frames
                    if self.closed_eye_counter >= self.consecutive_frames:
                        cv2.putText(img, "ALERT! Eyes Closed", (50, 100),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                        
                        # Trigger alert (increment counter for sidebar display)
                        current_time = time.time()
                        if current_time - last_alert_time > 2:  # Alert every 2 seconds
                            alert_counter += 1
                            last_alert_time = current_time
                            self.alert_active = True
                else:
                    self.closed_eye_counter = 0
                    self.alert_active = False
                    cv2.putText(img, "Eyes Open", (50, 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        # Add threshold info
        cv2.putText(img, f"Threshold: {self.threshold:.2f}", (10, img.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return img

# Streamlit UI
st.title("👁️ Eye Detection Alert System")
st.markdown("**Real-time drowsiness detection using webcam**")

# Sidebar controls
st.sidebar.header("⚙️ Controls")
threshold = st.sidebar.slider("Detection Threshold", 0.15, 0.35, 0.22, 0.01)
consecutive_frames = st.sidebar.slider("Consecutive Frames", 3, 15, 5)

# Info section
st.sidebar.header("📊 Information")
st.sidebar.info(f"Alert Count: {alert_counter}")

# Instructions
st.sidebar.header("📖 Instructions")
st.sidebar.markdown("""
- **Normal EAR**: 0.25-0.35
- **Closed Eyes**: Below threshold
- Adjust threshold if needed
- Good lighting improves accuracy
""")

# Technical info
with st.expander("🔧 Technical Details"):
    st.markdown("""
    **How it works:**
    - Uses MediaPipe face mesh detection
    - Calculates Eye Aspect Ratio (EAR)
    - Triggers alert when EAR drops below threshold
    - Requires consecutive frames for accuracy
    
    **EAR Formula:**
    ```
    EAR = (vertical_1 + vertical_2) / (2 * horizontal)
    ```
    """)

# WebRTC configuration
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# Main video stream
st.header("📹 Live Detection")

# Create two columns
col1, col2 = st.columns([3, 1])

with col1:
    # Video streamer
    ctx = webrtc_streamer(
        key="eye-detection",
        video_transformer_factory=EyeDetectionTransformer,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={
            "video": True,
            "audio": False
        },
        async_processing=True,
    )
    
    # Update transformer settings
    if ctx.video_transformer:
        ctx.video_transformer.threshold = threshold
        ctx.video_transformer.consecutive_frames = consecutive_frames

with col2:
    # Status indicators
    st.subheader("🚨 Status")
    
    if alert_counter > 0:
        st.error(f"⚠️ {alert_counter} Alert(s) Detected!")
    else:
        st.success("✅ No Alerts")
    
    # Real-time metrics (placeholder)
    metrics_placeholder = st.empty()
    
    # Auto-refresh metrics
    if ctx.video_transformer:
        with metrics_placeholder.container():
            st.metric("Threshold", f"{threshold:.2f}")
            st.metric("Required Frames", consecutive_frames)
            if hasattr(ctx.video_transformer, 'alert_active'):
                status = "🔴 Alert!" if ctx.video_transformer.alert_active else "🟢 Normal"
                st.metric("Current Status", status)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    <p>Built with ❤️ using Streamlit and MediaPipe</p>
    <p><a href="https://github.com/Himanshuyadav6764/eye_detection" target="_blank">View on GitHub</a></p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every second for alert counter
if st.button("🔄 Refresh Status"):
    st.rerun()