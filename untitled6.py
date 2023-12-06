import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
import time


class MyVideoCapture:
    def __init__(self, video_source, quad_num):
        classesFilename = "./dnn_yolov4/obj.names"
        configFilename = "./dnn_yolov4/yolov4-FYP.cfg"
        weightsFilename = "./dnn_yolov4/yolov4-FYP.weights"

        self.vid = cv2.VideoCapture(video_source)
        self.net = cv2.dnn.readNetFromDarknet(configFilename, weightsFilename)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.classes = self.load_classes(classesFilename)

        self.width = 1280.0/2
        self.height = 720.0/2
        width = self.width
        height = self.height

        self.quad_num = quad_num

        self.mainTitle = "Obstruction Destruction System"
        self.C1 = "Camera 1"
        self.C2 = "Camera 2"
        self.C3 = "Camera 3"
        self.C4 = "Camera 4"

        # not declaring click, msg_sent because not needed rn
        self.scale_percent = 1.0

        # image declaration :heart_eyes:
        self.imgIn = np.zeros((int(height), int(width), 3),
                              dtype="uint8")   # blank images
        self.imgIn2 = np.zeros((int(height), int(width), 3),
                               dtype="uint8")   # blank images
        # Used for collating all AOI drawings
        self.imgInDraw = np.zeros(
            (int(height), int(width), 3), dtype="uint8")   # blank images
        # Store reference image here
        self.imgRef = np.zeros((int(height), int(width), 3),
                               dtype="uint8")   # blank images
        self.imgMaskDiff = np.zeros(
            (int(height), int(width), 3), dtype="uint8")   # blank images
        self.imgAverage = np.zeros(
            (int(height), int(width), 3), dtype="float32")   # blank images

        # imgTemp used for creating black rectangles on white image
        self.imgTemp = np.ones(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")
        self.imgTemp2 = np.ones(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")
        self.imgTemp3 = np.ones(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")
        self.imgTemp4 = np.ones(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")

        # imgMask used for creating green rectangles on black image
        self.imgMask = np.zeros(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")
        self.imgMask2 = np.zeros(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")
        self.imgMask3 = np.zeros(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")
        self.imgMask4 = np.zeros(
            (int(height/2*self.scale_percent), int(width/2*self.scale_percent), 3), dtype="uint8")

        self.th = 20
        self.ts = 40
        self.tv = 50
        self.lower = np.array([self.th, self.ts, self.tv])
        self.upper = np.array([255, 255, 255])

        # screen res
        self.x_screen = 1920
        self.y_screen = 1080

    def load_classes(self, classes_filename):
        self.classes = []
        with open(classes_filename, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.layer_name = self.net.getLayerNames()
        self.output_layer = [self.layer_name[i - 1] for i in self.net.getUnconnectedOutLayers()]
        return self.classes

    def split_frame(self, merged_frame):
        height, width = (1280, 720)

        # using 4 as default rn for num_quads
        hheight = int(height/2)  # half height
        hwidth = int(width/2)  # half width

        if self.quad_num == 1:
            quad = merged_frame[:hheight, :hwidth]
        elif self.quad_num == 2:
            quad = merged_frame[:hheight, hwidth:]
        elif self.quad_num == 3:
            quad = merged_frame[hheight:, :hwidth]
        else:
            quad = merged_frame[hheight:, hwidth:]

        return quad

    def detect_objects(self, img):
        blob = cv2.dnn.blobFromImage(
            img, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layer)  # outputs array `
        # print('outs', outs)

        # Showing Information on the screen
        class_ids = []
        confidences = []
        boxes = []

        CCoords = []
        ClassID = []

        ClassID1 = []
        ClassID2 = []
        ClassID3 = []
        ClassID4 = []

        CCoords1 = []
        CCoords2 = []
        CCoords3 = []
        CCoords4 = []

        Q1Idx = []
        Q2Idx = []
        Q3Idx = []
        Q4Idx = []

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
                    # Reactangle Cordinate
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        print('indx:', indexes)

        font = cv2.FONT_HERSHEY_SIMPLEX  # cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                cx = int((x + x + w) / 2)
                cy = int((y + y + h) / 2)
                label = str(self.classes[class_ids[i]])
                confidence = f'{confidences[i]:.2f}'  # str(confidences[i])
                # print(label)
                color = (0, 255, 255)  # colors[i]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                # cv2.putText(img, label + ' : ' +  confidence , (x + 5, y + 15), font, 0.5, (0,0,0),3)
                cv2.putText(img, label + ' : ' + confidence,
                            (x + 5, y + 15), font, 0.5, color, 1)
                ClassID.append(class_ids[i])
                CCoords.append([cx, cy])
        for i in CCoords:
            if (i[0] < (self.width / 2)) & (i[1] < (self.height / 2)):  # q1
                CCoords1.append(i)
                Q1Idx.append(CCoords.index(i))
            if (i[0] > (self.width / 2)) & (i[1] < (self.height / 2)):  # q2
                CCoords2.append(i)
                Q2Idx.append(CCoords.index(i))
            if (i[0] < (self.width / 2)) & (i[1] > (self.height / 2)):
                CCoords3.append(i)
                Q3Idx.append(CCoords.index(i))
            if (i[0] > (self.width / 2)) & (i[1] > (self.height / 2)):
                CCoords4.append(i)
                Q4Idx.append(CCoords.index(i))
        for idx in Q1Idx:
            if 0 <= idx < len(ClassID):
                ClassID1.append(ClassID[idx])
            else:
                print()
        for idx in Q2Idx:
            if 0 <= idx < len(ClassID):
                ClassID2.append(ClassID[idx])
            else:
                print()
        for idx in Q3Idx:
            if 0 <= idx < len(ClassID):
                ClassID3.append(ClassID[idx])
            else:
                print()
        for idx in Q4Idx:
            if 0 <= idx < len(ClassID):
                ClassID4.append(ClassID[idx])
            else:
                print()
        return ClassID1, ClassID2, ClassID3, ClassID4

    # compares ref w live to return missing ids and obstructing ids.
    def CompwRef(self, RefClass, LiveClass):
        miss = ' missing: '
        obs = ' obstruction: '
        obstruction = []
        missing = []
        for item in RefClass[:]:
            if item in LiveClass:
                LiveClass.remove(item)
                RefClass.remove(item)
                obstruction = LiveClass.copy()
                missing = RefClass.copy()
            elif item not in LiveClass:
                missing = RefClass.copy()
                obstruction = LiveClass.copy()
        obstruction = LiveClass.copy()
        missing = RefClass.copy()
        for c in obstruction:
            if 0 <= c < len(self.classes):
                obs += ', ' + self.classes[c]
            else:
                print()
        for c in missing:
            if 0 <= c < len(self.classes):
                miss += ' ' + self.classes[c]
            else:
                print()
        return miss, obs

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = self.split_frame(frame)
            if ret:
                self.imgIn = cv2.resize(frame, (int(self.width), int(self.height)),
                                        interpolation=cv2.INTER_AREA)
                self.imgIn2 = self.imgIn.copy()  # Used for extracting and expanding quadrants
                self.imgIn3 = self.imgIn.copy()  # Used for taking average
                self.imgin = self.imgIn.copy()

                # Averaging to minimise moving objects as part of difference calculation
                # Taking average of ImgIn3
                cv2.accumulateWeighted(self.imgIn3, self.imgAverage, 0.005)
                # Convert averaged ImgIn3 to uint8 data type for bitwise operation
                imgAverage_uint8 = self.imgAverage.astype(np.uint8)

                # Extract interested portions of each quadrant
                # Extracts corresponding pixels bounded within white rectangle
                imgAveragewMask = cv2.bitwise_and(
                    imgAverage_uint8, self.imgInDraw)
                cv2.accumulateWeighted(self.imgin, self.imgAverage, 0.006)
                self.imgin = self.imgin.astype(np.uint8)
                imgAvgAoi = cv2.bitwise_and(self.imgInDraw, self.imgin)
                # Extracts corresponding pixels bounded within white rectangle
                imgRefMask = cv2.bitwise_and(self.imgRef, self.imgInDraw)
                imgAveragewMaskHSV = cv2.cvtColor(
                    imgAveragewMask, cv2.COLOR_BGR2HSV)  # Convert to HSV from BGR
                imgRefMaskHSV = cv2.cvtColor(
                    imgRefMask, cv2.COLOR_BGR2HSV)  # Convert to HSV from BGR

                # Set H as hue value for imgAveragewMaskHSV
                H = imgAveragewMaskHSV[:, :, 0]
                # Set S as saturation value for imgAveragewMaskHSV
                S = imgAveragewMaskHSV[:, :, 1]
                # Set V as value value for imgAveragewMaskHSV
                V = imgAveragewMaskHSV[:, :, 2]

                # Extract H component from imgAveAoI and imgRefwMask
                imgAveragewMaskH = imgAveragewMaskHSV[:, :, 0]
                imgRefMaskH = imgRefMaskHSV[:, :, 0]

                # Find difference between imgAveragewMaskH & imgRefMaskH
                dh = cv2.absdiff(imgAveragewMaskH, imgRefMaskH)
                # hue range is 0-180, so need to correct negative values present in dh, if diff  in hue is greater than 90, correct it i.e. dh = 180 - dh
                dh[dh > 90] = 180.0 - dh[dh > 90]
                imgDiffAbs = cv2.absdiff(imgAveragewMaskHSV, imgRefMaskHSV)
                ds = imgDiffAbs[:, :, 1]
                dv = imgDiffAbs[:, :, 2]

                self.imgMaskDiff.fill(0)

                # test different conditions for creating mask
                self.imgMaskDiff[dv > self.tv] = 255
                #imgMask[ds>ts] = 255
                self.imgMaskDiff[np.where((ds > self.ts) & (V > 20))] = 255
                self.imgMaskDiff[np.where(
                    (dh > self.th) & (S > 50) & (V > 50))] = 255
                imgMaskDiffGray = cv2.cvtColor(
                    self.imgMaskDiff, cv2.COLOR_BGR2GRAY)

                RefClassID1, RefClassID2, RefClassID3, RefClassID4 = self.detect_objects(
                    imgRefMask)
                print('refClass3', RefClassID3)
                LiveClassID1, LiveClassID2, LiveClassID3, LiveClassID4 = self.detect_objects(
                    imgAvgAoi)  # (imgAveragewMask)
                print('LiveClass3', LiveClassID3)
                miss1, obs1 = self.CompwRef(RefClassID1, LiveClassID1)
                miss2, obs2 = self.CompwRef(RefClassID2, LiveClassID2)
                miss3, obs3 = self.CompwRef(RefClassID3, LiveClassID3)
                miss4, obs4 = self.CompwRef(RefClassID4, LiveClassID4)

                contours, hierarchy = cv2.findContours(
                    image=imgMaskDiffGray, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
                font = cv2.FONT_HERSHEY_SIMPLEX  # cv2.FONT_HERSHEY_PLAIN
                if len(contours) != 0:
                    for contour in contours:
                        if cv2.contourArea(contour) > 50:
                            x, y, w, h = cv2.boundingRect(contour)
                           # cv2.rectangle(imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                            # Finding centre point of image difference
                            M = cv2.moments(contour)
                            cx = int(M["m10"]/M["m00"])
                            cy = int(M["m01"]/M["m00"])

                            '''
                            # Hightlight quadrant where centre of image difference is detected using its coordinates
                            if (cx < (width / 2)) & (cy < (height / 2)):
                                if RefClassID1 != LiveClassID1:
                                    cv2.rectangle(
                                        imgIn, (0, 0), (int(width / 2), int(height / 2)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.putText(
                                        imgIn, miss1 + obs1, (0, 5), font, 0.5, (0, 255, 255), 1)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID1 == LiveClassID1:
                                    pass
                                if (RefClassID1 == []) & (LiveClassID1 == []):
                                    cv2.rectangle(
                                        imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.rectangle(
                                        imgIn, (0, 0), (int(width / 2), int(height / 2)), (0, 0, 255), 5)
                                    #send_to_telegram("Difference detected!")
                            if (cx > (width / 2)) & (cy < (height / 2)):
                                if RefClassID2 != LiveClassID2:
                                    cv2.rectangle(
                                        imgIn, (int(width / 2), 0), (int(width), int(height / 2)), (0, 0, 255), 5)
                                    cv2.putText(
                                        imgIn, miss2 + obs2, (645, 5), font, 0.5, (0, 255, 255), 1)
                                    cv2.rectangle(
                                        imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID2 == LiveClassID2:
                                    pass
                                if (RefClassID2 == []) & (LiveClassID2 == []):
                                    cv2.rectangle(
                                        imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    #send_to_telegram("Difference detected!")
                            if (cx < (width / 2)) & (cy > (height / 2)):
                                if RefClassID3 != LiveClassID3:
                                    cv2.rectangle(
                                        imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.putText(
                                        imgIn, miss3 + obs3, (0, 365), font, 0.5, (0, 255, 255), 1)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID3 == LiveClassID3:
                                    pass  # print()
                                if (RefClassID3 == []) & (LiveClassID3 == []):
                                    cv2.rectangle(
                                        imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    #send_to_telegram("Difference detected!")

                            if (cx > (width / 2)) & (cy > (height / 2)):
                                if RefClassID4 != LiveClassID4:
                                    cv2.rectangle(imgIn, (int(
                                        width / 2), int(height / 2)), (int(width), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.putText(
                                        imgIn, miss4 + obs4, (645, 365), font, 0.5, (0, 255, 255), 1)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID4 == LiveClassID4:
                                    pass  # print()
                                if (RefClassID4 == []) & (LiveClassID4 == []):
                                    cv2.rectangle(imgIn, (int(
                                        width / 2), int(height / 2)), (int(width), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    #send_to_telegram("Difference detected!")
'''
                return (ret, cv2.cvtColor(self.imgIn, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)


class App:
    def __init__(self, window):
        self.window = window
        self.window.title("FYP PI02")
        self.window.geometry("1280x720")  # Set window size

        self.vid = cv2.VideoCapture(1)

        self.video_captures = []

        self.video_captures.append(MyVideoCapture(1, 1))
        self.video_captures.append(MyVideoCapture(1, 2))
        self.video_captures.append(MyVideoCapture(1, 3))
        self.video_captures.append(MyVideoCapture(1, 4))

        # Use the fixed window size
        self.canvas = tk.Canvas(window, width=1280, height=720)
        self.canvas.pack()

        self.update()

        # run upon destruction of object
    def __del__(self):
        # Release the video source when the object is destroyed
        if self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()
            print("Stream ended")

        # split incoming video into four quadrants to process seperately

    def update(self):
        frames = []
        for video_capture in self.video_captures:
            ret, frame = video_capture.get_frame()
            if ret:
                frame = Image.fromarray(frame)
                # Resize frames to fit the window
                frame = frame.resize((640, 360), Image.ANTIALIAS)
                frames.append(frame)

            merged_image = Image.new('RGB', (1280, 720))
            x_offset = 0
            y_offset = 0
            for frame in frames:
                merged_image.paste(frame, (x_offset, y_offset))
                x_offset += 640  # Adjust the x-offset for the next frame
                if x_offset >= 1280:
                    x_offset = 0
                    # Move to the next row if the width exceeds the window width        for i, frame in enumerate(frames):
                    y_offset += 360

        self.photo = ImageTk.PhotoImage(image=merged_image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(10, self.update)


def main():
    # num_cameras = 4  # Change this variable to the number of available cameras
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
