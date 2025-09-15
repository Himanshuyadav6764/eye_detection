import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
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

class EyeDetectionProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.closed_eye_counter = 0
        self.last_alert_time = 0
        self.threshold = 0.22
        self.consecutive_frames = 5
        self.alert_active = False

    def eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio (EAR) with improved accuracy"""
        try:
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
        except:
            return 0.3  # Default open eye value

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Flip for mirror effect
        img = cv2.flip(img, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.face_mesh.process(rgb_img)
        
        # Initialize alert status
        current_alert = False
        ear_value = 0.0
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                
                # Eye landmark indices
                LEFT_EYE = [362, 385, 387, 263, 373, 380]
                RIGHT_EYE = [33, 160, 158, 133, 153, 144]
                
                # Calculate EAR for both eyes
                left_ear = self.eye_aspect_ratio(landmarks, LEFT_EYE)
                right_ear = self.eye_aspect_ratio(landmarks, RIGHT_EYE)
                avg_ear = (left_ear + right_ear) / 2
                ear_value = avg_ear
                
                # Check if eyes are closed
                if avg_ear < self.threshold:
                    self.closed_eye_counter += 1
                    if self.closed_eye_counter >= self.consecutive_frames:
                        current_time = time.time()
                        if current_time - self.last_alert_time > 2:  # Prevent spam
                            current_alert = True
                            self.alert_active = True
                            self.last_alert_time = current_time
                else:
                    self.closed_eye_counter = 0
                    self.alert_active = False
                
                # Draw status on frame
                status_color = (0, 0, 255) if current_alert else (0, 255, 0)
                status_text = "ALERT! Eyes Closed" if current_alert else "Eyes Open"
                
                cv2.putText(img, status_text, (30, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
                
                # Display EAR value
                cv2.putText(img, f"EAR: {avg_ear:.3f}", (30, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display frame counter
                cv2.putText(img, f"Frames: {self.closed_eye_counter}", (30, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Display threshold
                cv2.putText(img, f"Threshold: {self.threshold:.2f}", (30, 130), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Store alert status for JavaScript access
        if current_alert and hasattr(st, 'session_state'):
            st.session_state['alert_triggered'] = True
            st.session_state['ear_value'] = ear_value
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Simple RTC Configuration
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

def main():
    # Title and description
    st.title("👁️ Eye Detection Alert System")
    st.markdown("**Real-time drowsiness detection with enhanced camera support**")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Settings")
    
    # Initialize session state
    if 'alert_triggered' not in st.session_state:
        st.session_state['alert_triggered'] = False
    if 'ear_value' not in st.session_state:
        st.session_state['ear_value'] = 0.0
    
    # Threshold control
    threshold = st.sidebar.slider(
        "Detection Threshold", 
        min_value=0.15, 
        max_value=0.35, 
        value=0.22, 
        step=0.01,
        help="Lower values = more sensitive"
    )
    
    # Frame requirement control
    consecutive_frames = st.sidebar.slider(
        "Consecutive Frames Required", 
        min_value=3, 
        max_value=15, 
        value=5,
        help="Number of consecutive frames before alert"
    )
    
    # Audio settings
    st.sidebar.subheader("🔊 Audio Settings")
    enable_sound = st.sidebar.checkbox("Enable Sound Alerts", value=True)
    enable_speech = st.sidebar.checkbox("Enable Voice Alerts", value=True)
    
    # Instructions
    st.sidebar.subheader("📋 Instructions")
    st.sidebar.markdown("""
    1. **Click "START" button** to begin camera
    2. **Allow camera access** when prompted
    3. **Position your face** in the camera view
    4. **Watch the EAR value** - normal is 0.25-0.35
    5. **Adjust threshold** if needed using the slider
    6. **Close your eyes** to test the alert system
    """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Camera Feed")
        
        # Create processor instance
        processor = EyeDetectionProcessor()
        processor.threshold = threshold
        processor.consecutive_frames = consecutive_frames
        
        # Video stream with fixed settings
        webrtc_ctx = webrtc_streamer(
            key="eye-detection-stream",
            video_processor_factory=lambda: processor,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={
                "video": {
                    "width": 640,
                    "height": 480,
                    "frameRate": 30
                },
                "audio": False
            },
            async_processing=False
        )
        
        # Camera status
        if webrtc_ctx.state.playing:
            st.success("📹 Camera is active")
        else:
            st.info("👆 Click START to activate camera")
    
    with col2:
        # Status panel
        st.subheader("📊 Status")
        
        # Current EAR value
        if 'ear_value' in st.session_state:
            ear_val = st.session_state['ear_value']
            if ear_val > 0:
                st.metric("Eye Aspect Ratio", f"{ear_val:.3f}")
            else:
                st.metric("Eye Aspect Ratio", "Detecting...")
        
        # Alert status
        if st.session_state.get('alert_triggered', False):
            st.error("🚨 DROWSINESS DETECTED!")
        else:
            st.success("✅ Eyes Open")
        
        # Current settings display
        st.info(f"""
        **Current Settings:**
        - Threshold: {threshold:.2f}
        - Frames Required: {consecutive_frames}
        - Sound Alerts: {'On' if enable_sound else 'Off'}
        - Voice Alerts: {'On' if enable_speech else 'Off'}
        """)
        
        # Test button
        if st.button("🔊 Test Audio"):
            st.session_state['alert_triggered'] = True
    
    # Enhanced JavaScript for audio alerts
    if st.session_state.get('alert_triggered', False) and enable_sound:
        alert_js = f"""
        <script>
        function playEnhancedAlert() {{
            try {{
                // Audio Context for beeps
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                
                function createBeep(frequency, duration, delay = 0) {{
                    setTimeout(() => {{
                        const oscillator = audioContext.createOscillator();
                        const gainNode = audioContext.createGain();
                        
                        oscillator.connect(gainNode);
                        gainNode.connect(audioContext.destination);
                        
                        oscillator.frequency.value = frequency;
                        oscillator.type = 'sine';
                        
                        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
                        
                        oscillator.start(audioContext.currentTime);
                        oscillator.stop(audioContext.currentTime + duration);
                    }}, delay);
                }}
                
                // Play alert sequence
                createBeep(800, 0.2, 0);
                createBeep(1000, 0.2, 200);
                createBeep(1200, 0.4, 400);
                
                // Speech synthesis
                if ({str(enable_speech).lower()} && 'speechSynthesis' in window) {{
                    setTimeout(() => {{
                        speechSynthesis.cancel();
                        const utterance = new SpeechSynthesisUtterance('Wake up! Your eyes are closed!');
                        utterance.rate = 1.0;
                        utterance.volume = 0.8;
                        speechSynthesis.speak(utterance);
                    }}, 600);
                }}
            }} catch (error) {{
                console.log('Audio not available:', error);
            }}
        }}
        
        // Play alert
        playEnhancedAlert();
        </script>
        """
        st.components.v1.html(alert_js, height=0)
        
        # Reset alert state
        st.session_state['alert_triggered'] = False
    
    # Troubleshooting section
    st.markdown("---")
    st.subheader("🔧 Troubleshooting")
    
    with st.expander("Camera not working?"):
        st.markdown("""
        1. **Refresh the page** and try again
        2. **Check browser permissions** - allow camera access
        3. **Try a different browser** (Chrome/Firefox recommended)
        4. **Close other apps** that might be using the camera
        5. **Use HTTPS** - some browsers require secure connection for camera
        """)
    
    with st.expander("Audio not working?"):
        st.markdown("""
        1. **Check browser audio permissions**
        2. **Unmute your browser tab**
        3. **Try the 'Test Audio' button**
        4. **Use Chrome/Firefox** for best compatibility
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **💡 For best performance:**
    - Use Chrome or Firefox browser
    - Ensure good lighting
    - Keep face centered in camera view
    - Adjust threshold based on your eye characteristics
    
    **🚀 Want the desktop version?** 
    [Download from GitHub](https://github.com/Himanshuyadav6764/eye_detection)
    """)

if __name__ == "__main__":
    main()