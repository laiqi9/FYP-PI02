import tkinter
import cv2
import time
from PIL import Image, ImageTk
import numpy as np


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)

        # open video source
        self.vid = MyVideoCapture(video_source)

        # create a canvas that can fit the video source size
        self.canvas = tkinter.Canvas(
            window, width=self.vid.width*2, height=self.vid.height*2)
        self.canvas.pack()

        self.btn_snapshot = tkinter.Button(
            window, text="snapshot", width=50, command=self.vid.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        self.btn_toggle = tkinter.Button(
            window, text="Toggle", width=50, relief="raised", command=self.toggle)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
        self.btn_toggle2 = tkinter.Button(
            window, text="Toggle2", width=50, relief="raised", command=self.toggle2)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        # after called once, update auto called
        self.delay = 15
        self.update()

        self.window.mainloop()

    def toggle(self):
        if buttonOn:
            self.btn_toggle.config(relief="sunken")
            buttonOn = False
            self.toggle2()
        else:
            self.btn_toggle.config(relief="raised")
            buttonOn = True

    def toggle2(self):
        if buttonOn:
            self.btn_toggle2.config(relief="sunken")
            buttonOn = False
            self.toggle()
        else:
            self.btn_toggle2.config(relief="raised")
            buttonOn = True

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

        w = 1280.0/4
        h = 720.0/4
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        print("res set: ", w, h)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print("final res: ", self.width, self.height)

        self.imgRef = np.zeros(
            (int(self.height), int(self.width), 3), dtype="uint8")
        self.imgBackground = cv2.imread("Untitled.png")
        self.imgBackground = cv2.resize(self.imgBackground, (int(
            self.width), int(self.height)), interpolation=cv2.INTER_AREA)

    def snapshot(self):
        ret, frame = self.vid.read()
        self.imgRef = frame.copy()
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

                imgOut = 255 - imgIn.copy()

                # Layout and Display Results in One Window
                imgResults = self.concat_vh([[imgIn, imgIn],
                                             [self.imgRef, self.imgBackground],
                                             [imgIn, imgOut]])

                return (ret, imgResults)
            else:
                return (ret, None)
        else:
            return (ret, None)


# Create a window and pass it to the Application object
App(tkinter.Tk(), "TK_Video_Ref4a")
