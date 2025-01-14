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

    self.btn_snapshot=tkinter.Button(window, text="snapshot", width=50, command=self.vid.snapshot)
    self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

    #after called once, update auto called
    self.delay = 15
    self.update()

    self.window.mainloop()

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
    

   # Release the video source when the object is destroyed

  def snapshot(self):
    ret, frame = self.vid.read()
    self.imgRef=frame.copy()
    self.imgRef = cv2.cvtColor(self.imgRef, cv2.COLOR_BGR2RGB) 
    return self.imgRef
  
  def __del__(self):
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
       w=w 
       h=h

       if ret: 
        global imgRef
        #cv2.imshow('frame',frame)
        imgIn = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 

        imgIn = cv2.resize(imgIn, (w, h), interpolation=cv2.INTER_AREA)

        imgGray = cv2.cvtColor(imgIn, cv2.COLOR_BGR2GRAY)    
        imgGray = cv2.cvtColor(imgGray, cv2.COLOR_GRAY2BGR) # convert back to 3 channels
        #cv2.imshow('imgGray',imgGray)    
        
        imgDiff = cv2.absdiff(imgIn, self.imgRef) # (imgIn.copy() - imgRef.copy()) #np.absolute
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
        imgLayout = self.concat_vh( [[imgIn, imgGray],
                                     [self.imgRef, imgIn]])

        return (ret, imgLayout)
       else:
         return (ret, None)
     else:
      return (ret, None)

# Create a window and pass it to the Application object
App(tkinter.Tk(), "TK_Video_Ref2a")