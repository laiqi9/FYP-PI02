# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 18:57:42 2023

@author: lohchinfei
"""
# WebcamStream: CvCam on separate thread, 
# Version: 0.0
# Description: "crude" version, use with care.
#            : do not use cv2.wait or cv2.imshow() in this class
#              to avoid conflict with main loop 
#

import cv2 
import time 
from threading import Thread 

class WebcamStream:
    
    def __init__(self, name = "WebcamStream", src = 0, width = 1280, height = 720 ):

        # initialize the thread name
        self.name = name


        # Setup Camera Capture:
        # 1. Internal Webcam    
        self.cap  = cv2.VideoCapture(src) # Internal Webcam
        
        #pipeline = 'gst-launch-1.0 -e qtiqmmfsrc camera-id=0 ! video/x-h264,format=NV12,width=1920,height=1080,framerate=30/1 ! h264parse ! avdec_h264 ! videoconvert ! waylandsink sync=false'
        #cap = cv2.VideoCapture(0, cv2.CAP_GSTREAMER)
        
        # 2. if you are using IP camera
        #cap = cv2.VideoCapture("rtsp://admin:admin@192.168.0.102:554/11")
        #cap = cv2.VideoCapture("rtsp://192.168.0.100:554/11")
        #time.sleep(2) # pause while camera turns on, just in case
        
        w = width; h = height
        print("WebcamStream: setting camera resolution: ", w, h)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        
        w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print("camera actual resolution received: ", w, h)
        
        # read the first frame from the webcam stream
        (ret, self.frame) = self.cap.read()

        # initialize the variable for stopping thread 
        self.stopped = False
        self.avail = False
        
    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.loop, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def loop(self):
        
        # loop indefinitely until stop command is received
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped is True:
                break  # this ends the loop

            # otherwise, read the next frame from the stream
            (ret, self.frame) = self.cap.read()
            if ret:  
                self.avail = True 
                #print("WebcamStream: camera frame read.")
        
        # housekeeping before thread terminates
        self.cap.release() # turn off camera.

    def read(self):
        # return the frame most recently read
        self.avail = False   # reset 
        return self.frame
    
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True