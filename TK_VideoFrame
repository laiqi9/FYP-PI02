import tkinter
import cv2
import time
import sys
from PIL import Image, ImageTk
from pathlib import Path
path_root=Path(__file__).parents[2]
sys.path.append(str(path_root))
from TK_VideoCapture import MyVideoCapture


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