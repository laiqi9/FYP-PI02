import cv2, time
 
# Setup Camera Capture:
# 1. Internal Webcam    
#cap = cv2.VideoCapture(0) # Internal Webcam
# 2. if you are using IP camera
#cap = cv2.VideoCapture("rtsp://admin:admin@192.168.0.102:554/11")
cap = cv2.VideoCapture(0)

time.sleep(2)
 
while(True):
 
  ret, frame = cap.read()
  
  # print(ret)
  
  if ret:
    cv2.imshow('frame',frame)
  # else:
  #   print("no video")
  
  
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break
 
cap.release()
cv2.destroyAllWindows()
