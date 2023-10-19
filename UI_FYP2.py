from tkinter import *
import cv2 
import PIL as pillow
from PIL import Image, ImageTk 
from functools import partial


# Window
tkWindow = Tk()  
tkWindow.geometry('400x150')  
tkWindow.title('Authentication Required')

# Define a video capture object 
vid = cv2.VideoCapture(0) 

# Declare the width and height in variables 
width, height = 800, 600

# Set the width and height 
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width) 
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height) 

# Empty Space
SpaceTop = Label(tkWindow, text="                              ").grid(row=3, column=0)
SpaceTop.pack()

# Username label and text entry box
usernameLabel = Label(tkWindow, text="User Name").grid(row=4, column=1)
username = StringVar()
usernameEntry = Entry(tkWindow, textvariable=username).grid(row=4, column=2)  

# Password label and password entry box
passwordLabel = Label(tkWindow,text="Password").grid(row=5, column=1)  
password = StringVar()
passwordEntry = Entry(tkWindow, textvariable=password, show='*').grid(row=5, column=2)  

def validateLogin():
  # Capture the video frame by frame 
  _, frame = vid.read() 

  # Convert image from one color space to other 
  opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 

  # Capture the latest frame and transform to image 
  captured_image = Image.fromarray(opencv_image) 

  # Convert captured image to photoimage 
  photo_image = ImageTk.PhotoImage(image=captured_image) 

  # Displaying photoimage in the label 
  SpaceTop.photo_image = photo_image 

  # Configure image in the label 
  SpaceTop.configure(image=photo_image) 

  # Repeat the same process after every 10 seconds 
  SpaceTop.after(10, validateLogin) 

#whats this here for ?????????????????????????????????????????????
validateLogin = partial(validateLogin, username, password)

# Empty Space
SpaceBottom = Label(tkWindow, text="  ").grid(row=5, column=3)

# Login button
loginButton = Button(tkWindow, text="Login", command=validateLogin).grid(row=5, column=4)  

#infinite loop to keep displaying
tkWindow.mainloop()