from tkinter import *
import tkinter.font as tkFont
root = Tk()

def Password(root , unlock_message , access_camera):    

    activate_message = "SYSTEM ACTIVATED"
    denied_message = "ACCESS DENIED"

    message_box = Label(root , text = "Passcode required to " + unlock_message + " system" , padx = 500 )
    message_box.grid(row = 0 , column = 0)

    input_box = Entry(root , show = "*" , width = 6 , font = ('Verdana' , 20) ).grid(row = 1 , column = 0)
    enter_password_button = Button(root , text = "Confirm"  , pady = 8).place(x=650, y=20)

    
root.geometry("1800x1100")
root.title("Vehicle app")
Password(root , "unlock" , True)

root.mainloop()