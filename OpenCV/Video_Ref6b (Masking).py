import cv2, time
import numpy as np
 
# 0. Declarations

# From : https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/
# define a function for concatenating images vertically and horizontally
def concat_vh(list_2d):
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
imgDiff = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgAve = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgRef = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgContours1 = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgContours2 = np.zeros((h, w, 3), dtype = "uint8")   # blank images

imgMask3 = np.zeros((h, w, 1), dtype = "uint8")   # blank images

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
    if (key & 0xFF == ord('a')): imgRef = imgAve.copy()
    if (key & 0xFF == ord('w')): Threshold += 1; print('Threshold = ', Threshold)
    if (key & 0xFF == ord('s')): Threshold -= 1; print('Threshold = ', Threshold)
    
    # Capture Input Frame
    ret, frame = cap.read()
    if ret: # ie. camera frame is available, do processing here 
    
        imgIn = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
        cv2.imshow('imgIn',imgIn)            
        
        K = 0.05
        cv2.addWeighted( imgIn, K, imgAve, (1-K), K, imgAve);    
        cv2.imshow('imgAve',imgAve)       
        
        imgDiff = cv2.absdiff(imgIn,imgRef) 
        cv2.imshow('imgDiff',imgDiff)                   
        
        # create mask from imgDiff
        imgDiff = cv2.absdiff(imgIn,imgRef) 
        imgDiff = np.max(imgDiff, axis = 2)
        ret, imgMask = cv2.threshold(imgDiff,Threshold,255,cv2.THRESH_BINARY)
        cv2.imshow('imgMask',imgMask) 
        
        # Process Mask using Dilate-Erode
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        img_erosion = cv2.erode(imgMask, kernel, iterations=1)
        img_dilation = cv2.dilate(img_erosion, kernel, iterations=2)
        img_erosion = cv2.erode(img_dilation, kernel, iterations=1)
        imgMask2 = img_erosion
        cv2.imshow('Mask2', imgMask2.astype(np.uint8) )  
        
        # Process Mask using Contours
        threshold_area = 50
        contours, hierarchy = cv2.findContours(image=imgMask2, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    
        imgContours1 = imgIn.copy()
        cv2.drawContours(imgContours1,contours,-1,(0,255,255),1)
        cv2.imshow('imgContours1', imgContours1 ) 
        
        #imgResult = imgInSmall.copy()
        imgContours2[:] = 0 # reset image to zero
        imgMask3[:] = 0     # reset image to zero
        
        selectContours = []  # select and copy items into list to avoid 
                             #  deleting element from a list while looping on it
        for c in contours: 
            rect = cv2.minAreaRect(c)  
            (xR, yR), (wR, hR), angle = rect
            area = cv2.contourArea(c)         
            if ((area > threshold_area) and (wR > 5) and (hR > 5)):                   
                 selectContours.append(c)
                 
        for c in selectContours:
            #rect = cv2.minAreaRect(c)     
            #box = cv2.boxPoints(rect)
            #box = np.int0(box)            
            #cv2.drawContours(imgContours2,[box],0,(0,0,255),2)
            cv2.drawContours(imgContours2, [c], 0, (0,0,255), 1)
            xc,yc,wc,hc = cv2.boundingRect(c)
            cv2.rectangle(imgContours2,(xc,yc),(xc+wc,yc+hc),(0,255,255),2)
            cv2.drawContours(imgMask3, [c], 0, 255, -1)
            
        cv2.imshow('imgContours2', imgContours2 )
        cv2.imshow('imgMask3', imgMask3 )
        
        
        # Cut out foreground object from imgIn using mask
        imgOut = cv2.bitwise_and(imgIn, imgIn, mask = imgMask3)
        
        # Layout and Display Results in One Window
        imgResults= concat_vh( [[imgIn, imgAve],
                                [imgRef, imgOut]]) 
        cv2.imshow("Results", imgResults)
    
# Quit Program with Proper HouseKeeping    
quit(cap)
