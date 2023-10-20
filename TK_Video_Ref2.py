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
w = 1280.0/2 
h = 720.0/2
# Try to set capture to desired (w,h)
print("setting resolution", w, h)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

# Retrieve actual size (w,h)
w = int( vid.get(cv2.CAP_PROP_FRAME_WIDTH)  /2)
h = int( vid.get(cv2.CAP_PROP_FRAME_HEIGHT) /2)
print("final resolution", w, h)

time.sleep(2)

# Create a GUI app 
app = Tk() 

# Bind the app with Escape keyboard to 
# quit app whenever pressed 
app.bind('<Escape>', lambda e: app.quit()) 

# Create a label and display it on app 
label_widget = Label(app) 
label_widget.pack() 

# Create a function to open camera and 
# display it in the label_widget on app 



def open_camera(): 
  
    # Capture the video frame by frame 
    _, frame = vid.read() 
  
    ret, frame = vid.read()    
    if ret:
        #cv2.imshow('frame',frame)
        imgIn = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)

        #imgOut = imgIn * (0, 1, 1.25)
        imgOut =  cv2.Canny(imgIn, 100, 100)
            
        imgOut = np.clip(imgOut, 0.0, 255.0).astype(np.uint8)

    # Capture the latest frame and transform to image 
    captured_image = Image.fromarray(imgOut) 
  
    # Convert captured image to photoimage 
    photo_image = ImageTk.PhotoImage(image=captured_image) 
  
    # Displaying photoimage in the label 
    label_widget.photo_image = photo_image 
  
    # Configure image in the label 
    label_widget.configure(image=photo_image) 
  
    # Repeat the same process after every 10 seconds 
    label_widget.after(10, open_camera) 


# Create a button to open the camera in GUI app 
button1 = Button(app, text="Open Camera", command=open_camera) 
button1.pack() 


# Create an infinite loop for displaying app on screen 
app.mainloop() 
