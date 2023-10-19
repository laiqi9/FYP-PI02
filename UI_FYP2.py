from tkinter import *
import cv2 
import PIL as pillow
from PIL import Image, ImageTk 
from functools import partial


# Window
tkWindow = Tk()  
tkWindow.geometry('400x150')  
tkWindow.title('Authentication Required')


def validateLogin(username, password):
	if (username=='admin') and (password =='admin'):
            
		# Capture the video frame by frame 
    _, frame = vid.read() 
  
    # Convert image from one color space to other 
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
  
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

# Empty Space
SpaceTop = Label(tkWindow, text="                              ").grid(row=3, column=0)

# Username label and text entry box
usernameLabel = Label(tkWindow, text="User Name").grid(row=4, column=1)
username = StringVar()
usernameEntry = Entry(tkWindow, textvariable=username).grid(row=4, column=2)  

# Password label and password entry box
passwordLabel = Label(tkWindow,text="Password").grid(row=5, column=1)  
password = StringVar()
passwordEntry = Entry(tkWindow, textvariable=password, show='*').grid(row=5, column=2)  

validateLogin = partial(validateLogin, username, password)

# Empty Space
SpaceBottom = Label(tkWindow, text="  ").grid(row=5, column=3)

# Login button
loginButton = Button(tkWindow, text="Login", command=validateLogin).grid(row=5, column=4)  

tkWindow.mainloop()

# Create an infinite loop for displaying app on screen 
app.mainloop() 