import cv2
import mediapipe as mp
import numpy as np
import math

class detector():
    def __init__(self):
        # self.hand_detector = mp.solutions.hands.Hands()
        self.mp_pose = mp.solutions.pose
        self.drawer = mp.solutions.drawing_utils

        
    def calculate_angle(self, a, b, c):
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360.0 - angle
        
        return angle
    
    def calculate_dis(self, a, b):
        a = np.array(a)
        b = np.array(b)
        return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
    
    def identify (self, shoulderLeft, shoulderRight, hipLeft, hipRight, kneeLeft, kneeRight, footLeft, footRight, eyeLeft, eyeRight, handLeft, handRight, earLeft, earRight):
        string = 'None'
        angleSHK = self.calculate_angle(shoulderLeft, hipLeft, kneeLeft)

        # 卷腹类
        if abs(hipLeft[1] - footLeft[1]) < 10:  # 0.1是一个可以调整的阈值，根据实际情况调整
            foot_hip_height_condition = True
        else:
            foot_hip_height_condition = False
        if 60<angleSHK < 110 and foot_hip_height_condition:
            string = 'Sit-up'
            return string

        #单侧前屈
        #手-脚距离远小于手-膝距离   眼-膝盖距离远小于头-手距离  膝-臀-肩角度小于六十度
        if self.calculate_dis(handLeft, footLeft) < self.calculate_dis(handLeft, kneeLeft) and self.calculate_dis(eyeLeft, kneeLeft) < self.calculate_dis(eyeLeft, handLeft) and angleSHK < 60:
            string = 'forward fold'
            return string
        if self.calculate_dis(handRight, footRight) < self.calculate_dis(handRight, kneeRight) and self.calculate_dis(eyeRight, kneeRight) < self.calculate_dis(eyeRight, handRight) and angleSHK < 60:
            string = 'forward fold'
            return string
        
        #平板支撑类
        #单手低于头 耳在眼上    眼-肩-臀角度大
        angleESH = self.calculate_angle(eyeLeft, shoulderLeft, hipLeft)
        if (eyeRight>handRight or eyeLeft>handLeft) and (earLeft[1]<eyeLeft[1] or earRight[1]>eyeRight[1]) and angleESH > 135:
            string = 'plank'

        #站立腿部拉伸-立式体前屈
        #眼低于臀   手-脚距离小于手-肩距离  肩高于臀高于膝高于脚
        if eyeLeft[1] > hipLeft[1] and eyeRight[1] > hipRight[1] and self.calculate_dis(handLeft, footLeft) < self.calculate_dis(handLeft, shoulderLeft) and shoulderLeft[1] < hipLeft[1] < kneeLeft[1] < footLeft[1]:
            string = 'Standing forward bend'

        return string

        
    
    def process_frame(self, img):
        pose = self.mp_pose.Pose(static_image_mode=False,        # 是静态图片还是连续视频帧
        model_complexity=0,            # 选择人体姿态关键点检测模型，0性能差但快，2性能好但慢，1介于两者之间
        smooth_landmarks=True,         # 是否平滑关键点 
        min_detection_confidence=0.5,  # 置信度阈值
        min_tracking_confidence=0.5)   # 追踪阈值
        
        h, w = img.shape[0], img.shape[1]

        img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_RGB)
        string = 'None'

        # 在这里添加判断逻辑
        if results.pose_landmarks:
            self.drawer.draw_landmarks(img, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            # x=[]; y=[]; z=[]
            # # 添加判断逻辑
            # # 例如，计算肩膀和膝盖之间的角度
            # for i in range(33):
            #     tx = results.pose_landmarks.landmark[i].x * w; ty = results.pose_landmarks.landmark[i].y * h
            #     x.append(tx)
            #     y.append(ty)
            #     z.append(results.pose_landmarks.landmark[i].z)
            
            
            landmarks = results.pose_landmarks.landmark
            
            shoulderLeft = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            shoulderRight = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            hipLeft = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            hipRight = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            kneeLeft = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            kneeRight = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            footLeft = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            footRight = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            eyeLeft = [landmarks[self.mp_pose.PoseLandmark.LEFT_EYE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_EYE.value].y]
            eyeRight = [landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE.value].x,
                        landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE.value].y]
            handLeft = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            handRight = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            earLeft = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y]
            earRight = [landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value].x,
                        landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value].y]

            
            string = self.identify(shoulderLeft, shoulderRight, hipLeft, hipRight, kneeLeft, kneeRight, footLeft, footRight, eyeLeft, eyeRight, handLeft, handRight, earLeft, earRight)
            cv2.putText(img, string, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            # else:
            #     cv2.putText(img, 'Not Sit-up', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        return string