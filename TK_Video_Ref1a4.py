import tkinter
import cv2
import time
from PIL import Image, ImageTk
 
class App:
  def __init__(self, window, window_title, ):
    self.window = window
    self.window.title(window_title)

    #open video source
    self.vid = MyVideoCapture(0)
    self.vid1 = MyVideoCapture(1)
    
    #create a canvas that can fit the video source size
    self.canvas = tkinter.Canvas(window, width = self.vid.width, height=self.vid.height)
    self.canvas.pack()

    self.btn_snapshot=tkinter.Button(window, text="snapshot", width=20, command=self.snapshot)
    self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

    #after called once, update auto called
    self.delay = 15
    self.update()

    self.window.mainloop()

  def snapshot(self):
    ret, frame = self.vid.get_frame()

  def update(self):
    ret, frame = self.vid.get_frame()

    if ret:
      self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
      self.canvas.create_image(0, 0, image=self.photo, ancho=tkinter.NW)
    
    self.window.after(self.delay, self.update)

class MyVideoCapture:
  def __init__(self, video_source):
    # Open the video source
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)

    # Get video source width and height
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

   # Release the video source when the object is destroyed
  def __del__(self):
    if self.vid.isOpened():
      self.vid.release()
      cv2.destroyAllWindows()
      print("Stream ended")
      
  def get_frame(self):
     if self.vid.isOpened():
       ret, frame = self.vid.read()
       if ret:
         # Return a boolean success flag and the current frame converted to BGR
         return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
       else:
         return (ret, None)
     else:
      return (ret, None)

# Create a window and pass it to the Application object
App(tkinter.Tk(), "TK_Video_Ref1a")