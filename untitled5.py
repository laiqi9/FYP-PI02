import numpy as np
import cv2
import glob
import math
from imutils import paths
import imutils


# camera calibrate and depth

# steps: get right/left cam images of checkerboard
#       calibrate each cam indiv
#       stereocalibrate
#       stereorectify
#       depth map

# simplified MYVIDEOCAPTURE for fetching individual cameras
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
                self.imgIn = cv2.resize(
                    frame, (iwidth, iheight), interpolation=cv2.INTER_AREA)
                self.imgIn = cropHorizontal(self.imgIn)
                return (ret, cv2.cvtColor(self.imgIn, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)


CROP_WIDTH = 960
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720


def cropHorizontal(image):
    h, w, _ = image.shape
    return image[10:(h-10), 20:(w-20)]


def cropMoreHorizontal(image):
    h, w, _ = image.shape
    return image[10:(h-10), 40:(w-0)]


# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like ( 0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)

objp = np.zeros((7*10, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:10].T.reshape(-1, 2)
objp *= 0.015  # each square is 15mm
# Arrays to store object points and image points from all the images.
lobjpoints = []  # 3d point in real world space
limgpoints = []  # 2d points in image plane.
robjpoints = []
rimgpoints = []
stereoobjpts = []
stereoimgpts_l = []
stereoimgpts_r = []

i = 0

images2 = glob.glob('leftcalib/best/*.png')
for fname in images2:
    img = cv2.imread(fname)
    # img=cropHorizontal(img)
    #img = cropMoreHorizontal(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(
        gray, (7, 10), cv2.CALIB_CB_FAST_CHECK | cv2.CALIB_CB_ADAPTIVE_THRESH)
    # If found, add object points, image points (after refining them)
    if ret == True:
        lobjpoints.append(objp)
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        limgpoints.append(corners2)
        # Draw and display the corners
        cv2.drawChessboardCorners(gray, (7, 10), corners2, ret)
        #cv.imshow('img', img)
        # cv.waitKey(500)
        #title = "rightcalib/cropped/"+str(i)+".png"
        #cv2.imwrite(title, img)
        #cv2.imshow("true", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # i+=1
    else:
        print(ret)
        #cv2.imshow("false", gray)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
print("left camera finished")

lret, lmtx, ldist, lrvecs, ltvecs = cv2.calibrateCamera(
    lobjpoints, limgpoints, (640, 360), None, None, criteria=criteria)
#img = cropHorizontal(img)
# img=cropMoreHorizontal(img)
print("errorL:", lret)
img = cv2.imread('frame0L.png')
h,  w = img.shape[:2]
lnewcameramtx, lroi = cv2.getOptimalNewCameraMatrix(
    lmtx, ldist, (w, h), 1, (w, h))

# undistort
mapx, mapy = cv2.initUndistortRectifyMap(
    lmtx, ldist, None, lnewcameramtx, (w, h), 5)
dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
# crop the image

#x, y, w, h = roi
#dst = dst[y:y+h, x:x+w]
#cv2.imshow('left image undistorted', dst)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


images = glob.glob('rightcalib/best/*.png')
for fname in images:
    img = cv2.imread(fname)
    #img = cropMoreHorizontal(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.filter2D(gray, -1, sharpen)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7, 10), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        robjpoints.append(objp)
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        rimgpoints.append(corners2)
        # Draw and display the corners
        cv2.drawChessboardCorners(gray, (7, 10), corners2, ret)
        #title = "rightcalib/best/R"+str(i)+".png"
        #cv2.imwrite(title, img)
        #cv2.imshow("true", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        i += 1
    else:
        print(ret)
        #cv2.imshow("false", gray)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
print("right camera finished")


# calibrate camera
rret, rmtx, rdist, rrvecs, rtvecs = cv2.calibrateCamera(
    robjpoints, rimgpoints, gray.shape[::-1], None, None)
img = cv2.imread('frame0R.png')
print("errorL:", rret)
h,  w = img.shape[:2]
rnewcameramtx, rroi = cv2.getOptimalNewCameraMatrix(
    rmtx, rdist, (w, h), 1, (w, h))
# undistort
rmapx, rmapy = cv2.initUndistortRectifyMap(
    rmtx, rdist, None, rnewcameramtx, (w, h), 5)
dst = cv2.remap(img, rmapx, rmapy, cv2.INTER_LINEAR)
# crop the image
#x, y, w, h = roi
#dst = dst[y:y+h, x:x+w]
#cv2.imshow('right image undistorted', dst)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

images3 = glob.glob('both/*.png')
images4 = glob.glob('both/New folder/*.png')
for fname_l, fname_r in zip(images3, images4):
    imgL = cv2.imread(fname_l)
    imgR = cv2.imread(fname_r)
    #img = cropHorizontal(img)
    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)
    #gray = cv2.filter2D(gray, -1, sharpen)

    # Find the chess board corners
    retL, cornersL = cv2.findChessboardCorners(grayL, (7, 10), None)
    retR, cornersR = cv2.findChessboardCorners(grayR, (7, 10), None)
    # If found, add object points, image points (after refining them)
    if retL and retR:
        stereoobjpts.append(objp)
        corners2L = cv2.cornerSubPix(
            grayL, cornersL, (11, 11), (-1, -1), criteria)
        stereoimgpts_l.append(corners2L)
        corners2R = cv2.cornerSubPix(
            grayR, cornersR, (11, 11), (-1, -1), criteria)
        stereoimgpts_r.append(corners2R)
        # Draw and display the corners
        #cv2.drawChessboardCorners(gray, (7,10), corners2, ret)
        #title = "cropped/L"+str(i)+".png"
        #cv2.imwrite(title, img)
        #cv2.imshow("true", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    else:
        print(ret)
        #cv2.imshow("false", gray)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
