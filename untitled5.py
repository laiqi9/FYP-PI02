import numpy as np
import cv2 
import glob
import math
from imutils import paths 
import imutils


class MyVideoCapture:
    def __init__(self, quad_num, video_source=1):
        self.vid = cv2.VideoCapture(video_source)
        ret, frame = self.vid.read()

        self.width = 1280.0/2
        self.height = 720.0/2
        width = self.width
        height = self.height
        self.quad_num = quad_num
        self.mainTitle = "Depth Test"

        # image declaration :heart_eyes:
        self.imgIn = np.zeros((int(height), int(width), 3),
                              dtype="uint8")   # blank images
        self.imgIn2 = np.zeros((int(height), int(width), 3),
                               dtype="uint8")   # blank images

        # screen res
        self.width = 1280.0/2
        self.height = 720.0/2

    # run upon destruction of object
    def __del__(self):
        # Release the video source when the object is destroyed
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()
            print("Stream ended")
            
    def split_frame(self, merged_frame):
        height, width, _ = merged_frame.shape
        #print("shape h:", height, "shape w:", width)

        # assuming that the number of squares is a square number (height and width of grid is same number of images)
        sqsize = int(math.sqrt(4))  # half height
        sqsize = int(math.sqrt(4))  # half width

        col = int(self.quad_num % sqsize)
        row = int(self.quad_num / sqsize)
        
        hheight = height/sqsize
        hwidth = width/sqsize
        
        r1 = int((hheight*row))
        r2 = int(hheight*(row+1))
        c1 = int((hwidth*col))
        c2 = int(hwidth*(col+1))
        
        print(hheight, hwidth)
        print(r1, r2, c1, c2, "quad", self.quad_num, "col:", col, "row:", row)
 
        quad = merged_frame[r1:r2, c1:c2]
        return quad

    def get_frame(self):
        if self.vid.isOpened():
            width = self.width
            height = self.height
            ret, frame = self.vid.read()
            if ret:
                iwidth = int(width)
                iheight = int(height)
                frame = self.split_frame(frame)
                self.imgIn = cv2.resize(frame, (iwidth, iheight), interpolation=cv2.INTER_AREA)
                
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)

CROP_WIDTH = 960
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
def cropHorizontal(image):
    return image[:,
                 int((CAMERA_WIDTH-CROP_WIDTH)/2):
                 int(CROP_WIDTH+(CAMERA_WIDTH-CROP_WIDTH)/2)]
        
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('cropped/*.png')
i = 0

for fname in images:   
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        # Draw and display the corners
        cv2.drawChessboardCorners(img, (7,6), corners2, ret)

#calibrate camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
img = cv2.imread('somework/1.png')
h,  w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

#remap to remove distoriton
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]

#mean error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error
print( "total error: {}".format(mean_error/len(objpoints)) )



q1 = MyVideoCapture(0)
q2 = MyVideoCapture(1)

ret, imgLeft = q1.get_frame()
ret1, imgRight = q2.get_frame()

#calibrate camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
h,  w = imgLeft.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

#remap to remove distoriton
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
imgLeft = cv2.remap(imgLeft, mapx, mapy, cv2.INTER_LINEAR)

#calibrate camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
h,  w = imgRight.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

#remap to remove distoriton
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
imgRight = cv2.remap(imgRight, mapx, mapy, cv2.INTER_LINEAR)


'''

imgLeft = cv2.imread("im0.png")
imgRight = cv2.imread("im1.png")
'''

imgLeft=cv2.resize(cv2.cvtColor(imgLeft, cv2.COLOR_BGR2GRAY), (640, 360), cv2.INTER_AREA)
imgRight=cv2.resize(cv2.cvtColor(imgRight, cv2.COLOR_BGR2GRAY), (640, 360), cv2.INTER_AREA)

'''
def find_marker(image):
    blur = cv2.GaussianBlur(imgLeftGray, (5,5), 0)
    edged = cv2.Canny(blur, 35, 125)
    
    cnts = cv2.findCountours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMIPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key = cv2.contourArea)
    
    return cv2.minAreaRect(c)

def distance_to_camera(knownWidth, focalLength, perWidth):
    return(knownWidth*focalLength)/perWidth

KNOWN_DISTANCE=30.0
KNOWN_WIDTH = 6.0

image = cv2.imread("2ft.png")
marker = find_marker(image)
focalLength= = (marker[1][0]*KNOWN_DISTANCE)/ KNOWN_WIDTH
'''

def ShowDisparity(bSize=19):
    stereo = cv2.StereoBM_create(numDisparities=32, blockSize=bSize)
    
    disparity = stereo.compute(imgLeft, imgRight)
    
    min = disparity.min()
    max = disparity.max()
    disparity = np.uint8(255*(disparity-min)/(max-min))
    
    return disparity


result = ShowDisparity()
cv2.imshow("test1", result)
cv2.imshow("test2", imgRight)
cv2.waitKey(0)
cv2.destroyAllWindows()


#disparity ref: https://medium.com/analytics-vidhya/distance-estimation-cf2f2fd709d8
