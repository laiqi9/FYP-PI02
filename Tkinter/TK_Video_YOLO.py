import tkinter
import cv2
import time
from PIL import Image, ImageTk
import numpy as np

# Load yolo
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)

        # open video source
        self.vid = MyVideoCapture(video_source)

        # create a canvas that can fit the video source size
        self.canvas = tkinter.Canvas(
            window, width=self.vid.width*2, height=self.vid.height*3)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.startpaint)
        self.canvas.bind("<ButtonRelease-1>", self.endpaint)

        self.btn_snapshot = tkinter.Button(
            window, text="snapshot", width=30, command=self.vid.snapshot)
        self.btn_snapshot.pack(
            side=tkinter.RIGHT, anchor=tkinter.NE, expand=True)

        self.btn_snapshot = tkinter.Button(
            window, text="Clear Mask", width=30, command=self.vid.clearmask)
        self.btn_snapshot.pack(
            side=tkinter.LEFT, anchor=tkinter.NW, expand=True)

        self.drawing = False

        # after called once, update auto called
        self.delay = 15
        self.update()

        self.window.mainloop()

    def startpaint(self, event):
        self.vid.iy, self.vid.ix, self.vid.endx, self.vid.endy

        print("AHHHHHHHHHHHHHHHHHHHHHHHHH", self.vid.ix,
              self.vid.iy, self.vid.endx, self.vid.endy)
        self.drawing = True
        self.vid.ix, self.vid.iy = (event.x, event.y)

    def endpaint(self, event):
        self.vid.endx, self.vid.endy

        print("ENDDDDDDDDDDDDDDDDDDDD", self.vid.endx, self.vid.endy)
        self.drawing = False
        self.vid.endx, self.vid.endy = (event.x, event.y)

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

        self.mousePt = (0, 0)
        self.mouseDown = False

        self.ix, self.iy, self.endx, self.endy = -1, -1, -1, -1

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
        self.imgComposite = np.zeros((int(self.height), int(
            self.width), 3), dtype="uint8")   # blank images
        self.imgTemp1 = np.zeros(
            (int(self.height), int(self.width), 3), dtype="uint8")
        self.imgBackground = np.zeros(
            (int(self.height), int(self.width), 3), dtype="uint8")
        self.imgMask = np.zeros(
            (int(self.height), int(self.width), 3), dtype="uint8")
        self.imgRectMask = np.zeros(
            (int(self.height), int(self.width), 3), dtype="uint8")

        # Copy a image of snapshot for reference
        self.imgMask = self.imgRef.copy()
        self.classes = []
        with open("coco.names", 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        # print(classes)
        self.layer_name = net.getLayerNames()
        self.output_layer = [self.layer_name[i - 1]
                             for i in net.getUnconnectedOutLayers()]
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        self.drawing = False
        self.ix, self.iy = -1, -1

        self.endx, self.endy = -1, -1

    def clearmask(self):
        self.imgRectMask.fill(0)

    def snapshot(self):
        ret, frame = self.vid.read()
        self.imgRef = frame.copy()
        self.imgRef = cv2.cvtColor(self.imgRef, cv2.COLOR_BGR2RGB)
        self.imgRef = cv2.resize(self.imgRef, (int(self.width), int(
            self.height)), interpolation=cv2.INTER_AREA)
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
            if ret:
                # ==============
                # Detect Objects
                blob = cv2.dnn.blobFromImage(
                    frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(self.output_layer)
                # print(outs)

                # Showing Information on the screen
                class_ids = []
                confidences = []
                boxes = []
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.5:
                            # Object detection
                            center_x = int(detection[0] * self.width)
                            center_y = int(detection[1] * self.height)
                            w = int(detection[2] * self.width)
                            h = int(detection[3] * self.height)
                            # cv.circle(img, (center_x, center_y), 10, (0, 255, 0), 2 )
                            # Reactangle Cordinate
                            x = int(center_x - w/2)
                            y = int(center_y - h/2)
                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)
                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
                print(indexes)

                font = cv2.FONT_HERSHEY_SIMPLEX  # cv2.FONT_HERSHEY_PLAIN
                presence = ""
                count = 0
                danger = False
                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        cx = int((x + x + w) / 2)
                        cy = int((y + y + h) / 2)
                        label = str(self.classes[class_ids[i]])
                        print(label)
                        # str(confidences[i])
                        confidence = f'{confidences[i]:.3f}'
                        if ((presence == "person" and label == "cell phone") or (presence == "cell phone" and label == "person")):
                            if count == 1:
                                print("Test Succeeded - Detecting One Person")
                                danger = True
                            elif count == 2:
                                print("Test Succeeded - Detecting Two People")
                                danger = False

                        if label == "cell phone" or label == "person":
                            presence = label

                        if label == "person":
                            count += 1

                        if danger == True and label == "cell phone":
                            color = self.colors[i]
                            cv2.rectangle(self.imgOut, (self.ix, self.iy),
                                          (self.endx, self.endy), color, 1)
                            cv2.putText(frame, label + ' : ' + confidence + ' people count: ' +
                                        str(count), (x + 2, y + 10), font, 0.3, color, 1)

                    else:
                        danger = False

                self.imgRectMask = cv2.rectangle(
                    self.imgRectMask, (self.ix, self.iy), (self.endx, self.endy), (255, 255, 255), -1)

                imgIn = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                imgIn = cv2.resize(imgIn, (int(self.width), int(
                    self.height)), interpolation=cv2.INTER_AREA)

                self.imgOut = imgIn.copy()

                self.imgTemp1 = self.imgMask.copy()
                # create a copy of mask in yellow by setting blue = 0
                self.imgTemp1[:, :, 0] = 0

                print(self.imgTemp1.shape)
                print(imgIn.shape)

                cv2.addWeighted(imgIn, 0.5, self.imgTemp1,
                                0.5, 0.0, self.imgTemp1)
                cv2.imshow('imgTemp1', self.imgTemp1)

                self.imgOut = cv2.bitwise_and(imgIn, cv2.bitwise_not(
                    self.imgMask)) + cv2.bitwise_and(self.imgTemp1, self.imgMask)
                cv2.imshow('imgOut', self.imgOut)

                cv2.imshow('imgOut', self.imgOut)
                cv2.imshow('imgMask', self.imgMask)

                cv2.imshow('imgRectMask', self.imgRectMask)

                # Layout and Display Results in One Window
                imgDraw = cv2.bitwise_and(imgIn, cv2.bitwise_not(
                    self.imgRectMask)) + cv2. bitwise_and(self.imgTemp1, self.imgRectMask)
                imgResults = self.concat_vh([[imgIn, imgDraw],
                                             [self.imgRef, self.imgBackground],
                                             [imgIn, self.imgOut]])
                return (ret, imgResults)
            else:
                return (ret, None)
        else:
            return (ret, None)


# Create a window and pass it to the Application object
App(tkinter.Tk(), "TK_Video_Ref4.2a")
