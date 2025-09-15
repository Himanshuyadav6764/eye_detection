import cv2
import mediapipe as mp
import winsound  # Using reliable Windows sound API
import os
import subprocess  # For alternative TTS

# Simple and reliable alert function
def speak_alert(message):
    """Function to create audio alert"""
    try:
        # Try to use Windows SAPI via com objects (most reliable)
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(message)
    except ImportError:
        try:
            # Fallback: Enhanced beep pattern for "Wake up" alert
            # Three ascending beeps
            winsound.Beep(800, 150)   # Low beep
            winsound.Beep(1000, 150)  # Medium beep  
            winsound.Beep(1200, 300)  # High beep (longer)
            print(f"Audio Alert: {message}")
        except:
            print(f"Alert: {message}")

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Webcam capture
cap = cv2.VideoCapture(0)

# Function to calculate Eye Aspect Ratio (EAR) - Improved version
def eye_aspect_ratio(landmarks, eye_indices):
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

# Variables for drowsiness detection
CLOSED_EYE_THRESHOLD = 0.22  # Increased threshold for better detection
CONSECUTIVE_FRAMES = 5  # Reduced frames needed for quicker response
closed_eye_counter = 0
last_alert_frame = 0  # Track when last alert was given

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark

            # More accurate Mediapipe eye landmark indices
            LEFT_EYE = [362, 385, 387, 263, 373, 380]   # Left eye landmarks
            RIGHT_EYE = [33, 160, 158, 133, 153, 144]   # Right eye landmarks

            # Calculate EAR for both eyes
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
            avg_ear = (left_ear + right_ear) / 2

            # Display EAR values for debugging
            cv2.putText(frame, f"EAR: {avg_ear:.3f}", (300, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Check if eyes are closed
            if avg_ear < CLOSED_EYE_THRESHOLD:
                closed_eye_counter += 1
                cv2.putText(frame, f"Closed frames: {closed_eye_counter}", (300, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Alert after consecutive closed frames
                if closed_eye_counter >= CONSECUTIVE_FRAMES:
                    cv2.putText(frame, "ALERT! Eyes Closed", (50,100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
                    
                    # Give voice alert immediately when threshold is reached, then every 20 frames
                    if closed_eye_counter == CONSECUTIVE_FRAMES or (closed_eye_counter - CONSECUTIVE_FRAMES) % 20 == 0:
                        speak_alert("Wake up! Your eyes are closed!")
                        last_alert_frame = closed_eye_counter
                        print(f"Alert! EAR: {avg_ear:.3f}, Frames: {closed_eye_counter}")
            else:
                if closed_eye_counter > 0:
                    print(f"Eyes opened. Was closed for {closed_eye_counter} frames")
                closed_eye_counter = 0  # Reset counter when eyes are open
                cv2.putText(frame, "Eyes Open", (50,100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)

    cv2.imshow("Eye Detection Alert System", frame)
    
    # Add instructions (only show for first few seconds)
    cv2.putText(frame, "Instructions:", (10, frame.shape[0] - 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, "Watch EAR value - adjust threshold if needed", (10, frame.shape[0] - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, f"Current threshold: {CLOSED_EYE_THRESHOLD:.2f}", (10, frame.shape[0] - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, "Press +/- to adjust, T to test voice, ESC to exit", (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Keyboard controls for threshold adjustment
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC key to exit
        break
    elif key == ord('+') or key == ord('='):  # Increase threshold
        CLOSED_EYE_THRESHOLD += 0.01
        print(f"Threshold increased to: {CLOSED_EYE_THRESHOLD:.2f}")
    elif key == ord('-'):  # Decrease threshold
        CLOSED_EYE_THRESHOLD -= 0.01
        if CLOSED_EYE_THRESHOLD < 0.1:
            CLOSED_EYE_THRESHOLD = 0.1
        print(f"Threshold decreased to: {CLOSED_EYE_THRESHOLD:.2f}")
    elif key == ord('t') or key == ord('T'):  # Test voice
        print("Testing voice alert...")
        speak_alert("Voice test - Wake up! This is working!")
        print("Voice test completed")

cap.release()
cv2.destroyAllWindows()
