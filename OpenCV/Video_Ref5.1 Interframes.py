import cv2, time
import numpy as np
 
# 0. Declarations

# From : https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/
# define a function for concatenating images vertically and horizontally
def concat_vh(list_2d):
    
      # return final image
    return cv2.vconcat([cv2.hconcat(list_h) 
                        for list_h in list_2d])

# Quit Program with Proper HouseKeeping
def quit(cap):
    if (cap.isOpened()): cap.release()
    cv2.destroyAllWindows()
    

# 1. Initializations, Setups 

# Setup Camera Capture:
# 1. Internal Webcam    
cap = cv2.VideoCapture(0) # Internal Webcam
# 2. if you are using IP camera
#cap = cv2.VideoCapture("rtsp://admin:admin@192.168.0.102:554/11")
#cap = cv2.VideoCapture("rtsp://192.168.0.100:554/11")
time.sleep(2) # pause while camera turns on, just in case

w = 1280.0/2 
h = 720.0/2
print("setting camera resolution: ", w, h)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("camera actual resolution received: ", w, h)

w = 320
h = 180
print("final input image resolution used: ", w, h)

# Initialise, Load Necessary Images

imgIn = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgOut = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgPrev = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgRef = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgDiff = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgAve = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgComposite = np.zeros((h, w, 3), dtype = "uint8")   # blank images
#imgTemp1 = np.zeros((h, w, 3), dtype = "uint8") # blank images
#imgTemp2 = np.zeros((h, w, 3), dtype = "uint8") # blank images

imgBackground = cv2.imread('paris.bmp')
imgBackground = cv2.resize(imgBackground, (w, h), interpolation=cv2.INTER_AREA)
cv2.imshow('imgBackground',imgBackground) 


# Other Variables
Threshold = 20

# Main Loop
bLoop = True
while (bLoop):
    
    # Pre-processing
    imgPrev = imgIn.copy()  # make a copy of previous frame

    # Process Keyboard, Mouse Any Other Inputs
    key = cv2.waitKey(1)
    if (key == 27): bLoop = False ; break
    
    # Capture Input Frame
    ret, frame = cap.read()
    if ret: # ie. camera frame is available, do processing here 
    
        imgIn = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
        cv2.imshow('imgIn',imgIn)            
        
        K = 0.2
        cv2.addWeighted( imgIn, K, imgPrev, (1-K), 0.0, imgAve);    
        cv2.imshow('imgAve',imgAve)       
        
        imgDiff = cv2.absdiff(imgIn,imgPrev) 
        cv2.imshow('imgDiff',imgDiff)                   
        
        # Layout and Display Results in One Window
        imgResults= concat_vh( [[imgPrev, imgAve],
                                [imgPrev, imgDiff]]) 
        cv2.imshow("Results", imgResults)
    
# Quit Program with Proper HouseKeeping    
quit(cap) 
