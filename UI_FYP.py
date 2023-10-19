import tkinter as tk 
from tkinter import *
import PIL as pillow
from PIL import Image, ImageTk 

window =tk.Tk()

#Login Page
loginaccess = tk.Tk()
def get_data():
  Label.config(text= loggedin.get())

def Password(window , unlock_message , access_camera):    

    activate_message = "SYSTEM ACTIVATED"
    denied_message = "ACCESS DENIED"


password = 'password'
loggedin = (password =='password')

login=tk.Entry(width=20)
button = tk.Button(
    text="Enter",
    width=5,
    height=1,
    bg="White",
    fg="Black",
)

password=tk.Entry(width=20)
if loggedin: 
  window.title("Error")
  window.geometry('640x480')
else:
  window.title("Security System")
  window.geometry('960x540')
  window.config(bg = 'White')

login.pack()
button.pack()
window.mainloop() 