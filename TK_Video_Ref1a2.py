import tkinter
import PIL.Image
import PIL.ImageTk
import cv2

#ref from overnight

class App:
    def __init__(self, window, video_source1=0, video_source2=1):
        self.window = window
        self.window.title("KEC MEDIA PLAYER")
        self.video_source1 = video_source1
        self.video_source2 = video_source2
        self.photo1 = ""
        self.photo2 = ""

        # open video source
        self.vid1 = MyVideoCapture(self.video_source1, self.video_source2)

        # Create a canvas that can fit the above video source size
        self.canvas1 = tkinter.Canvas(window, width=500, height=500)
        self.canvas2 = tkinter.Canvas(window, width=500, height=500)
        self.canvas1.pack(padx=5, pady=10, side="left")
        self.canvas2.pack(padx=5, pady=60, side="left")

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret1, frame1, ret2, frame2 = self.vid1.get_frame

        if ret1 and ret2:
                self.photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame1))
                self.photo2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame2))
                self.canvas1.create_image(0, 0, image=self.photo1, anchor=tkinter.NW)
                self.canvas2.create_image(0, 0, image=self.photo2, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source1=0, video_source2=1):
        # Open the video source
        self.vid1 = cv2.VideoCapture(video_source1)
        self.vid2 = cv2.VideoCapture(video_source2)

        if not self.vid1.isOpened():
            raise ValueError("Unable to open video source", video_source1)

    @property
    def get_frame(self):
        ret1 = ""
        ret2 = ""
        if self.vid1.isOpened() and self.vid2.isOpened():
            ret1, frame1 = self.vid1.read()
            ret2, frame2 = self.vid2.read()
            frame1 = cv2.resize(frame1, (500, 500))
            frame2 = cv2.resize(frame2, (500, 500))
            if ret1 and ret2:
                # Return a boolean success flag and the current frame converted to BGR
                return ret1, cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB), ret2, cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            else:
                return ret1, None, ret2, None
        else:
            return ret1, None, ret2, None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid1.isOpened():
            self.vid1.release()
        if self.vid2.isOpened():
            self.vid2.release()


def callback():
    global v1,v2
    v1=E1.get()
    v2=E2.get()
    if v1 == "" or v2 == "":
        L3.pack()
        return
    initial.destroy()


v1 = ""
v2 = ""

initial = tkinter.Tk()

initial.mainloop()


# Create a window and pass it to the Application object
App(tkinter.Tk())