import tkinter
import cv2
import time
from PIL import Image, ImageTk
import numpy as np
 
class App:
  #__init__ runs once upon startup
  def __init__(self, window, window_title, video_source=0):
    self.window = window
    self.window.title(window_title)

    #open video source, declare as self.vid
    self.vid = MyVideoCapture(video_source)
    
    #create a canvas that can fit the video source size
    self.canvas = tkinter.Canvas(window, width = self.vid.width*2, height=self.vid.height*2)
    self.canvas.pack()
    self.canvas.bind( "<B1-Motion>", self.paint )

    #create interactive buttons for user
    #  side = tkinter.TOP BOTTOM LEFT RIGHT
    #  anchor = tkinter. N E S W NE NW...
    self.btn_snapshot=tkinter.Button(window, text="snapshot", width=20, command=self.vid.snapshot)
    self.btn_snapshot.pack(side=tkinter.RIGHT, anchor=tkinter.NE)

    self.btn_snapshot=tkinter.Button(window, text="Clear Mask", width=20, command=self.clearmask)
    self.btn_snapshot.pack(side=tkinter.LEFT, anchor=tkinter.NW)
    
    #sliding scale
    #  orient=tkinter.HORIZONTAL for horizontal scale
    #  from_= lowest, to= highest
    scale = tkinter.Scale(window, variable=self.vid.threshold, orient=tkinter.HORIZONTAL, from_=1, to=50, command=self.sel)
    scale.pack(side=tkinter.TOP, anchor=tkinter.N)

    #after called once, update auto called
    self.delay = 15
    self.update()

    #keep the window open
    self.window.mainloop()

  #set vid threshold from scale
  #here because connected to button
  def sel(self, val):
    self.vid.threshold=int(val)
    print(self.vid.threshold)

  #draw recatngles on vid.imgMask for overlay drawing
  #here because connected to button
  def paint(self, event):
   mousePt=(event.x, event.y)
   pt1 = tuple(map(lambda x, y: x - y, mousePt, (10,10))) # ie. pt1 = mousePt - (10,10)
   pt2 = tuple(map(lambda x, y: x + y, mousePt, (10,10))) # ie. pt2 = mousePt + (10,10)
   self.vid.imgMask=cv2.rectangle(self.vid.imgMask, pt1, pt2, (255, 255, 255), -1)
 
  #rest the drawing to black
  def clearmask(self):
    self.vid.imgMask.fill(0)

  #keep running and displaying video
  def update(self):
    ret, frame = self.vid.get_frame()

    if ret:
      self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
      self.canvas.create_image(0, 0, image=self.photo, ancho=tkinter.NW)
    
    self.window.after(self.delay, self.update)

#video capture and processing
class MyVideoCapture:
  #runs once upon startup
  def __init__(self, video_source=0):
    # Open the video source
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)    

    w=1280.0/4
    h=720.0/4
    self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    print("res set: ", w, h)


    # Get video source width and height
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("final res: ", self.width, self.height)

    #set images as all black
    self.imgRef = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")
    self.imgComposite = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")   # blank images
    self.imgTemp1 = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")
    self.imgBackground = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")
    self.imgPrev = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")   # blank images
    self.imgAve = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")   # blank images
    self.imgContours1 = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")   # blank images
    self.imgContours2 = np.zeros((int(self.height), int(self.width), 3), dtype = "uint8")   # blank images
    self.imgMask3 = np.zeros((int(self.height), int(self.width), 1), dtype = "uint8")   # blank images

    #Copy a image of snapshot for reference
    self.imgMask = self.imgRef.copy()

    # Other Variable
    self.threshold = 20
  
  #take a snapshot and set to imgRef
  def snapshot(self):
    ret, frame = self.vid.read()
    self.imgRef=frame.copy()
    self.imgRef = cv2.cvtColor(self.imgRef, cv2.COLOR_BGR2RGB) 
    self.imgRef = cv2.resize(self.imgRef, (int(self.width), int(self.height)), interpolation=cv2.INTER_AREA)
    return self.imgRef
  
  #run upon destruction of object
  def __del__(self):
    # Release the video source when the object is destroyed
    if self.vid.isOpened():
      self.vid.release()
      cv2.destroyAllWindows()
      print("Stream ended")
  
  #put video squares together
  def concat_vh(self, list_2d):
    # return final image
    return cv2.vconcat([cv2.hconcat(list_h) for list_h in list_2d])

  # Main loop
  def get_frame(self):
     if self.vid.isOpened():

       ret, frame = self.vid.read()

       h, w = frame.shape[:2]

       if ret: #image processing here
        imgIn = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 

        imgIn = cv2.resize(imgIn, (w, h), interpolation=cv2.INTER_AREA)
        
        K = 0.05
        cv2.addWeighted( imgIn, K, self.imgAve, (1-K), K, self.imgAve);    
        
        imgDiff = cv2.absdiff(imgIn,self.imgRef) 
        
        # create mask from imgDiff
        imgDiff = cv2.absdiff(imgIn,self.imgRef) 
        imgDiff = np.max(imgDiff, axis = 2)
        ret, imgMask = cv2.threshold(imgDiff,self.threshold,255,cv2.THRESH_BINARY)
        
        # Process Mask using Dilate-Erode
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        img_erosion = cv2.erode(imgMask, kernel, iterations=1)
        img_dilation = cv2.dilate(img_erosion, kernel, iterations=2)
        img_erosion = cv2.erode(img_dilation, kernel, iterations=1)
        imgMask2 = img_erosion
        
        # Process Mask using Contours
        threshold_area = 50
        contours, hierarchy = cv2.findContours(image=imgMask2, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    
        imgContours1 = imgIn.copy()
        cv2.drawContours(imgContours1,contours,-1,(0,255,255),1)
        
        #imgResult = imgInSmall.copy()
        self.imgContours2[:] = 0 # reset image to zero
        self.imgMask3[:] = 0     # reset image to zero
        
        selectContours = []  # select and copy items into list to avoid 
                             #  deleting element from a list while looping on it
        for c in contours: 
            rect = cv2.minAreaRect(c)  
            (xR, yR), (wR, hR), angle = rect
            area = cv2.contourArea(c)         
            if ((area > threshold_area) and (wR > 5) and (hR > 5)):                   
                 selectContours.append(c)
                 
        for c in selectContours:
            #rect = cv2.minAreaRect(c)     
            #box = cv2.boxPoints(rect)
            #box = np.int0(box)            
            #cv2.drawContours(imgContours2,[box],0,(0,0,255),2)
            cv2.drawContours(self.imgContours2, [c], 0, (0,0,255), 1)
            xc,yc,wc,hc = cv2.boundingRect(c)
            cv2.rectangle(self.imgContours2,(xc,yc),(xc+wc,yc+hc),(0,255,255),2)
            cv2.drawContours(self.imgMask3, [c], 0, 255, -1)        
        
        # Cut out foreground object from imgIn using mask
        imgOut = cv2.bitwise_and(imgIn, imgIn, mask = self.imgMask3)
        
        # Layout and Display Results in One Window
        imgResults= self.concat_vh( [[imgIn, self.imgAve],
                                [self.imgRef, imgOut]]) 
        return (ret, imgResults)
       else:
        return (ret, None)
     else:
      return (ret, None)

# Create a window and pass it to the Application object
App(tkinter.Tk(), "TK_Video_Ref5a")