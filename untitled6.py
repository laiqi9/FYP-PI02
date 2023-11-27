import cv2
import time
from PIL import Image, ImageTk
import numpy as np
import requests
import tkinter

import Final_Work6v3copy as fw


'''
quadrant map
+----+----+
|  1 |  2 | 
+----+----+
|  3 |  4 | 
+----+----+

'''


class App:
    # __init__ runs once upon startup
    def __init__(self, window, window_title, video_source=1):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1300x750")

        self.vids = []

        # open video source, declare as self.vid
        self.vids.append(MyVideoCapture(video_source, 1))
        self.vids.append(MyVideoCapture(video_source, 2))
        self.vids.append(MyVideoCapture(video_source, 3))
        self.vids.append(MyVideoCapture(video_source, 4))

        # create a canvas that can fit the video source size
        self.canvas = tkinter.Canvas(window, width=1280, height=720)
        self.canvas.pack()

        self.canvas.bind('<Motion>', self.mouseMove)
        self.canvas.bind('<Button-1>', self.mouseClick)

        # create interactive buttons for user
        #  side = tkinter.TOP BOTTOM LEFT RIGHT
        #  anchor = tkinter. N E S W NE NW...
        '''
    self.btn_snapshot=tkinter.Button(window, text="snapshot", width=20, command=self.vid.snapshot)
    self.btn_snapshot.pack(side=tkinter.RIGHT, anchor=tkinter.NE)

    self.btn_snapshot=tkinter.Button(window, text="Clear Mask", width=20, command=self.clearmask)
    self.btn_snapshot.pack(side=tkinter.LEFT, anchor=tkinter.NW)
    
    #sliding scale
    #  orient=tkinter.HORIZONTAL for horizontal scale
    #  from_= lowest, to= highest
    scale = tkinter.Scale(window, variable=self.vid.threshold, orient=tkinter.HORIZONTAL, from_=1, to=50, command=self.sel)
    scale.pack(side=tkinter.TOP, anchor=tkinter.N)
    '''

        # after called once, update auto called
        self.delay = 100
        self.update()

        # keep the window open
        self.window.mainloop()

    def mouseMove(self, e):
        x = e.x
        y = e.y
        print("Mouse: ", x, y)

        # if x<

    # make onMouseButton obselete in fw
    def mouseClick(self, e):
        x = e.x
        y = e.y
        print("Clicked at: ", x, y)

        if (x < (1280/2) and y < (720/2)):
            # quad 1
            print("quad 1")
        elif(x > (1280/2) and y < (720/2)):
            # quad 2
            print("quad 2")
        elif(x < (1280/2) and y > (720/2)):
            # quad 3
            print("quad 3")
        else:
            # quad 4
            print("quad 4")

    # keep running and displaying video
    def update(self):
        
        ret0, frame0 = self.vids[0].get_frame()
        self.photo0 = ImageTk.PhotoImage(image=Image.fromarray(frame0))
        self.canvas.create_image(0, 0, image=self.photo0, ancho=tkinter.NW)
        
        ret1, frame1 = self.vids[1].get_frame()
        self.photo1 = ImageTk.PhotoImage(image=Image.fromarray(frame1))
        self.canvas.create_image(1280.0/2, 0, image=self.photo1, ancho=tkinter.NW)
        
        ret2, frame2 = self.vids[2].get_frame()
        self.photo2 = ImageTk.PhotoImage(image=Image.fromarray(frame2))
        self.canvas.create_image(0, 720.0/2, image=self.photo2, ancho=tkinter.NW)
        
        ret3, frame3 = self.vids[3].get_frame()
        self.photo3 = ImageTk.PhotoImage(image=Image.fromarray(frame3))
        self.canvas.create_image(1280.0/2, 720.0/2, image=self.photo3, ancho=tkinter.NW)
        
        self.window.after(self.delay, self.update)


'''
  #set vid threshold from scale
  #here because connected to button
  def sel(self, val):
    self.vid.threshold=int(val)
    print(self.vid.threshold)

  #draw rectangles on vid.imgMask for overlay drawing
  #here because connected to button
  def paint(self, event):
   mousePt=(event.x, event.y)
   pt1 = tuple(map(lambda x, y: x - y, mousePt, (10,10))) # ie. pt1 = mousePt - (10,10)
   pt2 = tuple(map(lambda x, y: x + y, mousePt, (10,10))) # ie. pt2 = mousePt + (10,10)
   self.vid.imgMask=cv2.rectangle(self.vid.imgMask, pt1, pt2, (255, 255, 255), -1)
 
  #reset the drawing to black
  def clearmask(self):
    self.vid.imgMask.fill(0)
'''

# video capture and processing


class MyVideoCapture:
    # runs once upon startup
    def __init__(self, video_source, quad_num):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source ", quad_num)

        w = 1280.0/2
        h = 720.0/2
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        print("res set: ", w, h)

        self.quad_num = quad_num

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print("final res: ", self.width, self.height)

        # Other Variable
        self.threshold = 20
        
        self.imgOut = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")
        self.imgIn = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")

    # take a snapshot and set to imgRef
    '''
  def snapshot(self):
    ret, frame = self.vid.read()
    self.imgRef = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")

    #Copy a image of snapshot for reference
    self.imgMask = self.imgRef.copy()

    self.imgRef = cv2.resize(self.imgRef, (int(self.width), int(self.height)), interpolation=cv2.INTER_AREA)
    return self.imgRef
'''

    # run upon destruction of object
    def __del__(self):
        # Release the video source when the object is destroyed
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()
            print("Stream ended")

    # Main loop
    def get_frame(self):
        if self.vid.isOpened():

            ret, frame = self.vid.read()

            h, w = frame.shape[:2]

            if ret:  # image processing here

                if self.quad_num == 1:  # quad 1
                    x_coord = 0
                    y_coord = 0
                    self.imgIn = fw.Quadrant(
                        self.quad_num, x_coord, y_coord, fw.imgTemp, fw.imgMask)
                elif self.quad_num == 2:  # quad 2
                    x_coord = 1280.0/2
                    y_coord = 0
                    self.imgIn = fw.Quadrant(
                        self.quad_num, x_coord, y_coord, fw.imgTemp2, fw.imgMask2)
                elif self.quad_num == 3:  # quad 3
                    x_coord = 0
                    y_coord = 720.0/2
                    self.imgIn = fw.Quadrant(
                        self.quad_num, x_coord, y_coord, fw.imgTemp3, fw.imgMask3)
                else:  # quad 4
                    x_coord = 1280.0/2
                    y_coord = 720.0/2
                    self.imgIn = fw.Quadrant(
                        self.quad_num, x_coord, y_coord, fw.imgTemp4, fw.imgMask4)
                
                self.imgOut=self.imgIn.Extract_Quadrant()
                self.imgOut=cv2.cvtColor(self.imgOut, cv2.COLOR_BGR2RGB) 

                return (ret, self.imgOut)
            else:
                return (ret, None)
        else:
            return (ret, None)


# Create a window and pass it to the Application object
App(tkinter.Tk(), "FYP")
