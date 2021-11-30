import cv2
import numpy as np
from numpy.core.records import array
def stretch(img):
    '''
    图像拉伸函数
    '''
    maxi=float(img.max())
    mini=float(img.min())
    
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img[i,j]=(255/(maxi-mini)*img[i,j]-(255*mini)/(maxi-mini))
    
    return img
def dobinaryzation(img):
    '''
    二值化处理函数
    '''
    maxi=float(img.max())
    mini=float(img.min())
    
    x=maxi-((maxi-mini)/2)
    #二值化,返回阈值ret  和  二值化操作后的图像thresh
    ret,thresh=cv2.threshold(img,x,255,cv2.THRESH_BINARY)
    #返回二值化后的黑白图像
    return thresh
def filter_out_red(src_frame):
    if src_frame is not None:
        hsv = cv2.cvtColor(src_frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 0, 0])
        upper_red = np.array([170, 170, 170])
        # inRange()方法返回的矩阵只包含0,255 (CV_8U) 0表示不在区间内
        mask = cv2.inRange(hsv, lower_red, upper_red)
        #return cv2.bitwise_and(src_frame, src_frame, mask=mask)
        return mask

img=cv2.imread('6.png')

m=400*img.shape[0]/img.shape[1]
#压缩图像
img=cv2.resize(img,(400,int(m)))
gray_img = filter_out_red(img)
#BGR转换为灰度图像
cv2.imshow("erzhi",gray_img)
#gray_img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#灰度拉伸
stretchedimg=stretch(gray_img)

'''进行开运算，用来去除噪声'''
r=5
h=w=r*2+1
kernel=np.zeros((h,w),np.uint8)
cv2.circle(kernel,(r,r),r,1,-1)
#bi运算bi

binaryimg=cv2.morphologyEx(stretchedimg,cv2.MORPH_CLOSE,kernel)

cv2.imshow("close",binaryimg)
#图像二值化
#binaryimg=dobinaryzation(openingimg)
#cv2.imshow("close2",openingimg)
#canny边缘检测
#kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
#kernelY = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 19))

#image = cv2.dilate(binaryimg, kernelX)
#image = cv2.erode(image, kernelX)

#image = cv2.erode(image, kernelY)
#image = cv2.dilate(image, kernelY)
#cv2.imshow("pz",image)
contours, hierarchy = cv2.findContours(binaryimg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
n=int(len(contours))
print(len(contours))
#for i in range(0,n):
    #s =contours[i][0]-contours[i][1]
    
#cv2.drawContours(img,contours,-1,(0,200,100),2)  

#print (len(contours)) 
'''消除小的区域，保留大块的区域，从而定位车牌'''
#进行闭运算
#kernel=np.ones((5,19),np.uint8)
#closingimg=cv2.morphologyEx(canny,cv2.MORPH_CLOSE,kernel)
#进行开运算
#openingimg=cv2.morphologyEx(closingimg,cv2.MORPH_OPEN,kernel)
cv2.imshow("kai",img)
for item in contours:
    rect = cv2.boundingRect(item)
    x = rect[0]
    y = rect[1]
    weight = rect[2]
    height = rect[3]
    print(weight,height)
    if (weight<height)&(weight>100)&(height>100):
        # 裁剪区域图片
        chepai = gray_img[y:y + height, x:x + weight]
        chepai1 = img[y:y + height, x:x + weight]
       
        cv2.imshow('chepai'+str(x), chepai1)

cv2.waitKey()

 
