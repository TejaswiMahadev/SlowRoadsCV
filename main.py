import cv2
import mediapipe as mp
import numpy as np
from pynput.keyboard import Key, Controller
import time


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(
    model_complexity=0,  
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=1) 


keyboard = Controller()


cap = cv2.VideoCapture(0)


is_accelerating = False
is_braking = False
is_turning_left = False
is_turning_right = False


def is_hand_open(hand_landmarks):
    """Check if hand is open (all fingers extended)"""
    finger_tips = [8, 12, 16, 20]  
    mcp_joints = [5, 9, 13, 17]    
    
    extended_fingers = 0
    for tip, mcp in zip(finger_tips, mcp_joints):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[mcp].y:
            extended_fingers += 1
    
    if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
        extended_fingers += 1
        
    return extended_fingers >= 4

def is_thumbs_up(hand_landmarks):
    """Check if hand is making thumbs up gesture (brake)"""
    is_thumb_up = (hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y and
                   hand_landmarks.landmark[3].y < hand_landmarks.landmark[2].y)
    finger_tips = [8, 12, 16, 20]  
    middle_joints = [6, 10, 14, 18]  
    
    curled_fingers = 0
    for tip, mid in zip(finger_tips, middle_joints):
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[mid].y:
            curled_fingers += 1
    
    return is_thumb_up and curled_fingers >= 3

def is_pointing_left(hand_landmarks):
    """Check if index finger is pointing left"""
    is_index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[5].y
    other_finger_tips = [12, 16, 20]  
    other_finger_mcp = [9, 13, 17]   
    
    curled_count = 0
    for tip, mcp in zip(other_finger_tips, other_finger_mcp):
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[mcp].y:
            curled_count += 1
    is_pointing_left = hand_landmarks.landmark[8].x < hand_landmarks.landmark[5].x
    
    return is_index_extended and curled_count >= 2 and is_pointing_left

def is_pointing_right(hand_landmarks):
    """Check if index finger is pointing right"""
    is_index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[5].y
    other_finger_tips = [12, 16, 20]
    other_finger_mcp = [9, 13, 17]   
    
    curled_count = 0
    for tip, mcp in zip(other_finger_tips, other_finger_mcp):
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[mcp].y:
            curled_count += 1
    is_pointing_right = hand_landmarks.landmark[8].x > hand_landmarks.landmark[5].x
    
    return is_index_extended and curled_count >= 2 and is_pointing_right

def apply_control(gesture):
    """Apply keyboard controls based on detected gesture"""
    global is_accelerating, is_braking, is_turning_left, is_turning_right
    if gesture == "open" and not is_accelerating:
        keyboard.press('w')
        is_accelerating = True
    elif gesture != "open" and is_accelerating:
        keyboard.release('w')
        is_accelerating = False
    if gesture == "thumbs_up" and not is_braking:
        keyboard.press('s')
        is_braking = True
    elif gesture != "thumbs_up" and is_braking:
        keyboard.release('s')
        is_braking = False
    if gesture == "pointing_left" and not is_turning_left:
        keyboard.press('a')
        is_turning_left = True
    elif gesture != "pointing_left" and is_turning_left:
        keyboard.release('a')
        is_turning_left = False
    if gesture == "pointing_right" and not is_turning_right:
        keyboard.press('d')
        is_turning_right = True
    elif gesture != "pointing_right" and is_turning_right:
        keyboard.release('d')
        is_turning_right = False

def main():
    global is_accelerating, is_braking, is_turning_left, is_turning_right
    
    prev_time = 0
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        
        cv2.putText(image, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        controls_text = ""
        if is_accelerating:
            controls_text += "Accelerating (W) "
        if is_braking:
            controls_text += "Reverse (S) "
        if is_turning_left:
            controls_text += "Turning Left (A) "
        if is_turning_right:
            controls_text += "Turning Right (D) "
        
        if controls_text:
            cv2.putText(image, controls_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                gesture = None
                if is_hand_open(hand_landmarks):
                    gesture = "open"
                    cv2.putText(image, "Open Hand: Accelerate", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                elif is_thumbs_up(hand_landmarks):
                    gesture = "thumbs_up"
                    cv2.putText(image, "Thumbs Up: Brake", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                elif is_pointing_left(hand_landmarks):
                    gesture = "pointing_left"
                    cv2.putText(image, "Pointing Left: Turn Left", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                elif is_pointing_right(hand_landmarks):
                    gesture = "pointing_right"
                    cv2.putText(image, "Pointing Right: Turn Right", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                if gesture:
                    apply_control(gesture)
        else:
            if is_accelerating:
                keyboard.release('w')
                is_accelerating = False
            if is_braking:
                keyboard.release('s')
                is_braking = False
            if is_turning_left:
                keyboard.release('a')
                is_turning_left = False
            if is_turning_right:
                keyboard.release('d')
                is_turning_right = False
        cv2.imshow('Hand Gesture Controller for Slow Roads', image)
        if cv2.waitKey(5) & 0xFF == 27:  
            break
    cap.release()
    cv2.destroyAllWindows()
    for key in ['w', 's', 'a', 'd']:
        keyboard.release(key)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        for key in ['w', 's', 'a', 'd']:
            keyboard.release(key)