import cv2
from ultralytics import YOLO
import numpy as np
import random
import torch
import base64
import socketio

# เปิดใช้การปรับแต่งของ OpenCV
cv2.setUseOptimized(True)

# เชื่อมต่อไปยัง server.js ที่ใช้ socket.io
sio = socketio.Client()

print("Connecting to server...")  # แสดง log ก่อนการเชื่อมต่อ
sio.connect('http://localhost:5501')

print("Connected to server.")  # แสดง log เมื่อเชื่อมต่อสำเร็จ

# โหลดโมเดล YOLOv9e
print("Loading YOLO model...")
model = YOLO('best.pt')

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")
model.to(device)

# สร้างสีสำหรับแต่ละ label
label_colors = {}

def get_label_color(label):
    if label not in label_colors:
        label_colors[label] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return label_colors[label]

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Starting video capture...")

redBin = ['battery', 'mobile-phone', 'mouse', 'light-bulb', 'fluorescent-lamp', 'earphone', 'cable', 'spray']
yellowBin = ['PET-plastic-bottle', 'PE-plastic-bag', 'broken-glass', 'metal-can', 'paper', 'taobin', 'transparent-plastic-bottle']
greenBin = ['animal-waste', 'banana-peel', 'orange-peel']
blueBin = ['snack-package', 'tissue-paper', 'foam']

label_color = (1, 1, 1)
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    print("Running YOLO inference...")
    # ทำการตรวจจับ instance segmentation บน frame จากกล้อง
    results = model(frame, batch=1)

    annotated_frame = frame.copy()
    
    all_labels = []
    if results[0].masks is not None:
        for i, mask in enumerate(results[0].masks.data):
            binary_mask = mask.cpu().numpy().astype('uint8') * 255
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # ดึงสีของ label
            label = results[0].names[results[0].boxes.cls[i].item()]
            # label_color = get_label_color(label)
            if label in redBin:
                label_color = (0, 0, 255)
            elif label in greenBin:
                label_color = (0, 255, 0)
            elif label in blueBin:
                label_color = (255, 0, 0)
            elif label in yellowBin:
                label_color = (0, 255, 255)
            else:
                label_color = (1, 1, 1)
            # print(label_colors[label])

            

            all_labels.append(label)
            # print(label, type(label))

            # วาดเส้นรอบ mask
            cv2.drawContours(annotated_frame, contours, -1, label_color, 4)

            # แสดง label และ score
            score = results[0].boxes.conf[i].item() * 100
            label_text = f'{label} {score:.2f}%'
            

            (text_width, text_height), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            x, y = int(results[0].boxes.xyxy[i][0]), int(results[0].boxes.xyxy[i][1])

            # วาดพื้นหลังสีตาม label
            cv2.rectangle(annotated_frame, (x, y - text_height - baseline), (x + text_width, y), label_color, -1)

            # วาดตัวอักษรสีขาว
            cv2.putText(annotated_frame, label_text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # แปลงภาพเป็น base64
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')

    # ส่งข้อมูลไปที่ server.js
    print("Sending frame to server...")
    sio.emit('video_frame', {'frame_base64': frame_base64, 'all_labels': all_labels})
    
    # print("names: ", results[0].names)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("Releasing video capture...")
cap.release()
