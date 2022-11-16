# echo_server.py
#-*- coding:utf-8 -*-
import os

import socket
import json
import time

import mediapipe as mp
import cv2
import numpy as np
import matplotlib.pyplot as plt
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

classes = ["person", "bicycle", "car", "motorcycle",
            "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant",
            "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse",
            "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
            "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis",
            "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
            "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife",
            "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog",
            "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table",
            "toilet", "tv", "laptop", "mouse", "remote", "keyboard",
            "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
            "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush" ]


len(classes)

# Yolo load
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))


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
        
#calculate Y diff
def calculate_Y_diff_abs(a, b):
    a = np.array(a)[1]
    b = np.array(b)[1]
    return abs(a-b)

def calculate_Y_diff(a, b):
    a = np.array(a)[1]
    b = np.array(b)[1]
    return (a-b)









#비디오 설정
stage = { "result" : str }
temp = cv2.VideoCapture(0) #카메라

stage['result'] = "Initial stage"
print(dict['result'])
result = json.dumps(stage)






# 루프 진입
while temp.isOpened():
    
    #setup mp
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:          
    
        
        #사진 촬영
        temp_ret, temp_frame = temp.read()
        #사진 저장
        cv2.imwrite("temp.png", temp_frame)
        time.sleep(0.5)
        #저장된 이미지
        img = cv2.imread("temp.png") 
        ret, frame = temp.read()
            
        #recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        #make detection
        results = pose.process(image)
        #recoloring back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
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
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                        
            #calculate (shoulder-hip-knee)
            right_angle = calculate_angle(right_shoulder, right_hip, right_knee)
            left_angle = calculate_angle(left_shoulder, left_hip, left_knee)
            #calculate (hip-knee-ankle)
            right_angle_leg = calculate_angle(right_hip, right_knee, right_ankle)
            left_angle_leg = calculate_angle(left_hip, left_knee, left_ankle)
            
            
            if calculate_Y_diff_abs(right_shoulder, right_hip)<0.05 or calculate_Y_diff_abs(left_shoulder, left_hip)<0.05:
                stage['result'] = "lie"
            else:
                    
                if (right_angle>140 and (left_angle>70 and left_angle<=140)) or (left_angle>140 and (right_angle>70 and right_angle<=140)): 
                    stage['result'] = "sit"
                    
                elif (right_angle>140 and left_angle<75) or (left_angle>140 and right_angle<75): 
                    stage['result'] = "sit"
                    
                elif ((right_angle>70 and right_angle<=140)and(left_angle<=75)) or ((left_angle>70 and left_angle<=140)and(right_angle<=75)): 
                    stage['result'] = "sit"
                                
                elif (right_angle>70 and right_angle<=140) and (left_angle>70 and left_angle<=140): 
                    if calculate_Y_diff(right_knee, right_hip)<=0.1:
                        stage['result'] = "sit"
                    else:
                        stage['result'] = "stand"
                        
                elif right_angle>140 and left_angle>140:
                    stage['result'] = "stand"
                    
                elif right_angle<=100 and left_angle<=100: 
                    if calculate_Y_diff(right_knee, right_hip)<=0.1 or calculate_Y_diff(left_knee, left_hip)<=0.1:
                        stage['result'] = "sit"              
        except:
            pass
        
        #img load
        img = cv2.imread("sample.jpg")
        #img = cv2.resize(img, None, fx=0.4, fy=0.4)
        height, width, channels = img.shape

        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)


        class_in = []
        box = []

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.1, 0.4)

        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                print(f"class_ids: {label} x : {x} y : {y}")
                color = colors[i]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y+30), font, 2, color, 2)
                
        #사진 삭제
        os.remove("temp.png")
            
    print(stage['result'])
            

    time.sleep(0.5)
    
#client_socket.close()  # 클라이언트 소켓 종료
    
    