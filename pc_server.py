# -*- coding: utf-8 -*-
import sys
from flask import Flask, request
import cv2
import numpy as np
import threading
import os
import easyocr
from difflib import SequenceMatcher
import time
import sql_robot

sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

reader = easyocr.Reader(['ko', 'en'], gpu=False)
# 받은 프레임을 저장할 변수
global received_frame, capture
capture = False
received_frame = None
frame_lock = threading.Lock()

# threading 이벤트를 사용하여 프레임이 도착할 때까지 대기
new_frame_event = threading.Event()

# 이미지를 저장할 디렉토리 생성
save_dir = 'received_frames'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 이미지를 받는 스레드 함수
def receive_frame_thread():
    global received_frame, new_frame_event
    while True:
        with frame_lock:
            if received_frame is not None:
                gray = cv2.cvtColor(received_frame, cv2.COLOR_BGR2GRAY)
                text = reader.readtext(gray, detail=0)

                text = "".join(text)
                print(text)
                print("유사도 : ", SequenceMatcher(None, "선형대수학 입문", text).ratio())

                # 프레임 처리 후 이벤트 설정
                new_frame_event.set()

                # 현재 프레임 초기화
                received_frame = None

                # ocr 결과값으로 x, y위치 가지고 오기
                result = sql_robot.robot_run(text)

                # result[0][pos_x], result[0][pos_y]를 robot에게 전달



# 스레드 시작
receive_thread = threading.Thread(target=receive_frame_thread)
receive_thread.start()

@app.route('/update_frame', methods=['POST'])
def update_frame():
    global received_frame, new_frame_event, capture
    # 전송된 프레임 받기
    frame_data = request.files['frame'].read()
    nparr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 받은 프레임을 전역 변수에 저장
    with frame_lock:
        received_frame = frame

    # 새로운 프레임 도착 이벤트를 리셋 (새로운 프레임이 도착할 때까지 대기하기 위해)
    new_frame_event.clear()

    # 대기 후 새로운 프레임 도착 시까지 기다림
    new_frame_event.wait()
    capture = 0
    # 프레임 처리 후 응답
    return 'Frame received and processed successfully'

@app.route('/capture')
def capture_true():
    global capture
    
    capture = 1
    return f"{capture}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)