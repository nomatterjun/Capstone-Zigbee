import mediapipe as mp
import cv2 as cv
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

stage = None

#video feed
cap = cv.VideoCapture(0)

#calculate angles
def calculate_angle(a, b, c):
            a = np.array(a)
            b = np.array(b)
            c = np.array(c)
            
            radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
            angle = np.abs(radians*180.0/np.pi)
            
            if angle > 180.0:
                angle = 360-angle
                
            return angle
        

#setup mp
with mp_pose.Pose(min_detection_confidence=0.5, 
                  min_tracking_confidence=0.5) as pose:          
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        #recolor image to RGB
        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        image.flags.writeable = False
        #make detection
        results = pose.process(image)
        #recoloring back to BGR
        image.flags.writeable = True
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        
        #extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            
            #calculate
            right_angle = calculate_angle(right_shoulder, right_hip, right_knee)
            left_angle = calculate_angle(left_shoulder, left_hip, left_knee)
            
            
            
            # Visualize angle
            cv.putText(image, str(right_angle), 
                           tuple(np.multiply(right_hip, [640, 480]).astype(int)), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA
                                )
            # Visualize angle
            cv.putText(image, str(left_angle), 
                           tuple(np.multiply(left_hip, [640, 480]).astype(int)), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA
                                )
            
            #sit logic
            if right_angle>=60 and right_angle<=140:
                stage = "sit"
            elif left_angle>=60 and left_angle<=140:
                stage = "sit"
            else:
                stage = "not sit"
            
        except:
            pass
                
        #setup status box 
        cv.rectangle(image, (0,0), (225, 73), (245, 117, 16), -1)
        
        #rep data
        cv.putText(image, 'STAGE', (15, 12),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv.LINE_AA)
        cv.putText(image, str(stage),
                   (10,60),
                   cv.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv.LINE_AA)
        
        #render detections
        mp_drawing.draw_landmarks(image,
                                results.pose_landmarks,
                                mp_pose.POSE_CONNECTIONS)

                
        
        cv.imshow('Mediapipe Feed', image)
        
        if cv.waitKey(10) & 0xFF == ord('q'):
            break
        
        
    cap.release()
    cv.destroyAllWindows()
