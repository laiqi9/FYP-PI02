import tkinter
import cv2
import time
from PIL import Image, ImageTk
 
class App:
  def __init__(self, window, window_title, video_source1=0, video_source2=1):
    self.window = window
    self.window.title(window_title)

    #open video source
    self.vid = MyVideoCapture(video_source1, video_source2)
    
    #create a canvas that can fit the video source size
    self.canvas = tkinter.Canvas(window, width = self.vid.width, height=self.vid.height)
    self.canvas.pack()

    self.canvas2 = tkinter.Canvas(window, width = self.vid.width, height=self.vid.height)
    self.canvas2.pack()

    #after called once, update auto called
    self.delay = 15
    self.update()

    self.window.mainloop()

  def update(self):
    ret1, frame1, ret2, frame2 = self.vid.get_frame()

    if ret1 and ret2:
      self.photo1 = ImageTk.PhotoImage(image=Image.fromarray(frame1))
      self.canvas.create_image(0, 0, image=self.photo1, ancho=tkinter.NW)

      self.photo2 = ImageTk.PhotoImage(image=Image.fromarray(frame2))
      self.canvas.create_image(0, 0, image=self.photo2, ancho=tkinter.NE)
    
    self.window.after(self.delay, self.update)

class MyVideoCapture:
  def __init__(self, video_source1, video_source2):
    # Open the video source
    self.vid1 = cv2.VideoCapture(video_source1)
    self.vid2 = cv2.VideoCapture(video_source2)

    if not self.vid1.isOpened():
      raise ValueError("Unable to open video source", video_source1)

    # Get video source width and height
    self.width = self.vid1.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid1.get(cv2.CAP_PROP_FRAME_HEIGHT)

   # Release the video source when the object is destroyed
  def __del__(self):
    if self.vid1.isOpened():
      self.vid1.release()
      cv2.destroyAllWindows()
      print("Stream ended")
    if self.vid2.isOpened():
      self.vid2.release()
      cv2.destroyAllWindows()

  def get_frame(self):
     if self.vid1.isOpened()and self.vid2.isOpened():
       ret1, frame1 = self.vid1.read()
       ret2, frame2 = self.vid2.read()
       if ret1 and ret2:
         imgIn1 = cv2.resize(frame1, (int(self.width/2), int(self.height/2)))
         imgIn2 = cv2.resize(frame2, (int(self.width/2), int(self.height/2)))
         # Return a boolean success flag and the current frame converted to BGR
         
         return ret1, imgIn1, ret2, imgIn2
       else:
         return (ret1, None, ret2, None)
     else:
      return (ret1, None, ret2, None)
     
  def __del__(self):
    if self.vid1.isOpened():
      self.vid1.release()
    if self.vid2.isOpened():
      self.vid2.release()

# Create a window and pass it to the Application object
App(tkinter.Tk(), "TK_Video_Ref1a")