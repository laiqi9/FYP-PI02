import cv2
import numpy as np 

imgIn = cv2.imread('./images/lena.jpg')

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
imgOut = np.zeros((h, w, 3), dtype = "float")

for y in range(h):
    for x in range(w):        

        # Get Pixel RGB value at (x,y) location    
        r = imgIn[y,x,2].astype(np.float64)
        g = imgIn[y,x,1].astype(np.float64)
        b = imgIn[y,x,0].astype(np.float64)
        
        # Process pixel value
        r = r
        g = g 
        b = b
        # print(x,y,r,g,b)
        
        # Write Pixel value to output image
        imgOut[y,x] = [b,g,r] 
 
imgShow = np.clip(imgOut, 0.0, 255.0).astype(np.uint8)
cv2.imshow('image',imgShow)  

cv2.waitKey()
cv2.destroyWindow('image')
#cv2.destroyAllWindo
