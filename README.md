# Eye Detection Alert System

A real-time eye detection system that alerts users when their eyes are closed for too long. Perfect for driver drowsiness detection, preventing fatigue during work, or maintaining alertness during important tasks.

## Features

- **Real-time Eye Detection**: Uses MediaPipe for accurate eye tracking
- **Voice Alerts**: Clear text-to-speech warnings when eyes are closed
- **Adjustable Sensitivity**: Real-time threshold adjustment with +/- keys
- **Mirror View**: Flipped camera feed for natural interaction
- **Visual Feedback**: Shows EAR (Eye Aspect Ratio) values and frame counts
- **Fallback Audio**: Enhanced beep patterns if voice synthesis fails

## Requirements

- Python 3.10 (MediaPipe compatibility requirement)
- Webcam
- Windows OS (for voice alerts)

## Installation

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

## Usage

1. **Run the application**:

   ```bash
   .\venv\Scripts\python.exe eye.py
   ```

2. **Controls**:

   - Press `T` to test voice alerts
   - Press `+` or `=` to increase sensitivity threshold
   - Press `-` to decrease sensitivity threshold
   - Press `ESC` to exit

3. **Calibration**:
   - Watch the EAR values displayed on screen
   - Normal open eyes: 0.25-0.35
   - Closed eyes: below 0.22
   - Adjust threshold using +/- keys for optimal detection

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
