import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
import time, datetime   

class MyVideoCapture:
    def __init__(self, quad_num, video_source=1):
        classesFilename = "./dnn_yolov4/obj.names"
        configFilename = "./dnn_yolov4/yolov4-FYP.cfg"
        weightsFilename = "./dnn_yolov4/yolov4-FYP.weights"

        self.vid = cv2.VideoCapture(video_source)
        ret, frame = self.vid.read()
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
        self.x_screen = 1280
        self.y_screen = 720

        # drawing rectangles
        self.ix = 0
        self.endx = 0
        self.iy = 0
        self.endy = 0

    # run upon destruction of object
    def __del__(self):
        # Release the video source when the object is destroyed
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()
            print("Stream ended")

    def load_classes(self, classes_filename):
        self.classes = []
        with open(classes_filename, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.layer_name = self.net.getLayerNames()
        self.output_layer = [self.layer_name[i - 1]
                             for i in self.net.getUnconnectedOutLayers()]
        return self.classes

    def split_frame(self, merged_frame):
        height, width, _ = merged_frame.shape

        # using 4 as default rn for num_quads
        hheight = int(height/2)  # half height
        hwidth = int(width/2)  # half width

        if self.quad_num == 1:
            quad = merged_frame[0:hheight, 0:hwidth]
        elif self.quad_num == 2:
            quad = merged_frame[0:hheight, hwidth:1280]
        elif self.quad_num == 3:
            quad = merged_frame[hheight:720, 0:hwidth]
        else:
            quad = merged_frame[hheight:720, hwidth:1280]

        return quad
    
    def ref_capture (self):
        self.imgRef=self.imgIn.copy()
        print("captured ref")

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
     
    # Create class that acts as a countdown
    def countdown1(self):
     
        # Calculate the total number of seconds
        total_seconds = 3
        
        # While loop that checks if total_seconds reaches zero
        # If not zero, decrement total time by one second
        while total_seconds > 0 and self.quad:
     
            # Timer represents time left on countdown
            timer = datetime.timedelta(seconds = total_seconds)
            
            # Prints the time left on the timer
            print(timer, end="\r")
     
            # Delays the program one second
            time.sleep(1)
     
            # Reduces total time by one second
            total_seconds -= 1
            
        self.countedQ1=True

    def get_frame(self):
        if self.vid.isOpened():
            width = self.width
            height = self.height
            ret, frame = self.vid.read()
            if ret:
                iwidth = int(width)
                iheight = int(height)
                frame = self.split_frame(frame)

                self.imgIn = cv2.resize(
                    frame, (iwidth, iheight), interpolation=cv2.INTER_AREA)
                self.imgIn2 = self.imgIn.copy()  # Used for extracting and expanding quadrants
                self.imgIn3 = self.imgIn.copy()  # Used for taking average
                self.imgin = self.imgIn.copy()

                # Averaging to minimise moving objects as part of difference calculation
                # Taking average of ImgIn3
                cv2.accumulateWeighted(self.imgIn3, self.imgAverage, 0.005)
                # Convert averaged ImgIn3 to uint8 data type for bitwise operation
                imgAverage_uint8 = self.imgAverage.astype(np.uint8)
                if(self.ix>640):
                    self.ix=self.ix-640
                if(self.endx>640):
                    self.endx=self.endx-640
                if(self.iy>360):
                    self.iy=self.iy-360
                if(self.endy>360):
                    self.endy=self.endy-360

                if (self.ix > 0) and (self.endx > 0):
                    self.imgInDraw = cv2.rectangle(
                        self.imgInDraw, (self.ix, self.iy), (self.endx, self.endy), (255, 0, 255), -1)
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
                #print('refClass3', RefClassID3)
                LiveClassID1, LiveClassID2, LiveClassID3, LiveClassID4 = self.detect_objects(
                    imgAvgAoi)  # (imgAveragewMask)
                #print('LiveClass3', LiveClassID3)
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

                            # Hightlight quadrant where centre of image difference is detected using its coordinates
                            if (cx < (width / 2)) & (cy < (height / 2)):
                                if RefClassID1 != LiveClassID1:
                                    cv2.rectangle(
                                        self.imgIn, (0, 0), (int(width / 2), int(height / 2)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        self.imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.putText(
                                        self.imgIn, miss1 + obs1, (0, 5), font, 0.5, (0, 255, 255), 1)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID1 == LiveClassID1:
                                    pass
                                if (RefClassID1 == []) & (LiveClassID1 == []):
                                    #self.countdown1()
                                    #if self.countedQ1:
                                    cv2.rectangle(
                                        self.imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.rectangle(
                                        self.imgIn, (0, 0), (int(width / 2), int(height / 2)), (0, 0, 255), 5)
                                        #send_to_telegram("Difference detected!")
                                    #else:
                                        #self.countedQ1=False
                            if (cx > (width / 2)) & (cy < (height / 2)):
                                if RefClassID2 != LiveClassID2:
                                    cv2.rectangle(
                                        self.imgIn, (int(width / 2), 0), (int(width), int(height / 2)), (0, 0, 255), 5)
                                    cv2.putText(
                                        self.imgIn, miss2 + obs2, (645, 5), font, 0.5, (0, 255, 255), 1)
                                    cv2.rectangle(
                                        self.imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID2 == LiveClassID2:
                                    pass
                                if (RefClassID2 == []) & (LiveClassID2 == []):
                                    cv2.rectangle(
                                        self.imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        self.imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    #send_to_telegram("Difference detected!")
                            if (cx < (width / 2)) & (cy > (height / 2)):
                                if RefClassID3 != LiveClassID3:
                                    cv2.rectangle(
                                        self.imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        self.imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.putText(
                                        self.imgIn, miss3 + obs3, (0, 365), font, 0.5, (0, 255, 255), 1)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID3 == LiveClassID3:
                                    pass  # print()
                                if (RefClassID3 == []) & (LiveClassID3 == []):
                                    cv2.rectangle(
                                        self.imgIn, (0, int(height / 2)), (int(width / 2), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        self.imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    #send_to_telegram("Difference detected!")

                            if (cx > (width / 2)) & (cy > (height / 2)):
                                if RefClassID4 != LiveClassID4:
                                    cv2.rectangle(self.imgIn, (int(
                                        width / 2), int(height / 2)), (int(width), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        self.imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    cv2.putText(
                                        self.imgIn, miss4 + obs4, (645, 365), font, 0.5, (0, 255, 255), 1)
                                    #send_to_telegram("Difference detected!")
                                if RefClassID4 == LiveClassID4:
                                    pass  # print()
                                if (RefClassID4 == []) & (LiveClassID4 == []):
                                    cv2.rectangle(self.imgIn, (int(
                                        width / 2), int(height / 2)), (int(width), int(height)), (0, 0, 255), 5)
                                    cv2.rectangle(
                                        self.imgIn, (x, y), (x + w, y + h), (0, 0, 255), 3)
                                    #send_to_telegram("Difference detected!")

                return (ret, cv2.cvtColor(self.imgIn, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)
'''
class Quadrant:
    def __init__(self, quad_num, x_coord, y_coord, black_rect, green_rect, imgIn2):
        self.quad_num = quad_num
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.black_rect = black_rect
        self.green_rect = green_rect
        
        self.imgIn2 = imgIn2
        
    def Extract_Quadrant(self): # Method to extract, resize and layer AOI on the extracted quadrant   
                
        # Extracting the quadrant
        crop_width = int(1280 / 2)
        crop_height = int(720 / 2)
        x = self.x_coord
        y = self.y_coord
        crop_Quadrant = self.imgIn2[y:y+crop_height, x:x+crop_width]
        
        scale_percent = 1
        # Resize the quadrant
        width_resize = int(crop_Quadrant.shape[1] * scale_percent)
        height_resize = int(crop_Quadrant.shape[0] * scale_percent)
        dimension = (width_resize, height_resize)
        resized_quadrant = cv2.resize(crop_Quadrant, dimension, interpolation = cv2.INTER_AREA)
        cv2.imshow(self.quad_num, resized_quadrant)
        
        # Check current quadrant and shift resized quadrant on a specific location on screen
        if quadrant == 1: cv2.moveWindow(self.quad_num, 0, 0)
        elif quadrant == 2: cv2.moveWindow(self.quad_num, int(x_screen / 2), 0)
        elif quadrant == 3: cv2.moveWindow(self.quad_num, 0, int((y_screen / 2) - 70))
        elif quadrant == 4: cv2.moveWindow(self.quad_num, int(x_screen / 2), int((y_screen / 2) - 70))
        
        # Layer AOI on the quadrant
        layer = cv2.bitwise_or(self.black_rect, resized_quadrant)
        resized_quadrant = cv2.bitwise_or(layer, self.green_rect) # Convert black rectangle to green rectangle for Area of Interest
        cv2.imshow(self.quad_num, resized_quadrant)
    
cv2.imshow(mainTitle,imgIn)      
cv2.moveWindow(mainTitle, int((x_screen - width) / 2), int((y_screen - height) / 2)) # Set main window at the centre of the screen
cv2.setMouseCallback(mainTitle, onMouseButton)   
'''

class App:
    def __init__(self, window):
        self.window = window
        self.window.title("FYP PI02")
        
        self.active_quad=0 #set active quadrant

        self.vid = cv2.VideoCapture(1)

        self.video_captures = []

        self.video_captures.append(MyVideoCapture(1))
        self.video_captures.append(MyVideoCapture(2))
        self.video_captures.append(MyVideoCapture(3))
        self.video_captures.append(MyVideoCapture(4))
        
        #toplevel = tk.Toplevel(window) #'toplevel' can be changed to anything, it is just a variable to hold the top level, 'window' should be whatever variable holds your main window
        #toplevel.title = 'Expanded Quadrant'

        # Use the fixed window size
        self.canvas = tk.Canvas(window, width=1280, height=720)
        self.canvas.pack()

        self.canvas.bind('<Motion>', self.mouseMove)
        self.canvas.bind("<Button-1>", self.startpaint)
        self.canvas.bind("<ButtonRelease-1>", self.endpaint)

        #buttons
        self.btn_clearmask = tk.Button(
            window, text="Clear Mask", width=30, command=self.clearmask)
        self.btn_clearmask.pack(side=tk.RIGHT, anchor=tk.NE, expand=True)
        self.btn_snapshot = tk.Button(
            window, text="Take Reference", width=30, command=self.video_captures[self.active_quad].ref_capture())
        self.btn_snapshot.pack(side=tk.RIGHT, anchor=tk.NE, expand=True)
        #self.btn_snapshot = tk.Button(
            #window, text="Enlarge Quadrant", width=30, command=self.ubt1())
        #self.btn_snapshot.pack(side=tk.RIGHT, anchor=tk.NE, expand=True)
        

        #quad buttons
        self.btn_Q1 = tk.Button(
            window, text="Q1", width=15, relief="raised", command= lambda: self.toggle(1))
        self.btn_Q2 = tk.Button(
            window, text="Q2", width=15, relief="raised", command= lambda: self.toggle(2))
        self.btn_Q3 = tk.Button(
            window, text="Q3", width=15, relief="raised", command= lambda: self.toggle(3))
        self.btn_Q4 = tk.Button(
            window, text="Q4", width=15, relief="raised", command= lambda: self.toggle(4))
        
        time.sleep(2)
        
        self.btn_Q1.pack(anchor=tk.CENTER, expand=True)
        self.btn_Q2.pack(anchor=tk.CENTER, expand=True)
        self.btn_Q3.pack(anchor=tk.CENTER, expand=True)
        self.btn_Q4.pack(anchor=tk.CENTER, expand=True)
        
        # after called once, update auto called
        self.delay = 15
        self.update()

        self.window.mainloop()

    def toggle(self, quad):
        if quad==1:
            self.btn_Q1.config(relief="sunken")
            self.btn_Q2.config(relief="raised")
            self.btn_Q3.config(relief="raised")
            self.btn_Q4.config(relief="raised")
        elif quad==2:
            self.btn_Q1.config(relief="raised")
            self.btn_Q2.config(relief="sunken")
            self.btn_Q3.config(relief="raised")
            self.btn_Q4.config(relief="raised")
        elif quad==3:
            self.btn_Q1.config(relief="raised")
            self.btn_Q2.config(relief="raised")
            self.btn_Q3.config(relief="sunken")
            self.btn_Q4.config(relief="raised")
        elif quad==4:
            self.btn_Q1.config(relief="raised")
            self.btn_Q2.config(relief="raised")
            self.btn_Q3.config(relief="raised")
            self.btn_Q4.config(relief="sunken")
        
        self.active_quad=quad-1 #0 indexed array of video_captures vs 1 indexed quad in this function
        print(self.active_quad)

    def clearmask(self):
        self.video_captures[self.active_quad].imgMask.fill(0)
        self.video_captures[self.active_quad].imgTemp.fill(0)
        self.video_captures[self.active_quad].imgInDraw.fill(0)
        

    def mouseMove(self, e):
        x = e.x
        y = e.y
        print("Mouse: ", x, y)

    def startpaint(self, event):
        self.video_captures[self.active_quad].iy
        self.video_captures[self.active_quad].iy, self.video_captures[self.active_quad].ix, self.video_captures[self.active_quad].endx, self.video_captures[self.active_quad].endy

        print("AHHHHHHHHHHHHHHHHHHHHHHHHH", self.video_captures[self.active_quad].ix,
              self.video_captures[self.active_quad].iy, self.video_captures[self.active_quad].endx, self.video_captures[self.active_quad].endy)
        self.drawing = True
        self.video_captures[self.active_quad].ix, self.video_captures[self.active_quad].iy = (
            event.x, event.y)

    def endpaint(self, event):
        self.video_captures[self.active_quad].endx, self.video_captures[self.active_quad].endy

        print("ENDDDDDDDDDDDDDDDDDDDD",
              self.video_captures[self.active_quad].endx, self.video_captures[self.active_quad].endy)
        self.drawing = False
        self.video_captures[self.active_quad].endx, self.video_captures[self.active_quad].endy = (
            event.x, event.y)

    def update(self):
        image_frames = []
        
        for video in self.video_captures:
            ret, frame = video.get_frame()
            if ret:
                print("img", type(frame))
                image_frames.append(cv2.resize(frame, (640,360)))
                
        merged_image = self.assemble_grid(image_frames)
        merged_image = Image.fromarray(merged_image)

        
        self.photo = ImageTk.PhotoImage(image=merged_image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
    
        self.window.after(self.delay, self.update)
        
    def concat_vh(self, list_2d):
        # return final image
        return cv2.vconcat([cv2.hconcat(list_h) 
                        for list_h in list_2d])
    
    def assemble_grid(self, images):
        num_images = len(images)
        grid_size = int(np.sqrt(num_images))
    
        # Manually construct grid without NumPy reshape:
        merged_image = None
        for row_index in range(grid_size):
            row_images = images[row_index * grid_size: (row_index + 1) * grid_size]
            concatenated_row = cv2.hconcat(row_images)
            if merged_image is None:
                merged_image = concatenated_row
            else:
                merged_image = cv2.vconcat([merged_image, concatenated_row])
    
        return merged_image
   
    def align_images(self, images):
        width = max(image.shape[1] for image in images)
        height = max(image.shape[0] for image in images)
        aligned_images = [cv2.resize(image, (width, height)) for image in images]
        return aligned_images
'''              
    def ubt1(self):
        title="Quadrant" + str(self.active_quad) 
        # Creating a second Level
        second = tk.Toplevel()
        second.title(title) # Rename this
        # Changing Label text
        # Creation of Canvas
        c=tk.Canvas(second)
        c.pack()
    
        # Creation of image object
        img = self.video_captures[self.active_quad].get_frame()
        self.picture = ImageTk.PhotoImage(image=img)
        self.c.create_image(0, 0, image=self.picture, anchor=tk.NW)

        self.second.after(self.delay, self.ubt1())
'''

def main():
    # num_cameras = 4  # Change this variable to the number of available cameras
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
