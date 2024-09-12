import cv2
import mediapipe as mp
import time
from directkeys import right_pressed, left_pressed, PressKey, ReleaseKey

# Key mappings
break_key_pressed = left_pressed
accelerato_key_pressed = right_pressed

# Delay to set up
time.sleep(2.0)
current_key_pressed = set()

# Initialize MediaPipe hands module
mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

# Finger tip IDs for checking if fingers are up
tipIds = [4, 8, 12, 16, 20]

# Capture video from the webcam
video = cv2.VideoCapture(0)

# Start the hand detection process
with mp_hand.Hands(min_detection_confidence=0.5, max_num_hands=1) as hands:
    
    while True:
        ret, image = video.read()
        keyPressed = False
        break_pressed=False
        accelerator_pressed=False
        key_count=0
        key_pressed=0

        # Convert the image to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        lmList = []
        if results.multi_hand_landmarks:
            for hand_landmark in results.multi_hand_landmarks:
                myHands = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHands.landmark):
                    h, w, c = image.shape
                    cx = int(lm.x * w)
                    cy = int(lm.y * h)
                    lmList.append([id, cx, cy])
                    
                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)

        # Check which fingers are up
        fingers = []
        if lmList:
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:  # Thumb
                fingers.append(1)
            else:
                fingers.append(0)

            for id in range(1, 5):  # Other fingers
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            total = fingers.count(1)

            # Check if brake or gas
            if total == 0:
                # Brake
                cv2.rectangle(image, (20, 300), (270, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(image, "BRAKE", (45, 375), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 0, 0), 5)
                PressKey(break_key_pressed)
                break_pressed=True
                current_key_pressed.add(break_key_pressed)
                key_pressed=break_key_pressed
                keyPressed = True
                key_count=key_count+1

            elif total == 5 :
                # Gas
                cv2.rectangle(image, (20, 300), (270, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(image, "  GAS", (45, 375), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 0, 0), 5)
                PressKey(accelerato_key_pressed)
                key_pressed=accelerato_key_pressed
                accelerator_pressed=True
                keyPressed = True
                current_key_pressed.add(accelerato_key_pressed)
                key_count=key_count+1

        if not keyPressed and len(current_key_pressed) != 0:
            for key in current_key_pressed:
                ReleaseKey(key)
            current_key_pressed = set()
        elif key_count==1 and len(current_key_pressed)==2:    
            for key in current_key_pressed:             
                if key_pressed!=key:
                    ReleaseKey(key)
            current_key_pressed = set()
            for key in current_key_pressed:
                ReleaseKey(key)
            current_key_pressed = set()

        # Show the frame
        cv2.imshow("Frame", image)

        # Quit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
video.release()
cv2.destroyAllWindows()
