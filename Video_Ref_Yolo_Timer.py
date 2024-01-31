import tkinter as tk
from tkinter import messagebox
import cv2
import datetime
from PIL import Image as Img
from PIL import ImageTk
import numpy as np
import requests
from cryptography.fernet import Fernet

#buttons weird location
#screen moves when button activated
#does not go to security system on login
#when theres two people still detects
#make it that it saves from previous close down

classesFilename = "./yolov4 v2/obj.names"
configFilename  = "./yolov4 v2/yolov4-custom.cfg"
weightsFilename = "./yolov4 v2/yolov4-custom_final.weights"

def send_msg(text):
   token = "6322081157:AAG_zbPn8b3oXpYBV1IVclsP3IdqlSOxtDI"
   chat_id = "-4058750208"
   url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text 
   results = requests.get(url_req)
   print(results.json())

def generate_key():
    return Fernet.generate_key()

def encrypt_password(key, password):
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(key, encrypted_password):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

passwords = {}

def send_img():
    files ={'photo':open('danger.png', 'rb')}
    resp = requests.post('https://api.telegram.org/bot6322081157:AAG_zbPn8b3oXpYBV1IVclsP3IdqlSOxtDI/sendPhoto?chat_id=-4058750208',files=files)


class App:
    def __init__(self, window, window_title, video_source=1):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1280x1000") 

        # open video source
        self.vid = MyVideoCapture(video_source)

        # create a canvas that can fit the video source size
        self.window.grid_rowconfigure(list(range(10)), minsize=5)
        self.window.grid_columnconfigure(list(range(10)), minsize=60)
        self.window.grid_columnconfigure(1, minsize=100)

        self.window.grid_propagate(False)

        self.mouseDown = False

        self.canvas = tk.Canvas(
            window, width=self.vid.width*2, height=self.vid.height*3)
        self.canvas.pack()
        #self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.toggleMouse)
        self.canvas.bind("<Button-1>", self.toggleMouse)
        self.canvas.grid(row = 1, column = 4, sticky = tk.W)

        self.btn_snapshot = tk.Button(
            window, text="snapshot", width=30, command=self.vid.snapshot)
        self.btn_snapshot.grid(row = 2, column = 1, sticky = tk.W+tk.N)

        self.btn_clearmask = tk.Button(
            window, text="Clear Mask", width=30, command=self.clearmask)
        self.btn_clearmask.grid(row = 2, column = 6, sticky = tk.W+tk.N)
        
        # Adjust size 

        #For Time
        self.slidertime = tk.Scale(self.window, from_=0, to=50, orient=tk.HORIZONTAL, command=self.changeseconds)
        self.defaulttime = tk.Button( self.window , text = "Default", command=self.default_time, height=1, width=8)

        #For Detection
        self.click2 = tk.StringVar()
        self.click2.set("Select")
        detect2 = [
            "Auto Detect", 
            "Select AOI", 
        ]
        self.drop2 =tk.OptionMenu(self.window, self.click2, *detect2, command=self.secondselect)

        #For Threshold
        self.sliderthres = tk.Scale(self.window, from_=0, to=50, orient=tk.HORIZONTAL)
        self.defaultthres = tk.Button( self.window , text = "Default", command=self.default_thres, height=1, width=8)

        #Dropdown menu options
        detect_options = [
            "Main Menu",
            "Detection",
            "Time", 
            "Log Out",
        ]

        #Datatype of menu text
        self.clicked = tk.StringVar()

        #Initial Menu Text
        self.clicked.set("Main Menu")

        #Create Drop Down Menu
        drop = tk.OptionMenu(self.window, self.clicked, *detect_options, command=self.selected)
        drop.grid(row = 0, column = 0, sticky = tk.W+tk.N)

        #Create Label 
        label = tk.Label(self.window , text = " " ) 
        label.grid(row = 0, column = 0, sticky = tk.W) 

        #Create Play and Stop button
        resizedplayphoto = cv2.imread('play.png')
        resizedplayphoto = cv2.resize(resizedplayphoto, (20,20), interpolation=cv2.INTER_AREA)
        playphoto = Img.fromarray(resizedplayphoto)
        playphoto = ImageTk.PhotoImage(image=playphoto)
        playbutton = tk.Button(self.window, text = 'Click Me!', image = playphoto, command=self.selected)
        playbutton.grid(row = 2, column = 5, sticky = tk.W+tk.N)


        resizedstopphoto = cv2.imread('stop.png')
        resizedstopphoto = cv2.resize(resizedstopphoto, (20,20), interpolation=cv2.INTER_AREA)
        stopphoto = Img.fromarray(resizedstopphoto)
        stopphoto = ImageTk.PhotoImage(image=stopphoto)
        stopbutton = tk.Button(self.window, text = 'Click Me!', image = stopphoto, command=self.selected)
        stopbutton.grid(row = 2, column = 4, sticky = tk.E+tk.N)

        previouspage = tk.Button(self.window, text = 'Previous', command=self.selected)
        previouspage.grid(row = 2, column = 3, sticky = tk.E+tk.N)

        nextpage = tk.Button(self.window, text = 'Next', command=self.selected)
        nextpage.grid(row = 2, column = 4, sticky = tk.W+tk.N)
        
        # after called once, update auto called
        self.delay = 15
        self.update()
        # Execute tkinter 
        self.window.mainloop() 

    def changeseconds(self, e):
        #read val off of slider and set as self.vid.seconds
        self.vid.seconds=int(e)

    def secondselect(self, event):
        if self.click2.get()== "Select AOI":
            self.vid.click2 = "Select AOI"
        else:
            self.vid.click2 = "Auto Detect"
    
    def toggleMouse(self, e):
        if not self.vid.mouseDown:
            self.vid.mouseDown = True
            print("clicking")
            self.vid.ix = e.x
            self.vid.iy = e.y
            self.mouseOri = (e.x, e.y)
            print("ix, iy:", self.vid.ix, self.vid.iy)
        else:
            self.vid.mouseDown = False
            self.mousePt = (e.x, e.y)
            print("mousept:", self.mousePt)
            print("releasing")
            self.paint()

    def selected(self, event):
        if self.clicked.get() == 'Detection':
            print("Hi")
            self.drop2.grid(row=0, column=1, sticky=tk.W+tk.N)
            self.defaulttime.grid_forget()
            self.slidertime.grid_forget()

        elif self.clicked.get() == 'Time':
            print("kms")
            self.drop2.grid_forget()
            self.slidertime.set(15)
            self.slidertime.grid(row = 0, column = 1, sticky = tk.W+tk.N)
            # Create button, it will change label text 
            self.defaulttime.grid(row = 1, column = 0, sticky = tk.N)

        elif self.clicked.get() == 'Log Out':
            print("oops bye")
            self.window.destroy()
            switch()

        elif self.clicked.get() == "Main Menu":
            self.drop2.grid_forget()
            self.slidertime.grid_forget()
            self.defaulttime.grid_forget()

        else:
            print("Bye")
            self.drop2.grid_forget()
            self.slidertime.grid_forget()
            self.defaulttime.grid_forget()

    def default_time(self):
        self.slidertime.set(5)

    def paint(self):
        self.vid.imgMask = self.vid.imgMask.copy()

        cv2.rectangle(self.vid.imgMask, self.mouseOri, self.mousePt, (255, 255, 255), -1)

        print("rectangle from", self.vid.ix, self.vid.iy, self.mousePt)


    def clearmask(self):
        self.vid.imgMask.fill(0)

    def default_thres(self):
        self.sliderthres.set(50)

    def update(self):
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = ImageTk.PhotoImage(image=Img.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

class Application:
    def login(self):
        service = self.service_entry.get()
        #username = username_entry.get()
        password = self.password_entry.get()
        admin_pass = 'admin'
        admin_login = 'admin'

        if service and password:
            self.encrypted_password = encrypt_password(self.key, password)
            passwords[service] = {'username': service, 'password': self.encrypted_password}

            if service == admin_login and password == admin_pass:
                #close all
                self.window.destroy()
                send_msg("Security access granted. Login authenticated.")
                switch()
            else:
                messagebox.showwarning("Error", "Invalid login and password.") 


        else:
            messagebox.showwarning("Error", "Please fill in all the fields.")
    
        self.window.mainloop()


    def __init__(self, window):   
        self.key = generate_key()

        instructions = '''Please enter username and password for security reason'''

        self.window=window
        self.window.title("Password Manager")
        self.window.configure(bg="grey")
        self.window.resizable(False, False)


        center_frame = tk.Frame(self.window, bg="#d3d3d3")
        center_frame.grid(row=0, column=0, padx=10, pady=10)

        instruction_label = tk.Label(center_frame, text=instructions, bg="#d3d3d3")
        instruction_label.grid(row=0, column=1, padx=10, pady=5)

        service_label = tk.Label(center_frame, text="Username:", bg="#d3d3d3")
        service_label.grid(row=1, column=0, padx=10, pady=5)
        self.service_entry = tk.Entry(center_frame)
        self.service_entry.grid(row=1, column=1, padx=10, pady=5)

        password_label = tk.Label(center_frame, text="Password:", bg="#d3d3d3")
        password_label.grid(row=3, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(center_frame, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)


        add_button = tk.Button(center_frame, text="Login", command=self.login, height=1, width=10)
        add_button.grid(row=5, column=4, padx=10, pady=5)

    def __del__(self):
        self.window.destroy()


class MyVideoCapture:
    def __init__(self, video_source=1):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.mousePt = (0, 0)
        self.mouseDown = False
        self.runonce = True
        self.timer = datetime.datetime(2025, 1, 1, 1, 1, 1, 1)
        self.current = datetime.datetime.now()
        self.timesup = False
        self.dangerous = False

        self.click2 = "Select Option"
        self.seconds = 5


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

        # Copy an image of snapshot for reference
        self.imgMask = self.imgRef.copy()
        self.phototaken = False
        self.danger = False

    def snapshot(self):
        ret, frame = self.vid.read()
        self.imgRef = frame.copy()
        self.imgRef = cv2.cvtColor(self.imgRef, cv2.COLOR_BGR2RGB)
        self.imgRef = cv2.resize(self.imgRef, (int(self.width), int(self.height)), interpolation=cv2.INTER_AREA)
        return self.imgRef

    def __del__(self):
        # Release the video source when the object is destroyed
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()
            print("Stream ended")

    def concat_vh(self, list_2d):
        # return the final image
        return cv2.vconcat([cv2.hconcat(list_h) for list_h in list_2d])

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Detect Objects
                # Load yolo
                net = cv2.dnn.readNet(weightsFilename, configFilename)

                classes = []
                with open(classesFilename, 'r') as f:
                    classes = [line.strip() for line in f.readlines()]
                # print(classes)
                layer_name = net.getLayerNames()
                output_layer = [layer_name[i - 1] for i in net.getUnconnectedOutLayers()]
                colors = np.random.uniform(0, 255, size=(len(classes), 3))
                drawing = False                                                      #what what what
                self.ix, self.iy = -1, -1
                self.imgIn = frame
                if self.click2 == "Select AOI":
                    frame = cv2.bitwise_and(self.imgIn, self.imgMask)
                
                blob = cv2.dnn.blobFromImage(
                    frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layer)
                #fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
                #writer = cv2.VideoWriter('security.mp4', fourcc, 2, (640,480))
                
                print("self.click2", self.click2)
                phototaken = True

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
                            # Rectangle Coordinate
                            x = int(center_x - w/2)
                            y = int(center_y - h/2)
                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)
                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
                print(indexes)
        
                font = cv2.FONT_HERSHEY_SIMPLEX
                presence = ""
                count = 0
                danger = False
                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        cx = int((x + x + w) / 2)
                        cy = int((y + y + h) / 2)
                        label = str(classes[class_ids[i]])
                        print(label)
                        confidence = f'{confidences[i]:.3f}'

                        if ((presence == "person" and label == "cell phone") or (presence == "cell phone" and label == "person")):
                            if count == 1:
                                print("Test Succeeded - Detecting One Person")
                                self.danger = True
                            elif count == 2:
                                print("Test Succeeded - Detecting Two People")
                                self.danger = False

                        if label == "cell phone" or label == "person":
                            presence = label

                        if label == "person":
                            count += 1
                        
                        if self.danger == True and label == "cell phone":
                            self.current = datetime.datetime.now() 
                            if (self.timesup == False) and self.runonce == True:
                                
                                print("Current date:", str(self.current))
                                self.timer = self.current + datetime.timedelta(seconds=self.seconds)
                                print("timer time is:", self.timer)
                                print("Time in 5 seconds:", str(self.timer))
                                self.runonce = False
                                print("runounce false")
                            if self.current >= self.timer:
                                print("creaming crying while")
                                self.timesup = True
                                if self.timesup == True:    
                                    print("life is hell AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                                    color = colors[i]
                                    cv2.rectangle(
                                        frame, (x, y), (x + w, y + h), color, 1)
                                    cv2.putText(frame, label + ' : ' + confidence + ' people count: ' +
                                                str(count), (x + 2, y + 10), font, 0.3, color, 1)
                print("dangerous:", self.dangerous, "danger:", self.danger, "runonce:", self.runonce, "timesup:", self.timesup)
                if self.timesup and not(self.dangerous or self.danger or self. runonce):
                    self.timesup = False
                    self.runonce = True
                    print("resetting timer")
                    #writer.release()
                    print("freedom")
                    

                if self.dangerous and self.timesup and not self.phototaken:
                    cv2.imwrite("danger.png", frame)
                    #writer.write(frame)
                    send_msg("Danger Detected:")
                    send_img()
                    self.phototaken = True

                self.dangerous = self.danger
                self.danger = False
                imgIn = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imgIn = cv2.resize(imgIn, (int(self.width), int(
                    self.height)), interpolation=cv2.INTER_AREA)

                self.imgOut = imgIn.copy()

                self.imgTemp1 = self.imgMask.copy()
                self.imgTemp1[:, :, 0] = 0

                cv2.addWeighted(imgIn, 0.5, self.imgTemp1,
                                0.5, 0.0, self.imgTemp1)

                self.imgOut = cv2.bitwise_and(imgIn, cv2.bitwise_not(
                    self.imgMask)) + cv2.bitwise_and(self.imgTemp1, self.imgMask)


                # Layout and Display Results in One Window
                self.imgIn = cv2.cvtColor(self.imgIn, cv2.COLOR_BGR2RGB)
                imgResults = self.concat_vh([[self.imgIn, self.imgOut],
                                             [imgIn, self.imgOut]])

                return (ret, imgResults)
            else:
                return (ret, None)
        else:
            return (ret, None)

def switch():
    global loggedin, window
    if loggedin:
        loggedin=False
        window=tk.Tk()
        app=Application(window)
    else:
        loggedin=True
        window=tk.Tk()
        app=App(window, "Interface")

# Create a window and pass it to the Application object
loggedin = True
App(tk.Tk(), "test")
