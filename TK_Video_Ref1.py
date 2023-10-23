from tkinter import * #gui
import cv2 #opencv_python
from PIL import Image, ImageTk #put the image into tkinter
import time #wait
import numpy as np #np.zeros

# Setup Camera Capture:
# 1. Internal Webcam    
#cap = cv2.VideoCapture(0) # Internal Webcam
# 2. if you are using IP camera
#cap = cv2.VideoCapture("rtsp://admin:admin@192.168.0.102:554/11") 
vid = cv2.VideoCapture(0) 

# Declare the width and height in variables 
width, height = 800, 600

# Set the width and height 
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width) 
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height) 

# Create the window
app = Tk()

# Bind the app with Escape keyboard to 
#one version of key bind, quit when escape
app.bind('<Escape>', lambda e: app.quit()) 

# Create a label and display it on app, empty to start
label_widget = Label(app) 
label_widget.pack() 

# Create a function to open camera and 
# display it in the label_widget on app 
def open_camera(): 
  
    # Capture the video frame by frame 
    _, frame = vid.read() 
  
   #image processing here, MUST BGR2RGB
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Capture the latest frame and transform to image 
    captured_image = Image.fromarray(opencv_image) 
  
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
