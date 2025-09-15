# Eye Detection Alert System

A real-time eye detection system that alerts users when their eyes are closed for too long. Perfect for driver drowsiness detection, preventing fatigue during work, or maintaining alertness during important tasks.

## 🌐 Live Demo

Try the web version: [Eye Detection Web App](https://eye-detection-app.streamlit.app) _(Will be available after deployment)_

## 📱 Two Versions Available

### 1. **Desktop Version** (`eye.py`)

- Full-featured with voice alerts
- Windows-specific TTS support
- Real-time threshold adjustment
- Enhanced beep fallbacks

### 2. **Web Version** (`app.py`)

- Browser-based using Streamlit
- Works on any device with webcam
- Real-time detection in web browser
- Cross-platform compatible

## Features

- **Real-time Eye Detection**: Uses MediaPipe for accurate eye tracking
- **Voice Alerts**: Clear text-to-speech warnings when eyes are closed (desktop version)
- **Visual Alerts**: On-screen notifications for all versions
- **Adjustable Sensitivity**: Real-time threshold adjustment
- **Mirror View**: Flipped camera feed for natural interaction
- **Visual Feedback**: Shows EAR (Eye Aspect Ratio) values and frame counts
- **Cross-platform**: Desktop version for Windows, web version for all platforms

## Installation & Usage

### 🖥️ Desktop Version (Windows)

1. **Install Python 3.10**:

   ```bash
   winget install Python.Python.3.10
   ```

2. **Clone the repository**:

   ```bash
   git clone https://github.com/Himanshuyadav6764/eye_detection.git
   cd eye_detection
   ```

3. **Create virtual environment**:

   ```bash
   py -3.10 -m venv venv
   .\venv\Scripts\activate
   ```

4. **Install dependencies**:

   ```bash
   pip install mediapipe opencv-python pywin32
   ```

5. **Run the desktop application**:
   ```bash
   python eye.py
   ```

### 🌐 Web Version (Any Platform)

1. **Clone and setup**:

   ```bash
   git clone https://github.com/Himanshuyadav6764/eye_detection.git
   cd eye_detection
   pip install -r requirements.txt
   ```

2. **Run the web application**:

   ```bash
   streamlit run app.py
   ```

3. **Access in browser**: Open `http://localhost:8501`

### ☁️ Deploy to Streamlit Cloud

1. Fork this repository on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository and `app.py`
5. Click "Deploy"

## Controls

### Desktop Version (`eye.py`)

- Press `T` to test voice alerts
- Press `+` or `=` to increase sensitivity threshold
- Press `-` to decrease sensitivity threshold
- Press `ESC` to exit

### Web Version (`app.py`)

- Use sidebar sliders to adjust threshold and frame requirements
- Real-time status updates
- Cross-platform webcam access

## Calibration

- Watch the EAR values displayed on screen
- Normal open eyes: 0.25-0.35
- Closed eyes: below 0.22
- Adjust threshold using controls for optimal detection

## How It Works

The system uses MediaPipe's face mesh detection to track eye landmarks and calculate the Eye Aspect Ratio (EAR). When the EAR drops below the threshold for 5 consecutive frames, it triggers a voice alert.

### Eye Aspect Ratio Formula

```
EAR = (vertical_1 + vertical_2) / (2 * horizontal)
```

Where:

- `vertical_1`, `vertical_2`: Vertical distances between eye landmarks
- `horizontal`: Horizontal distance between eye corners

## Technical Details

- **Framework**: OpenCV, MediaPipe
- **TTS Engine**: Windows SAPI (win32com.client)
- **Detection Method**: Eye Aspect Ratio calculation
- **Alert Threshold**: 0.22 (adjustable)
- **Frame Requirement**: 5 consecutive frames
- **Python Version**: 3.10 (required for MediaPipe)

## Troubleshooting

1. **"ModuleNotFoundError: No module named 'mediapipe'"**:

   - Ensure you're using Python 3.10
   - MediaPipe doesn't support Python 3.11+

2. **Voice not working**:

   - Press `T` to test voice functionality
   - Fallback beep sounds will play if TTS fails

3. **False alerts when eyes are open**:

   - Press `+` to increase threshold
   - Watch EAR values and adjust accordingly

4. **Not detecting when eyes are closed**:
   - Press `-` to decrease threshold
   - Ensure good lighting conditions

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).
