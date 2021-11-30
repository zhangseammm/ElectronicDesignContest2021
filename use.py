
import cv2

clicked=False

def onMouse(event,x,y,flags,param): #一旦点击鼠标执行
    global clicked
    if event==cv2.EVENT_LBUTTONDBLCLK: #左键双击执行以下
        clicked=True


cameraCapture=cv2.VideoCapture(1)
cv2.namedWindow('MyWindow')
cv2.setMouseCallback('MyWindow',onMouse)  #设置鼠标点击之后动作
print('Shiwing camera feed, Click window or press any key to stop')
success,frame = cameraCapture.read()
while success and cv2.waitKey(1)==-1 and not clicked:  
#cv2.waitKey(1)==-1表示没有任何键盘输入
    cv2.imshow('MyWindow', frame)
    success,frame = cameraCapture.read()

cv2.destroyAllWindows()
cameraCapture.release()

