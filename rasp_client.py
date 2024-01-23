import cv2
import requests
import numpy as np

server_address = 'http://192.168.1.187:5000/update_frame'
signal_endpoint = 'http://192.168.1.187:5000/capture_ture'

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    
    response_signal = requests.get(signal_endpoint)
    print("response : ", response_signal.text)
    signal = int(response_signal.text)
    
    if signal == 1:
        _, img_encoded = cv2.imencode('.jpg', frame)
        response = requests.post(server_address, files={'frame': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')})
        print(response.text)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()