print("stereo finished")

# cam 1 is right, both?*.png
#q1 = MyVideoCapture(0)
#q2 = MyVideoCapture(1)

#ret, imgLeft = q1.get_frame()
#frame = cropHorizontal()
#h,w,_ = imgLeft.shape
#rret, imgRight = q2.get_frame()

imgLeft = cv2.imread('im0.png')
imgRight = cv2.imread('im1.png')

imgLeft = cv2.resize(cv2.cvtColor(
    imgLeft, cv2.COLOR_BGR2GRAY), (360, 640), cv2.INTER_AREA)
imgRight = cv2.resize(cv2.cvtColor(
    imgRight, cv2.COLOR_BGR2GRAY), (360, 640), cv2.INTER_AREA)


def ShowDisparity(bSize=19):
    stereo = cv2.StereoBM_create(numDisparities=32, blockSize=bSize)
    depth = stereo.compute(imgLeft, imgRight)
    stereo.setMinDisparity(4)
    stereo.setNumDisparities(64)
    stereo.setBlockSize(21)
    stereo.setSpeckleRange(16)
    stereo.setSpeckleWindowSize(45)

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

error, _, _, _, _, rotationMatrix, translationVector, _, _ = cv2.stereoCalibrate(
    stereoobjpts, stereoimgpts_l, stereoimgpts_r, lmtx,
    ldist, rmtx, rdist,
    (w, h), None, None, None, flags=cv2.CALIB_FIX_INTRINSIC, criteria=criteria)

print("error:", error)

(leftRect, rightRect, leftProj, rightProj, disptodepth, leftROI, rightROI) = cv2.stereoRectify(
    lmtx, ldist, rmtx, rdist, (w, h), rotationMatrix, translationVector,
    None, None, None, None, None,
    cv2.CALIB_ZERO_DISPARITY)


# disparity ref: https://medium.com/analytics-vidhya/distance-estimation-cf2f2fd709d8
# calibration ref: https://albertarmea.com/post/opencv-stereo-camera/
# horizontal translation ref: https://learnopencv.com/image-rotation-and-translation-using-opencv/
# note: ref images and camera are cropped due to too extreme fisheye effect on the edge
