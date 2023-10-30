import cv2
import numpy as np 

imgIn = cv2.imread('baboon.jpg').astype("uint8")

#img[:, :, 0] = 0*img[:, :, 0] 
#img[:, :, 1] = 0*img[:, :, 1] 
#img[:, :, 2] = 1*img[:, :, 2] 

print(imgIn.shape)
print(imgIn.size)
print(imgIn.dtype)
print()

h = imgIn.shape[0]
w = imgIn.shape[1]
channels = imgIn.shape[2]

print("h,w,chan = ", h,w,channels)

# Create output matrix
#imgOut = np.zeros((h, w, 3), dtype = "float")

imgHSV = cv2.cvtColor(imgIn, cv2.COLOR_BGR2HSV)
 
# OpenCV expects that imshow() will be fed with BGR color space so 
# you need to convert whatever image into BGR before displaying. 
# If you are displaying HSV image using imshow(), it will show you an 
# invalid image that you might interpret as something useful or cool. 
# But it's not. It's like a beautiful bug that you think it's a feature.
# So, just show the BGR image, it has the same semantic content as HSV.
#
# Note: In OpenCV, for HSV, hue range is [0,179], saturation range is [0,255], 
# and value range is [0,255]. 
#

cv2.imshow('imgIn',imgIn)  
cv2.imshow('imgHSV - wrong way to display',imgHSV)  

# Alternative way to display HSV as separate chroma (i.e color) and luminance components

# Separate into separate H, S and V components
imgHSV = cv2.cvtColor(imgIn, cv2.COLOR_BGR2HSV)

H = imgHSV[:,:,0]
S = imgHSV[:,:,1]
V = imgHSV[:,:,2]

cv2.imshow('H',H)  
cv2.imshow('S',S)  
cv2.imshow('V',V)  

# 1. Test: reconstructing an HSV image from their H, S and V components
imgTemp1 = np.zeros((h, w, 3), dtype = "uint8")
imgTemp1[:,:,0] = H
imgTemp1[:,:,1] = S
imgTemp1[:,:,2] = V
imgRecombined = cv2.cvtColor(imgTemp1, cv2.COLOR_HSV2BGR)
cv2.imshow('1. imgRecombined',imgRecombined)  

# 2. Test: display H component only, but display in color 
imgTemp2 = np.zeros((h, w, 3), dtype = "uint8")
imgTemp2[:,:,0] = H
imgTemp2[:,:,1].fill(255)  # 100% saturated
imgTemp2[:,:,2].fill(255)  # 100% luminance
imgH_in_color = cv2.cvtColor(imgTemp2, cv2.COLOR_HSV2BGR)
cv2.imshow('2. imgH_in_color',imgH_in_color)  

# 3. Test: display H & S component together in color 
imgTemp3 = np.zeros((h, w, 3), dtype = "uint8")
imgTemp3[:,:,0] = H
imgTemp3[:,:,1] = S
imgTemp3[:,:,2].fill(255)  # 100% luminance
imgHS_combined = cv2.cvtColor(imgTemp3, cv2.COLOR_HSV2BGR)
cv2.imshow('3. imgHS_combined',imgHS_combined)  

cv2.waitKey()
cv2.destroyAllWindows()
