import cv2, time
import numpy as np
 
# From : https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/
# define a function for vertically 
# concatenating images of the 
# same size  and horizontally
def concat_vh(list_2d):
    
      # return final image
    return cv2.vconcat([cv2.hconcat(list_h) 
                        for list_h in list_2d])

# Example Usage:
# # image resizing
# img1_s = cv2.resize(img1, dsize = (0,0),
#                     fx = 0.5, fy = 0.5)
  
# # function calling
# img_tile = concat_vh([[img1_s, img1_s, img1_s],
#                       [img1_s, img1_s, img1_s],
#                       [img1_s, img1_s, img1_s]])
# # show the output image
# cv2.imshow('concat_vh.jpg', img_tile)

# Setup Camera Capture:
# 1. Internal Webcam    
# 2. if you are using IP camera
#cap = cv2.VideoCapture("rtsp://admin:admin@192.168.0.102:554/11")
#cap = cv2.VideoCapture("rtsp://192.168.0.100:554/11")

cap = cv2.VideoCapture(0) # Internal Webcam

w = 1280.0/2 
h = 720.0/2
print("setting resolution", w, h)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("camera actual resolution", w, h)

w = 320
h = 180
print("final resolution", w, h)

# Create Reference Image, set as black
imgRef = np.zeros((h, w, 3), dtype = "uint8")

imgBackground = cv2.imread('Untitled.png')
imgBackground = cv2.resize(imgBackground, (w, h), interpolation=cv2.INTER_AREA)
cv2.imshow('imgBackground',imgBackground) 

time.sleep(2)

ret = 1 #, frame = cap.read()
key = cv2.waitKey(1)

while( ret & (key != 27) ):
 
  ret, frame = cap.read()
    
  if ret: # ie. camera frame is available, do processing here 
    #cv2.imshow('frame',frame)
    
    imgIn = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
    cv2.imshow('imgIn',imgIn)    
    
    imgGray = cv2.cvtColor(imgIn, cv2.COLOR_BGR2GRAY)    
    imgGray = cv2.cvtColor(imgGray, cv2.COLOR_GRAY2BGR) # convert back to 3 channels
    #cv2.imshow('imgGray',imgGray)    
    
    imgDiff = cv2.absdiff(imgIn,imgRef) # (imgIn.copy() - imgRef.copy()) #np.absolute
    #diff = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)
    cv2.imshow('imgDiff',imgDiff) 
    
    threshold = 50
    #result = np.mean(result,2) # axis = 2
    imgMask = np.where(np.max(imgDiff,axis = 2) > threshold, 1, 0)
    #result = cv2.cvtColor( result, cv2.COLOR_GRAY2BGR) 
    # print("result.shape = ", result.shape)
    cv2.imshow("imgMask",(imgMask*255).astype(np.uint8))
    
    imgMask3 = cv2.cvtColor(imgMask.astype(np.uint8), cv2.COLOR_GRAY2BGR).astype(np.uint8)
    cv2.imshow("imgMask3",imgMask3*imgIn + (1-imgMask3)*imgBackground)
    #imgComp = imgIn * (cv2.cvtColor(imgMask, cv2.COLOR_GRAY2BGR).astype(np.uint8))
    #cv2.imshow("imgComp",imgComp.astype(np.uint8))
    
 
    #imgMask = cv2.cvtColor( (result*255).astype(np.uint8), cv2.COLOR_GRAY2BGR) # convert back to 3 channels

    # Layout and Display Output Windows    
    imgLayout = concat_vh( [[imgIn, imgGray],
                            [imgRef, imgIn]])
    
    cv2.imshow("Output", imgLayout)
 
    
    key = cv2.waitKey(1)
    if (key & 0xFF == ord('a')): imgRef = imgIn.copy()
    
cap.release()
cv2.destroyAllWindows()
