# Python program to open the 
# camera in Tkinter 
# Import the libraries, 
# tkinter, cv2, Image and ImageTk 

from tkinter import *
import cv2 
import PIL as pillow
from PIL import Image, ImageTk 
import time
import numpy as np

# Define a video capture object 
vid = cv2.VideoCapture(0) 

#declare w h
w = 1280.0/4
h = 720.0/4
# Try to set capture to desired (w,h)
print("setting resolution", w, h)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

# Retrieve actual size (w,h)
w = int( vid.get(cv2.CAP_PROP_FRAME_WIDTH)  /2)
h = int( vid.get(cv2.CAP_PROP_FRAME_HEIGHT) /2)
print("final resolution", w, h)

time.sleep(2)

imgRef = np.zeros((h, w, 3), dtype = "uint8")

# Create a GUI app 
app = Tk() 

# Bind the app with Escape keyboard to 
# quit app whenever pressed 
app.bind('<Escape>', lambda e: app.quit()) 
app.bind('a', lambda e: dupe())

# Create a label and display it on app 
label_widget = Label(app)
label_widget.pack()
# Create a function to open camera and 
# display it in the label_widget on app 

imgBackground = cv2.imread('Untitled.png')
imgBackground = cv2.resize(imgBackground, (w, h), interpolation=cv2.INTER_AREA)
cv2.imshow('imgBackground',imgBackground) 

# From : https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/
# define a function for vertically 
# concatenating images of the 
# same size  and horizontally
def concat_vh(list_2d):
    
      # return final image
    return cv2.vconcat([cv2.hconcat(list_h) 
                        for list_h in list_2d])

def open_camera(imgRef): 
  
    # Capture the video frame by frame  
    ret, frame = vid.read()    

    global imgIn
    imgIn = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
    
    if ret: 
        #cv2.imshow('frame',frame)
        
        imgIn = cv2.resize(imgIn, (w, h), interpolation=cv2.INTER_AREA)

        imgGray = cv2.cvtColor(imgIn, cv2.COLOR_BGR2GRAY)    
        imgGray = cv2.cvtColor(imgGray, cv2.COLOR_GRAY2BGR) # convert back to 3 channels
        #cv2.imshow('imgGray',imgGray)    
        
        imgDiff = cv2.absdiff(imgIn,imgRef) # (imgIn.copy() - imgRef.copy()) #np.absolute
        #diff = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR) 
        
        threshold = 50
        #result = np.mean(result,2) # axis = 2
        imgMask = np.where(np.max(imgDiff,axis = 2) > threshold, 1, 0)
        #result = cv2.cvtColor( result, cv2.COLOR_GRAY2BGR) 
        # print("result.shape = ", result.shape)
        #         
        imgMask3 = cv2.cvtColor(imgMask.astype(np.uint8), cv2.COLOR_GRAY2BGR).astype(np.uint8)
        #imgComp = imgIn * (cv2.cvtColor(imgMask, cv2.COLOR_GRAY2BGR).astype(np.uint8))
        #cv2.imshow("imgComp",imgComp.astype(np.uint8))
                
    
        #imgMask = cv2.cvtColor( (result*255).astype(np.uint8), cv2.COLOR_GRAY2BGR) # convert back to 3 channels                

        # Layout and Display Output Windows    
        imgLayout = concat_vh( [[imgIn, imgGray],
                                [imgRef, imgIn]])
        


    # Capture the latest frame and transform to image 
    captured_image = Image.fromarray(imgLayout) 
  
    # Convert captured image to photoimage 
    photo_image = ImageTk.PhotoImage(image=captured_image) 
  
    # Displaying photoimage in the label 
    label_widget.photo_image = photo_image 
  
    # Configure image in the label 
    label_widget.configure(image=photo_image) 

    print("loop")
  
    # Repeat the same process after every 10 seconds 
    label_widget.after(10, lambda: open_camera(imgRef)) 

def dupe():
    global imgIn, imgRef
    imgRef=imgIn.copy()
    open_camera(imgRef)
    print("screaming")


# Create a button to open the camera in GUI app 
camopen = Button(app, text="Open Camera", command=lambda: open_camera(imgRef))
camopen.pack()

capturebg = Button(app, text="Capture Background")
capturebg.pack()


# Create an infinite loop for displaying app on screen 
app.mainloop() 
