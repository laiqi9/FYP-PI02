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

mainTitle = "Security Systems v0.0"
mouseX = 0; mouseY = 0
mouseDown = False
mouseUp = False

def onMouseButton(event, x, y, flags, param):
    
    global mouseX, mouseY, mouseDown, mouseUp 
    
    if event == cv2.EVENT_LBUTTONDOWN:
        print("onMouseButton: Mouse Down...")
        mouseX = x; mouseY = y; mouseDown = True;  mouseUp = False;  
    
    if event == cv2.EVENT_LBUTTONUP:
        print("onMouseButton: Mouse Up...")
        mouseX = x; mouseY = y; mouseDown = False;  mouseUp = True;  

          
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
imgRef = np.zeros((h, w, 3), dtype = "uint8")   # blank images
imgMain = np.zeros((h*2, w*2, 3), dtype = "uint8")
imgInLarge = np.zeros((h*2, w*2, 3), dtype = "uint8")

# Main Loop
prevState = 0
nowState  = 1 
nextState = 2 # -1 is reserved or non-changing states

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
        imgInLarge = frame.copy()
        imgIn = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
        imgOut = imgIn.copy() 
        
        newFrame = True
        
        cv2.imshow('imgIn',imgIn)
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

        if newFrame:
            # Layout and Display Results in One Window
            imgMain = concat_vh( [[imgIn, imgIn],
                                  [imgRef, imgOut]]) 
            cv2.imshow(mainTitle, imgMain)
        
        # Process users inputs 
        if (key & 0xFF == ord('f')): imgRef = imgIn.copy() 
    
        # At this moment, do nothing. 
        if (mouseDown):
            print("Main: mouseDown at " + str(mouseX) + ", " + str(mouseY) ); 
            nextState= 3
            mouseDown = False;
    
        if (mouseUp):
            print("Main: mouseDown at " + str(mouseX) + ", " + str(mouseY) )        
            mouseUp = False;

        # Go to state 9
        if (False): # ToDo: set appropriate conditions here for changing state 
            nextState = 9
        if (nextState != 0):
           prevState = nowState; nowState = nextState; nextState = 0

    if nowState == 3:
        print("Main.3: entering state 3")
        if newFrame:
            # Layout and Display Results in One Window
            imgMain =  imgInLarge
            cv2.imshow(mainTitle, imgMain)
            
        # Process users inputs 
        if (key & 0xFF == 13):  # Enter = 13
            nextState = 2

        if (nextState != 0):
           prevState = nowState; nowState = nextState; nextState = 0
        


    if nowState == 9:
        print("Main: entered State 3. Exiting loop ... ")
        # do any necessary house keeping here before quiting loop (if any)
        break;
        
        

        
# stop all threads and closing all windows 
webcamStream.stop()
cv2.destroyAllWindows()