# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 19:08:59 2023

@author: lohchinfei
"""
# importing required libraries 
import cv2, time 
import numpy as np

from WebcamStream_0p0 import WebcamStream

# From : https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/
# define a function for concatenating images vertically and horizontally
def concat_vh(list_2d):
    return cv2.vconcat([cv2.hconcat(list_h) 
                        for list_h in list_2d])

mainTitle = "Security Systems v0.2"
mouseX = 0; 
mouseY = 0
mouseDown   = False
mouseUp     = False
mouseMove   = False

def onMouseButton(event, x, y, flags, param):
    
    global mouseX, mouseY, mouseDown, mouseUp, mouseMove, mouseState
     
    if event == cv2.EVENT_LBUTTONDOWN:
        print("onMouseButton: Mouse Down Event ...")
        mouseX = x; mouseY = y; mouseDown = True;  mouseUp = False;  
  
    if event == cv2.EVENT_LBUTTONUP:
        print("onMouseButton: Mouse Up Event ...")
        mouseX = x; mouseY = y; mouseDown = False;  mouseUp = True; 

    if event == cv2.EVENT_MOUSEMOVE:
        #print("onMouseButton: Mouse Move ...")
        mouseX = x; mouseY = y; mouseMove = True;    
        

def gridRect( img, xc, yc, grid = 20, color = (255,255,0)):
    r = int(grid/2)
    xc = int(xc/grid)*grid + r
    yc = int(yc/grid)*grid + r
    pt1 = tuple(map(lambda a, b: a - b, (xc,yc), (r,r))) # ie. pt1 = (xc,yc) - (10,10)
    pt2 = tuple(map(lambda a, b: a + b, (xc,yc), (r,r))) # ie. pt2 = (xc,yc) + (10,10)
    cv2.rectangle(img, pt1, pt2, color , -1)


# for updating moving average imageMaFast and imgMAslow
def updateKfKs():
    global imgMAFast, imgMASlow, imgIn, imgMAAve, imgInSmall
    global Ks_target, Kf_target, Ks, Kf, Ka 
    global imgMAFastReady, imgMASlowReady
    
    #imgMAFast = Kf * imgIn + (1-Kf)*imgMAFast
    #imgMASlow = Ks * imgIn + (1-Ks)*imgMASlow 
    imgTemp = imgInSmall.astype(np.float32)
    imgMAFast = cv2.addWeighted(imgTemp,Kf,imgMAFast,(1-Kf),0)
    imgMASlow = cv2.addWeighted(imgMAFast,Ks,imgMASlow,(1-Ks),0)

    cv2.imshow('imgMASlow', imgMASlow.astype(np.uint8) )
    cv2.imshow('imgMAFast', imgMAFast.astype(np.uint8) )

    if ( (not imgMAFastReady) or (not imgMASlowReady) ):  
        Kf = Ka * Kf_target + (1-Ka)*Kf
        Ks = Ka * Ks_target + (1-Ka)*Ks
        if ( Kf < 1.01 * Kf_target ): imgMAFastReady = True
        if ( Ks < 1.01 * Ks_target ): imgMASlowReady = True
        #print(Kf, Ks, (not imgMAFastReady) , (not imgMASlowReady)  )
        

def doFGDetect():
    global imgMAFast, imgMASlow, imgIn, imgResult, imgInSmall, imgDrawOver
    
    # update moving average images imgMAFast and imgMASlow
    updateKfKs()
    imgTemp = cv2.absdiff(imgMAFast, imgMASlow) # imgRef1
    cv2.imshow('Diff', imgTemp.astype(np.uint8) )      
    #imgTemp2 = imgTemp.copy()
    #cv2.multiply( imgTemp, imgTemp, imgTemp2 )  
    #imgRMSSumRGB = imgTemp2 .sum(axis=-1) / 3
    #imgRMSSumRGB = (imgTemp*imgTemp)
    #imgRMSSumRGB = np.sqrt(imgRMSSumRGB).astype(np.uint8)    

    b,g,r = cv2.split(imgTemp)
    b2 = cv2.multiply( b, b )
    g2 = cv2.multiply( g, g )
    r2 = cv2.multiply( r, r )
    
    imgRMSSumRGB = b2.copy() 
    imgRMSSumRGB = cv2.add( imgRMSSumRGB, g2) 
    imgRMSSumRGB = cv2.add( imgRMSSumRGB, r2)
    imgRMSSumRGB = cv2.multiply(imgRMSSumRGB, 1.0/3.0)
    imgRMSSumRGB = cv2.sqrt(imgRMSSumRGB)
    imgTemp = imgRMSSumRGB.astype(np.uint8)
    cv2.imshow('imgRMSSumRGB', imgTemp )

    #cv2.bitwise_and(	imgTemp, imgROIMask)      
    ret2,imgTemp2 = cv2.threshold( cv2.bitwise_and( imgTemp, imgROIMask),      
                                  threshold, 255, cv2.THRESH_BINARY )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    img_erosion = cv2.erode(imgTemp2, kernel, iterations=1)
    img_dilation = cv2.dilate(img_erosion, kernel, iterations=2)
    img_erosion = cv2.erode(img_dilation, kernel, iterations=1)
    imgMask3 = img_erosion
    cv2.imshow('Mask3', imgMask3.astype(np.uint8) )      


    threshold_area = 50
    contours, hierarchy = cv2.findContours(image=imgMask3, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

    imgResult = imgInSmall.copy()
    cv2.drawContours(imgResult,contours,-1,(0,255,255),1)
    cv2.imshow('imgResult Contours', imgResult ) 
    
    #imgResult = imgInSmall.copy()
    imgDrawOver[:] = 0 # reset image to zero
    selectContours = []  # copy it, to avoid deleting element from a list while looping on it!
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
        #cv2.drawContours(imgContours,[box],0,(0,0,255),2)
        xc,yc,wc,hc = cv2.boundingRect(c)
        cv2.rectangle(imgDrawOver,(xc,yc),(xc+wc,yc+hc),(0,255,255),2)
    cv2.imshow('imgDrawOver', imgDrawOver )
          
            
    

# Setup Camera
w = 1280 
h = 720 
 
# initializing and starting multi-threaded webcam capture input stream 
src = 0 #"rtsp://admin:888888@192.168.10.116:10554/tcp/av0_0"
webcamStream = WebcamStream( name = "WebcamStream0", src = src, width = w, height = h  ) 
webcamStream.start()

# Note: final w,h : need to manually set this (for now) ...
w =  int(1280/2) 
h =  int(720/2) 



# Create matrix for images
imgIn = np.zeros((h*2, w*2, 3), dtype = "uint8")   # blank images
#imgOut = np.zeros((h, w, 3), dtype = "float")
imgOut = np.zeros((h, w, 3), dtype = "uint8")
imgRef = np.zeros((h, w, 3), dtype = "uint8")   

imgDrawOver = np.zeros((h, w, 3), dtype = "uint8")   

imgMain     = np.zeros((h*2, w*2, 3), dtype = "uint8") # blank images
imgROIDraw  = np.zeros((h*2, w*2, 3), dtype = "uint8") 
imgROIonImgIn = np.zeros((h*2, w*2, 3), dtype = "uint8")    

imgROIMask  = np.zeros((h, w, 1), dtype = "uint8")    
imgROIMask3 = np.zeros((h, w, 3), dtype = "uint8")    

# Load imgROIDraw if file is present.
if cv2.haveImageReader('imgROIDraw.bmp'):
    imgROIDraw = cv2.imread('imgROIDraw.bmp')  
else:
    # otherwise create the first version (blank)
    cv2.imwrite('imgROIDraw.bmp',imgROIDraw) 

# Process ROIDraw to ROIMask
#= cv2.resize(imgIn, (w, h), interpolation=cv2.INTER_AREA)
cv2.extractChannel( 
     cv2.resize(imgROIDraw, (w, h), interpolation=cv2.INTER_NEAREST), 
     1, imgROIMask) # use G only
cv2.mixChannels([cv2.resize(imgROIDraw, (w, h), interpolation=cv2.INTER_NEAREST)],
                [imgROIMask3], 
                [1,0, 1,1, 1,2])
cv2.imshow('imgROIDraw', imgROIDraw) 
cv2.imshow('imgROIMask', imgROIMask)  # num of channels = 1
cv2.imshow('imgROIMask3', imgROIMask3) # num of channels = 3
    
imgMASlow = np.zeros((h, w, 3), dtype = "float32")   # blank images
imgMAFast = np.zeros((h, w, 3), dtype = "float32")   # blank images

imgResult = np.zeros((h, w, 3), dtype = "uint8")   # blank images


Ks_target = 1e-5 #1e-5 or 0.00001  # target slow MA update speed
Kf_target = 0.25   # target faster MA update speed
Ks = 1.0   # Ks value, adapts to target value eventually
Kf = 1.0   # Kf value, adapts to target value eventually
Ka = 0.05  # Ks and Kf adaptation rate. 

imgMASlowReady = False
imgMAFastReady = False
imgRef1Ready = False
imgMACount = 0

# Other Variables
firstRun = True
threshold = 15



# Main Loop
prevState = 0
nowState  = 1 
nextState = 0 # 0 is reserved or non-changing states

mousePressed = False   # mouse button is being held down or not

loop = True
while( loop ): 

    # Process Keyboard, Mouse Any Other Inputs - Global
    key = cv2.waitKey(1)    
    

    # Check if Camera Frame is available.
    newFrame = False
    if (webcamStream.avail):
        #print("Main: input frame available.")
        frame = webcamStream.read()
        
        imgIn = frame.copy()  
        cv2.imshow("imgIn", imgIn)
        
        imgInSmall = cv2.resize(imgIn, (w, h), interpolation=cv2.INTER_AREA)
        imgOut = imgInSmall.copy()  
        
        newFrame = True
        
        cv2.imshow('imgInSmall',imgInSmall)
        cv2.imshow('imgOut',imgOut)
        
    
    if nowState == 1:  # state 1: initial setups inside loop
        if (key == 27): bLoop = False ; break # ESC key -> exit loop

        # Set up main window, attach mouse callback
        cv2.imshow(mainTitle, imgMain)
        cv2.setMouseCallback(mainTitle, onMouseButton) 

        # Go to state 2
        nextState = 2
        if (nextState != 0):
            prevState = nowState; nowState = nextState; nextState = 0
        
    if nowState == 2:  # state 2: main loop state
        #if (key == 27): nextState = 1; # ESC key -> go back one state
        if (key == 27): bLoop = False ; break # ESC key -> exit loop

        # Process New Incoming Frames
        if newFrame:

            # Process New Frame
            doFGDetect()

            # Layout and Show Main Window for Stage 2
            imgMain = concat_vh( [[imgInSmall, cv2.bitwise_or(imgInSmall, imgDrawOver)],
                                  [imgRef,     imgOut]]) 
            cv2.imshow(mainTitle, imgMain)
        
        # Process users inputs 
        if (key & 0xFF == ord('f')): imgRef = imgInSmall.copy() 
        if (key & 0xFF == ord('[')): 
            Ks = 1.0; Kf = 1.0; 
            imgMAFastReady = False; 
            imgMASlowReady = False
    
        # If mouse click at top right image, go to state 2 
        if (mouseDown):
            print("Main.2: mouseDown at " + str(mouseX) + ", " + str(mouseY) ) 
            # Go to state 3 if mouse pressed over top right quadrant of window
            if (mouseX > w and mouseY < h): 
                print("Main.2: go to state 3")
                nextState = 3
            mouseDown = False; # ie. reset trigger
    
        if (mouseUp):
            print("Main.2: mouseDown at " + str(mouseX) + ", " + str(mouseY) )        
            mouseUp = False;    # ie. reset trigger

        # if state change, go to next state 
        if (nextState != 0):
           prevState = nowState; nowState = nextState; nextState = 0

    if nowState == 3:
        if (key == 27): nextState = 2; # ESC key -> go back one state

        # print("Main.3: entered State 3. Press Enter to go back to State 2")
        if newFrame:
            # Set up Main Window Layout for Stage 3
            imgMain = imgIn.copy()    
            # overlap ROI over imgIn before displaying
            cv2.addWeighted( imgMain, 0.95, imgROIDraw, 0.2, 0.0, imgROIonImgIn )
            #cv2.imshow('imgROIDraw',imgROIDraw)
            cv2.imshow(mainTitle, imgROIonImgIn) 
            

        # Process users inputs 
        if (key & 0xFF == 13): # Press Enter (13) to go back to State 2 
            print("Main.3: going back to state 2")
            nextState = 2 
        if (key & 0xFF == ord('s')): # Press s to save imgROIDraw
            print("Main.3: saving imgROIDraw")
            cv2.imwrite('imgROIDraw.bmp',imgROIDraw)            
        if (key & 0xFF == ord('l')): # Press l to load imgROIDraw
            print("Main.3: loading imgROIDraw")
            imgROIDraw = cv2.imread('imgROIDraw.bmp')            
        if (key & 0xFF == ord('c')): # Press c to Clear imgROIDraw
            #imgROIDraw = np.zeros((h*2, w*2, 3), dtype = "uint8")   # clear 
            print("Main.3: clearing imgROIDraw")
            imgROIDraw[:] = 0

        if (mouseDown):
            print("Main.3: mouseDown at " + str(mouseX) + ", " + str(mouseY) ); 
            gridRect(imgROIDraw, mouseX, mouseY, grid=30, color=(0,255,255))
            #cv2.imshow("imgROIDraw",imgROIDraw)
            mousePressed = True
            mouseDown = False;  # ie. reset trigger
            
        if (mouseMove):
             print("Main.3: mouseMove at " + str(mouseX) + ", " + str(mouseY) ); 
             if mousePressed:
                 gridRect(imgROIDraw, mouseX, mouseY, grid=30, color=(0,255,255))
             #cv2.imshow("imgROIDraw",imgROIDraw)
             mouseMove = False   # ie. reset trigger

        if (mouseUp):
            print("Main.3: mouseDown at " + str(mouseX) + ", " + str(mouseY) )        
            mousePressed = False
            mouseUp = False;    # ie. reset trigger

        # if state change, go to next state 
        if (nextState != 0):
            # Process ROIDraw to ROIMask
            #imgROIMask = imgROIDraw.copy()
            cv2.extractChannel( 
                 cv2.resize(imgROIDraw, (w, h), interpolation=cv2.INTER_NEAREST), 
                 1, imgROIMask) # use G only
            cv2.mixChannels([cv2.resize(imgROIDraw, (w, h), interpolation=cv2.INTER_NEAREST)],
                            [imgROIMask3], 
                            [1,0, 1,1, 1,2])
            cv2.imshow('imgROIDraw', imgROIDraw) 
            cv2.imshow('imgROIMask', imgROIMask)  # num of channels = 1
            cv2.imshow('imgROIMask3', imgROIMask3) # num of channels = 3


            prevState = nowState; nowState = nextState; nextState = 0
           
    if nowState == 9: # Reserved, State 9 is currently NOT USED. 
        print("Main.9: entered State 9. Exiting loop ... ")
        # do any necessary house keeping here before quiting loop (if any)
        break;
        
    
# stop all threads and closing all windows 
#  webcamStream.stop() ; cv2.destroyAllWindows()
webcamStream.stop()
cv2.destroyAllWindows()