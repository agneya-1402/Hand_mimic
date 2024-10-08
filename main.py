import cv2
import mediapipe as mp
import serial
import math


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)


cap = cv2.VideoCapture(1)


ser = serial.Serial('/dev/tty.usbmodem1101', 9600, timeout=1)

# Landmark indices
thumb_tip = 4
thumb_ip = 3
thumb_mcp = 2
index_mcp = 5
fingertips = [thumb_tip, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky

def calculate_angle(a, b, c):
    angle = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return angle + 360 if angle < 0 else angle

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
    
    finger_states = ['0'] * 5  # closed position

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
            
            # bounding box 
            x_coords = [landmark.x for landmark in hand_landmarks.landmark]
            y_coords = [landmark.y for landmark in hand_landmarks.landmark]
            bbox_min_x, bbox_max_x = min(x_coords), max(x_coords)
            bbox_min_y, bbox_max_y = min(y_coords), max(y_coords)
            
            # Thumb angle 
            angle = calculate_angle(hand_landmarks.landmark[thumb_tip],
                                    hand_landmarks.landmark[thumb_ip],
                                    hand_landmarks.landmark[index_mcp])
            
            # Thumb open
            if angle > 30:
                finger_states[0] = '1'  
            
            # other fingers
            for i in range(1, 5):
                tip = hand_landmarks.landmark[fingertips[i]]
                pip = hand_landmarks.landmark[fingertips[i] - 2]
                
                # Finger open, if tip is above the pip
                if tip.y < pip.y:
                    finger_states[i] = '1'  
            
            # Send to arduino
            ser.write(''.join(finger_states).encode())
            
            # bounding box
            h, w, c = image.shape
            cv2.rectangle(image, 
                          (int(bbox_min_x * w), int(bbox_min_y * h)), 
                          (int(bbox_max_x * w), int(bbox_max_y * h)), 
                          (0, 255, 0), 2)
    
    # Flip img
    image = cv2.flip(image, 1)
    
    for i, state in enumerate(finger_states):
        cv2.putText(image, f"Finger {i}: {'Open' if state == '1' else 'Closed'}", 
                    (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Hand Mimic Bot', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
ser.close()