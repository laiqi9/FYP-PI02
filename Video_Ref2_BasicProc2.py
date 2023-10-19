import cv2, time
import numpy as np
 
# Setup Camera Capture:
# 1. Internal Webcam    
cap = cv2.VideoCapture(0) # Internal Webcam
# 2. if you are using IP camera
#cap = cv2.VideoCapture("rtsp://admin:admin@192.168.0.102:554/11")
#cap = cv2.VideoCapture("rtsp://192.168.0.100:554/11")

w = 1280.0/2 
h = 720.0/2

# Try to set capture to desired (w,h)
print("setting resolution", w, h)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

# Retrieve actual size (w,h)
w = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH)  /2)
h = int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT) /2)
print("final resolution", w, h)

time.sleep(2)

# Create output matrix
imgOut = np.zeros((h, w, 3), dtype = "float")

 
while( cv2.waitKey(1) != 27): # ESC key -> exit
 
  ret, frame = cap.read()    
  if ret:
    #cv2.imshow('frame',frame)
    imgIn = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)

    #imgOut = imgIn * (0, 1, 1.25)
    imgOut =  cv2.Canny(imgIn, 100, 100)
        
    imgOut = np.clip(imgOut, 0.0, 255.0).astype(np.uint8)
    cv2.imshow('image',imgOut)         
 
cap.release()
cv2.destroyAllWindows()
