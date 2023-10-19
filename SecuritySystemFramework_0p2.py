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
     
w = 1280 
h = 720 
 
# initializing and starting multi-threaded webcam capture input stream 
webcamStream = WebcamStream( name = "WebcamStream0", src = 0, width = w, height = h  ) 
webcamStream.start()

# Note: final w,h : need to manually set this (for now) ...
w =  int(1280/2) 
h =  int(720/2) 

firstRun = True

# Create matrix for images
imgIn = np.zeros((h, w, 3), dtype = "uint8")   # blank images
#imgOut = np.zeros((h, w, 3), dtype = "float")
imgOut = np.zeros((h, w, 3), dtype = "uint8")
imgRef = np.zeros((h, w, 3), dtype = "uint8")   

imgMain     = np.zeros((h*2, w*2, 3), dtype = "uint8") # blank images
imgROIDraw  = np.zeros((h*2, w*2, 3), dtype = "uint8") 
imgROIMask  = np.zeros((h*2, w*2, 3), dtype = "uint8")    
imgROIonImgIn = np.zeros((h*2, w*2, 3), dtype = "uint8")    

# Main Loop
prevState = 0
nowState  = 1 
nextState = 0 # 0 is reserved or non-changing states

mousePressed = False   # mouse button is being held down or not

loop = True
while( loop ): 

    # Process Keyboard, Mouse Any Other Inputs - Global
    key = cv2.waitKey(1)    
    if (key == 27): bLoop = False ; break # ESC key -> exit loop


    # Check if Camera Frame is available.
    newFrame = False
    if (webcamStream.avail):
        #print("Main: input frame available.")
        frame = webcamStream.read()
        
        imgIn = frame.copy()  
        
        imgInSmall = cv2.resize(imgIn, (w, h), interpolation=cv2.INTER_AREA)
        imgOut = imgInSmall.copy()  
        
        newFrame = True
        
        cv2.imshow('imgInSmall',imgInSmall)
        cv2.imshow('imgOut',imgOut)
        
    
    if nowState == 1:  # state 1: initial setups inside loop

        # Set up main window, attach mouse callback
        cv2.imshow(mainTitle, imgMain)
        cv2.setMouseCallback(mainTitle, onMouseButton) 

        # Go to state 2
        nextState = 2
        if (nextState != 0):
            prevState = nowState; nowState = nextState; nextState = 0
        
    if nowState == 2:

        # Process New Incoming Frames
        if newFrame:
            # Layout and Show Main Window for Stage 2
            imgMain = concat_vh( [[imgInSmall, imgInSmall],
                                  [imgRef,     imgOut]]) 
            cv2.imshow(mainTitle, imgMain)
        
        # Process users inputs 
        if (key & 0xFF == ord('f')): imgRef = imgInSmall.copy() 
    
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
        # print("Main.3: entered State 3. Press Enter to go back to State 2")
        if newFrame:
            # Set up Main Window Layout for Stage 3
            imgMain = imgIn.copy()    
            # overlap ROI over imgIn before displaying
            cv2.addWeighted( imgMain, 0.8, imgROIDraw, 0.2, 0.0, imgROIonImgIn )
            cv2.imshow('imgROIDraw',imgROIDraw)
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
            prevState = nowState; nowState = nextState; nextState = 0
           
    if nowState == 9:
        print("Main.9: entered State 9. Exiting loop ... ")
        # do any necessary house keeping here before quiting loop (if any)
        break;
        
        
        
# stop all threads and closing all windows 
webcamStream.stop()
cv2.destroyAllWindows()