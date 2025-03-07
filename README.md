# Hand Gesture Controller for Slow Roads

## Overview

This project uses a webcam and the Mediapipe library to recognize hand gestures and control vehicle movement in driving simulations. The program detects specific hand gestures and maps them to keyboard inputs, allowing gesture-based control of acceleration, braking, and turning.

# Features

- Accelerate: Open hand gesture
  
- Brake: V Sign 
  
- Turn Left: Index finger pointing left
  
- Turn Right: Index finger pointing right

- Reverse - Fist 
  
- Displays real-time FPS and control status on the screen
  
- Uses pynput to simulate keyboard presses

# How It Works

- **Hand Detection**: Uses Mediapipe's Hand Tracking module to detect hands in the webcam feed.

- **Gesture Recognition**: Identifies specific hand gestures:

- **Open hand** → Accelerate (W key)

- **Thumbs up** → Brake (S key)

- ** Index finger left **→ Turn left (A key)

-  **Index finger right** → Turn right (D key)

- ** Keyboard Control** : Sends corresponding keypresses using pynput to simulate driving controls.

- ** Real-time Display** : Shows FPS and active controls on the screen using OpenCV.
