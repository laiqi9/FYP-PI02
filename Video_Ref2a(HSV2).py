import cv2, time
import numpy as np

# From : https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/
# defining a function for concatenating images vertically and horizontally
def concat_vh(list_2d):
    
      # return final image

    return cv2.vconcat([cv2.hconcat(list_h) 
                        for list_h in list_2d])

# Quit Program with Proper HouseKeeping
def quit(cap):
    if (cap.isOpened()): cap.release()
    cv2.destroyAllWindows()
    
# Initializations, Setups 
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture("rtsp://admin:88888888@192.168.0.104:10554/tcp/av0_1")
time.sleep(2)

width = 1280.0/2 
height = 720.0/2
print("setting camera resolution: ", width, height)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("camera actual resolution received: ", width, height)

width = 640
height = 360
print("final input image resolution used: ", width, height)

# Initialise Necessary Variables
imgIn = np.zeros((height, width, 3), dtype = "uint8")   # blank images
imgIn2 = np.zeros((height, width, 3), dtype = "uint8")   # blank images
imgRunAve = np.zeros((height, width, 3), dtype = "float32")   # blank images
imgRef = np.zeros((height, width, 3), dtype = "uint8")   # blank images
imgMask = np.zeros((height, width, 1), dtype = "uint8")   # blank images
th = 20
ts = 40
tv = 50
lower = np.array([th, ts, tv]) 
upper = np.array([255, 255, 255]) 

Ks = 0.001
Kf = 0.25
K = Ks

# Main Loop
bLoop = True
while (bLoop):
    
    # Process Keyboard, Mouse Any Other Inputs
    key = cv2.waitKey(1)
    if (key == 27): bLoop = False ; break
    if (key & 0xFF == ord('f')): imgRef = imgIn.copy(); imgRunAve = imgIn.astype(np.float32)
    if (key & 0xFF == ord('a')): th -=1; print("th = ", th)
    if (key & 0xFF == ord('q')): th +=1; print("th = ", th)
    if (key & 0xFF == ord('s')): ts -=1; print("ts = ", ts)
    if (key & 0xFF == ord('w')): ts +=1; print("ts = ", ts)
    if (key & 0xFF == ord('d')): tv -=1; print("tv = ", tv)
    if (key & 0xFF == ord('e')): tv +=1; print("tv = ", tv)

    lower = np.array([th, ts, tv]) 

    # # Capture Input Frame
    ret, frame = cap.read()
    
    if ret: # ie. camera frame is available, do processing here
        
        imgIn = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        imgRunAve = cv2.addWeighted(imgIn.astype(np.float32), K, imgRunAve, (1.0-K), 0.0)
        cv2.imshow('imgRunAve',imgRunAve.astype(np.uint8))  
        
        imgRef = imgRunAve.astype(np.uint8)

        
        imgRefHSV = cv2.cvtColor(imgRef, cv2.COLOR_BGR2HSV)
        cv2.imshow('imgRefHSV',imgRefHSV.astype(np.uint8))  

        imgInHSV = cv2.cvtColor(imgIn, cv2.COLOR_BGR2HSV)
                
        H = imgInHSV[:,:,0]
        S = imgInHSV[:,:,1]
        V = imgInHSV[:,:,2]

        # Display H component in full color 
        imgTemp2 = np.zeros((height, width, 3), dtype = "uint8")
        imgTemp2[:,:,0] = H
        imgTemp2[:,:,1].fill(255)  # 100% saturated
        imgTemp2[:,:,2].fill(255)  # 100% luminance
        imgH_in_color = cv2.cvtColor(imgTemp2, cv2.COLOR_HSV2BGR)
        cv2.imshow('H_in_color',imgH_in_color)  
        
        cv2.imshow('S',S)  
        cv2.imshow('V',V)  

        # Extract H component from imgIn and imgRef
        imgInH  = imgInHSV[:,:,0]   
        imgRefH = imgRefHSV[:,:,0]  

        # hue range is 0-180, so need to correct negative values present in dh
        #   if diff in hue is greater than 90, correct it i.e. dh = 180 - dh
        dh =  cv2.absdiff(imgInH, imgRefH)  
         
        dh[dh>90] = 180.0 - dh[dh>90] 
         
        imgDiffAbs = cv2.absdiff(imgInHSV, imgRefHSV)
  
        # Only use ds and dv here. Will use dh obtained earlier above
        ds = imgDiffAbs[:,:,1]
        dv = imgDiffAbs[:,:,2]

        cv2.imshow("dh", dh)  #.astype(np.uint8))
        cv2.imshow("ds", ds)
        cv2.imshow("dv", dv)

        # Create mask here:        
        imgMask.fill(0) # reset mask
        
        # test different conditions for creating mask
        imgMask[dv>tv] = 255
        # #imgMask[ds>ts] = 255
        imgMask[ np.where( (ds>ts) & (V > 20) ) ] = 255
        imgMask[ np.where( (dh>th) & (S>50) & (V > 50) ) ] = 255
        
        cv2.imshow("imgMask", imgMask)
        floatVal = cv2.countNonZero(imgMask)/imgMask.size * 100
        format_floatVal = "{:.2f}".format(floatVal)
        print(format_floatVal)
        

    
        # Layout and Display Results in One Window
        imgResults= concat_vh([[imgIn2, imgRef],
                               [imgDiffAbs, imgRefHSV]]) 
            
        cv2.imshow("Results", imgResults)
            
                   
# Quit Program with Proper HouseKeeping    
quit(cap)
