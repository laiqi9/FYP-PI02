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

# initialize the list of reference points and boolean indicating
mousePt = (0,0)
mouseDown = False

def onMouseButton(event, x, y, flags, param):
    # grab references to the global variables
    global mousePt, mouseDown
    # if the left mouse button was clicked, record the (x, y) coordinates 
    # and indicate mouse button is pressed
    if event == cv2.EVENT_LBUTTONDOWN:
        mousePt = (x, y)
        mouseDown = True
        print("Mouse Down ...")
    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
    # if the left mouse button was released, record the (x, y) coordinates 
    # and indicate mouse button is unclicked
        mousePt = (x, y)
        mouseDown = False
        print("Mouse Up ...")
    elif event == cv2.EVENT_MOUSEMOVE:
        mousePt = (x, y)
        print(x,y)



        
#cv2.setMouseCallback("image", onMouseButton)            
        
# 1. Initializations, Setups 

# Setup Camera Capture:
# 1. Internal Webcam    
cap = cv2.VideoCapture(0) # Internal Webcam
# 2. if you are using IP camera
#cap  = cv2.VideoCapture("rtsp://admin:admin@192.168.10.116:10554/tcp/av0_0")
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
imgRef = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgComposite = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgTemp1 = np.zeros((h, w, 3), dtype = "uint8") # blank images
#imgTemp2 = np.zeros((h, w, 3), dtype = "uint8") # blank images

imgBackground = cv2.imread('./images/paris.bmp')
imgBackground = cv2.resize(imgBackground, (w, h), interpolation=cv2.INTER_AREA)
cv2.imshow('imgBackground',imgBackground) 

imgMask = np.zeros((h, w, 3), dtype = "uint8")   # blank images

# Need to set mouse callback on image window before main loop
imgOut = np.zeros((h, w, 3), dtype = "uint8")   # blank images
cv2.imshow('imgOut',imgOut) 
cv2.setMouseCallback("imgOut", onMouseButton)     

# Other Variables
Threshold = 20

# Main Loop
bLoop = True
while (bLoop):
    
    # Process Keyboard, Mouse Any Other Inputs
    key = cv2.waitKey(1)
    if (key == 27): bLoop = False ; break
    if (key & 0xFF == ord('a')): imgRef = imgIn.copy()
    if (key & 0xFF == ord('c')): imgMask.fill(0)
    
    
    # Capture Input Frame
    ret, frame = cap.read()
    if ret: # ie. camera frame is available, do processing here 
    
        imgIn = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
        cv2.imshow('imgIn',imgIn)            
        
        imgOut = imgIn.copy()
        
        # color = (255, 0, 0) // blue
        if (mouseDown):
            # print("Mouse Down - drawing")
            #cv2.circle(imgOut, mousePt, 5, (0,0,255), -1)
            # Calculate top left corner and bottom right conner of rectangle centered at mousePt
            pt1 = tuple(map(lambda x, y: x - y, mousePt, (10,10))) # ie. pt1 = mousePt - (10,10)
            pt2 = tuple(map(lambda x, y: x + y, mousePt, (10,10))) # ie. pt2 = mousePt + (10,10)
            cv2.rectangle(imgMask, pt1, pt2,(255,255,255) , -1)
            
        imgTemp1 = imgMask.copy()   
        imgTemp1[:,:,0] = 0  # create a copy of mask in yellow by setting blue = 0  
        cv2.addWeighted( imgIn, 0.5, imgTemp1, 0.5, 0.0, imgTemp1 )
        cv2.imshow('imgTemp1',imgTemp1) 
        
        imgOut = cv2.bitwise_and( imgIn, cv2.bitwise_not(imgMask) )  +  cv2.bitwise_and(imgTemp1, imgMask) 
        cv2.imshow('imgOut',imgOut) 
        
        cv2.imshow('imgOut',imgOut)   
        cv2.imshow('imgMask',imgMask)   


        # Layout and Display Results in One Window
        imgResults= concat_vh( [[imgIn, imgIn],
                                [imgRef, imgBackground], 
                                [imgIn, imgOut]]) 
        cv2.imshow("Results", imgResults)
    
# Quit Program with Proper HouseKeeping    
quit(cap) 
