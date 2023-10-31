import tkinter
import cv2
import time
from PIL import Image, ImageTk
import numpy as np
 
class App:
  def __init__(self, window, window_title, video_source=0):
    self.window = window
    self.window.title(window_title)

    #open video source
    self.vid = MyVideoCapture(video_source)
    
    #create a canvas that can fit the video source size
    self.canvas = tkinter.Canvas(window, width = self.vid.width*2, height=self.vid.height*2)
    self.canvas.pack()
    self.canvas.bind( "<B1-Motion>", self.paint )

    self.btn_snapshot=tkinter.Button(window, text="snapshot", width=50, command=self.vid.snapshot)
    self.btn_snapshot.pack(anchor=tkinter.NE, expand=True)

    #after called once, update auto called
    self.delay = 15
    self.update()

    self.window.mainloop()

  def paint(self, event):
   python_green = "#476042"
   x1, y1 = ( event.x - 1 ), ( event.y - 1 )
   x2, y2 = ( event.x + 1 ), ( event.y + 1 )
   mousePt=(event.x, event.y)
   pt1 = tuple(map(lambda x, y: x - y, mousePt, (10,10))) # ie. pt1 = mousePt - (10,10)
   pt2 = tuple(map(lambda x, y: x + y, mousePt, (10,10))) # ie. pt2 = mousePt + (10,10)
   self.vid.imgMask=cv2.rectangle(self.vid.imgMask, pt1, pt2, (255, 255, 255), -1)

   print("ow")

  def update(self):
    ret, frame = self.vid.get_frame()

    if ret:
      self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
      self.canvas.create_image(0, 0, image=self.photo, ancho=tkinter.NW)
    
    self.window.after(self.delay, self.update)

class MyVideoCapture:
  def __init__(self, video_source=0):
    # Open the video source
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
    
    self.mousePt = (0,0)
    self.mouseDown = False
    
    w=1280.0/4
    h=720.0/4
    self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    print("res set: ", w, h)


    # Get video source width and height
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("final res: ", self.width, self.height)

    self.imgRef = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")
    self.imgComposite = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")   # blank images
    self.imgTemp1 = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")

    self.imgBackground = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")

    #Copy a image of snapshot for reference
    self.imgMask = self.imgRef.copy()

  def snapshot(self):
    ret, frame = self.vid.read()
    self.imgRef=frame.copy()
    self.imgRef = cv2.cvtColor(self.imgRef, cv2.COLOR_BGR2RGB) 
    return self.imgRef
  
  def __del__(self):
    # Release the video source when the object is destroyed
    if self.vid.isOpened():
      self.vid.release()
      cv2.destroyAllWindows()
      print("Stream ended")
  
  def concat_vh(self, list_2d):
    # return final image
    return cv2.vconcat([cv2.hconcat(list_h) for list_h in list_2d])

  def get_frame(self):
     if self.vid.isOpened():
       ret, frame = self.vid.read()

       h, w = frame.shape[:2]

       if ret: 
        imgIn = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 

        imgIn = cv2.resize(imgIn, (w, h), interpolation=cv2.INTER_AREA)   
        
        imgOut = imgIn.copy()
        
        self.imgTemp1 = self.imgMask.copy()   
        self.imgTemp1[:,:,0] = 0  # create a copy of mask in yellow by setting blue = 0  
        cv2.addWeighted( imgIn, 0.5, self.imgTemp1, 0.5, 0.0, self.imgTemp1 )
        cv2.imshow('imgTemp1',self.imgTemp1) 
        
        imgOut = cv2.bitwise_and( imgIn, cv2.bitwise_not(self.imgMask) )  +  cv2.bitwise_and(self.imgTemp1, self.imgMask) 
        cv2.imshow('imgOut',imgOut) 
        
        cv2.imshow('imgOut',imgOut)   
        cv2.imshow('imgMask',self.imgMask)   


        # Layout and Display Results in One Window
        imgResults= self.concat_vh( [[imgIn, imgIn],
                                [self.imgRef, self.imgBackground], 
                                [imgIn, imgOut]]) 
        cv2.imshow("Results", imgResults)

        return (ret, imgResults)
       else:
        return (ret, None)
     else:
      return (ret, None)

# Create a window and pass it to the Application object
App(tkinter.Tk(), "TK_Video_Ref4.2a")