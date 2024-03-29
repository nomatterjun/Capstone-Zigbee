# echo_server.py
#-*- coding:utf-8 -*-
import os

import socket
import json
import time

import mediapipe as mp
import cv2
import numpy as np
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

#상황별 필요 객체 목록
meal_con = ["bottle", "wine glass", "cup", "fork", "knife",
            "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog",
            "pizza", "donut", "cake"]
media_con = ["remote","tv","cell phone","couch","bed"]
work_con = ["book","keyboard", "laptop"]

#결과 송출 부분
meal_check = 0
score_con = 0
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






# 통신 정보 설정
IP = '10.92.11.31'
PORT = 8080
SIZE = 1024
ADDR = (IP, PORT)







#비디오 설정
stage = {
    "CurrentMoment" : "test currnet",
    "UpcomingMoment": "test upcoming"
}
temp = cv2.VideoCapture(0) #카메라
result = json.dumps(stage)
stage['CurrentMoment'] = "Initial"
motion = "initial"







# 서버 소켓 설정
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind(ADDR)  # 주소 바인딩
    server_socket.listen()  # 클라이언트의 요청을 받을 준비
    

    
    
    
    
    

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
                    stage["CurrentMoment"] = "lie"
                else:
                        
                    if (right_angle>140 and (left_angle>70 and left_angle<=140)) or (left_angle>140 and (right_angle>70 and right_angle<=140)): 
                        stage["CurrentMoment"] = "sit"
                        
                    elif (right_angle>140 and left_angle<75) or (left_angle>140 and right_angle<75): 
                        stage["CurrentMoment"] = "sit"
                        
                    elif ((right_angle>70 and right_angle<=140)and(left_angle<=75)) or ((left_angle>70 and left_angle<=140)and(right_angle<=75)): 
                        stage["CurrentMoment"] = "sit"
                                    
                    elif (right_angle>70 and right_angle<=140) and (left_angle>70 and left_angle<=140): 
                        if calculate_Y_diff(right_knee, right_hip)<=0.1:
                            stage["CurrentMoment"] = "sit"
                        else:
                            stage["CurrentMoment"] = "stand"
                            
                    elif right_angle>140 and left_angle>140:
                        stage["CurrentMoment"] = "stand"
                        
                    elif right_angle<=100 and left_angle<=100: 
                        if calculate_Y_diff(right_knee, right_hip)<=0.1 or calculate_Y_diff(left_knee, left_hip)<=0.1:
                            stage["CurrentMoment"] = "sit"              
            except:
                pass
                
 
                
            # 동작1 sit
            if motion == "stand":
                        #img load
                img = cv2.imread("temp.png")
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
                        print(f"class_ids: {class_ids} {label} x : {x} y : {y}")
                        color = colors[i]
                        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(img, label, (x, y+30), font, 2, color, 2)
                        # meal -> 아니면 점수 +-
                        if label in meal_con:
                            meal_check = meal_check + 1
                        elif label in media_con:
                            score_con = score_con - 1 
                        elif label in work_con:
                            score_con = score_con + 1
                        else:
                            print("no detect object")
                print("sit")                
            
                # meal -> 아니면 점수 체크해서 work or media
                # meal_check로 meal 판단
                if meal_check > 0:
                    stage["CurrentMoment"] = "meal"
                    print("meal")

                elif score_con > 0:
                    stage["CurrentMoment"] = "work"
                    print("work")
                elif score_con < 0:
                    stage["CurrentMoment"] = "media"
                    print("media")
                else:
                    print("Try again")


            #동작2 lie -> sleep
            elif stage["CurrentMoment"] == "lie":
                stage["CurrentMoment"] == "sleep"
                print("lie")
                

            #동작3 stand -> 전 상태 유지    
            else:
                print("stand")


                


            client_socket, client_addr = server_socket.accept()
            # 수신대기, 접속한 클라이언트 정보 (소켓, 주소) 반환

            msg = client_socket.recv(SIZE)
            # 클라이언트가 보낸 메시지 반환

            print("[{}] message : {}".format(client_addr,msg))
            # 클라이언트가 보낸 메시지 출력
            
            
            
            result = json.dumps(stage)
            client_socket.sendall(result.encode())  # 클라이언트에게 응답
            #print("전송 성공" + stage)
            
            
            
            
            
            #스코어 초기화 및 사진 삭제 
            meal_check = 0
            score_con = 0
            os.remove("temp.png")  

                    
        '''
        client_socket, client_addr = server_socket.accept()  # 수신대기, 접속한 클라이언트 정보 (소켓, 주소) 반환
        
        msg = client_socket.recv(SIZE)  # 클라이언트가 보낸 메시지 반환
        
        print("[{}] message : {}".format(client_addr,msg))  # 클라이언트가 보낸 메시지 출력

        result = json.dumps(stage)
        client_socket.sendall(result.encode())  # 클라이언트에게 응답
        print("전송 성공" + stage)
        
        time.sleep(1)
        '''
        
        time.sleep(0.5)
        
    #client_socket.close()  # 클라이언트 소켓 종료
        
        