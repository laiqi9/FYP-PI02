import numpy as np
import cv2 
import glob
import math



#camera calibrate and depth

#steps: get right/left cam images of checkerboard 
#       calibrate each cam indiv
#       stereocalibrate
#       stereorectify
#       depth map

#simplified MYVIDEOCAPTURE for fetching individual cameras
class MyVideoCapture:
    def _init_(self, quad_num, video_source=0):
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
        width = 1280.0/2
        height = 720.0/2

        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # screen res
        self.width = 1280.0/2
        self.height = 720.0/2

    # run upon destruction of object
    def _del_(self):
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
                self.imgIn = cropHorizontal(self.imgIn)
                return (ret, cv2.cvtColor(self.imgIn, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)

CROP_WIDTH = 960
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720


def cropHorizontal(image):
    h, w, _ = image.shape
    return image[10:(h-10), 20:(w-20)]
        
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like ( 0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
lobjpoints = [] # 3d point in real world space
limgpoints = [] # 2d points in image plane.
robjpoints = []
rimgpoints = []
sharpen = np.array((
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0]), dtype = "int"
)

sharpen2 = (-1.0/256)*np.array((
    [1, 4, 6, 4, 1],
    [4, 16, 24, 16, 4],
    [6, 24, -476, 24, 6],
    [4, 16, 24, 16, 4],
    [1, 4, 6, 4, 1]), dtype = "int"
)
i = 0

images2 = glob.glob('left/*.png')
for fname in images2:   
    img = cv2.imread(fname)
    #img = cropHorizontal(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.filter2D(gray, -1, sharpen)
    
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        lobjpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        limgpoints.append(corners2)
        # Draw and display the corners
        cv2.drawChessboardCorners(gray, (7,6), corners2, ret)
        title = "cropped/L"+str(i)+".png"
        #cv2.imwrite(title, img)
        #cv2.imshow("true", img)
        #cv2.waitKey(0)
        cv2.destroyAllWindows()
        i+=1
    else:
        print(ret)
        cv2.imshow("false", gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
print("left camera finished")
        
images = glob.glob('right/*.png')
for fname in images:   
    img = cv2.imread(fname)
    #img = cropHorizontal(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.filter2D(gray, -1, sharpen)
    
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        robjpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        rimgpoints.append(corners2)
        # Draw and display the corners
        cv2.drawChessboardCorners(gray, (7,6), corners2, ret)
        title = "cropped/L"+str(i)+".png"
        #cv2.imwrite(title, img)
        #cv2.imshow("true", img)
        #cv2.waitKey(0)
        cv2.destroyAllWindows()
        i+=1
    else:
        print(ret)
        cv2.imshow("false", gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
print("right camera finished")

'''
#calibrate camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
img = cv2.imread('cropped/set1R.png')
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
'''

#q1 = MyVideoCapture(0)
#q2 = MyVideoCapture(1)
q1 = cv2.VideoCapture(0)
q2 = cv2.VideoCapture(0)

ret, frame = q1.read()
#frame = cropHorizontal()
h,w,_ = frame.shape
rret, rframe = q2.read()


#calibrate camera
lret, lmtx, ldist, lrvecs, ltvecs = cv2.calibrateCamera(lobjpoints, limgpoints, (640, 320), None, None)
lnewcameramtx, lroi = cv2.getOptimalNewCameraMatrix(lmtx, ldist, (w,h), 1, (w,h))

rret, rmtx, rdist, rrvecs, rtvecs = cv2.calibrateCamera(robjpoints, rimgpoints, (640,320), None, None)
rnewcameramtx, rroi = cv2.getOptimalNewCameraMatrix(rmtx, rdist, (w,h), 1, (w,h))

#remap to remove distoriton
mapx, mapy = cv2.initUndistortRectifyMap(lmtx, ldist, None, lnewcameramtx, (w,h), 5)
imgLeft = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
rmapx, rmapy = cv2.initUndistortRectifyMap(rmtx, rdist, None, rnewcameramtx, (w,h), 5)
imgRight = cv2.remap(rframe, rmapx, rmapy, cv2.INTER_LINEAR)

cv2.imshow("left", imgLeft)
cv2.imshow("right", imgRight)
cv2.waitKey(0)
cv2.destroyAllWindows()

imgLeft=cv2.resize(cv2.cvtColor(imgLeft, cv2.COLOR_BGR2GRAY), (640, 360), cv2.INTER_AREA)
imgRight=cv2.resize(cv2.cvtColor(imgRight, cv2.COLOR_BGR2GRAY), (640, 360), cv2.INTER_AREA)

def ShowDisparity(bSize=21):
    stereo = cv2.StereoBM_create(numDisparities=128, blockSize=bSize)
    
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

_, _, _, _, _, rotationMatrix, translationVector, _, _ = cv2.stereoCalibrate(
    lobjpoints, limgpoints, rimgpoints, lmtx, 
    ldist, rmtx, rdist,
    (w,h), None, None, None, cv2.CALIB_FIX_INTRINSIC)

(leftRect, rightRect, leftProj, rightProj, disptodepth, leftROI, rightROI) = cv2.stereoRectify(
    lmtx, ldist, rmtx, rdist, (w,h), rotationMatrix, translationVector,
    None, None, None, None, None,
    cv2.CALIB_ZERO_DISPARITY)

#disparity ref: https://medium.com/analytics-vidhya/distance-estimation-cf2f2fd709d8
#calibration ref: https://albertarmea.com/post/opencv-stereo-camera/
#horizontal translation ref: https://learnopencv.com/image-rotation-and-translation-using-opencv/
#note: ref images and camera are cropped due to too extreme fisheye effect on the edge