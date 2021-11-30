red_threshold  = (0, 25, 40, 70, 20, 50)
black_threshold  = (20, 40, -10, 10, -10, 10)
debug=1
#red_thereshold =(37, 62, 6, 80, -38, 83)
import sensor, image, time
from pyb import UART
LINE_COLOR_thereshold = [(0, 200)]
uart = UART(3, 115200)
from pyb import LED
flag=1
DISTORTION_FACTOR = 1.5#畸变矫正因子
ROIS = {                                 #ROIS将镜头的画面分割为5个区域分别找寻色块
    'down': (0, 55, 64, 8),
    'middle': (0, 28, 64, 8),
    'up': (0, 0, 64, 8),
    'left': (0, 0, 8, 64),
    'right': (56, 0, 8, 64)
}
def xunxian():
    #开启LED灯进行补光
    LED(1).on()
    LED(2).on()
    LED(3).on()
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)#设置图像为彩模式
    sensor.set_framesize(sensor.B64X64)  #设置像素大小
    #sensor.set_windowing([0,20,80,40])
    sensor.skip_frames(time = 2000)     # WARNING: If you use QQVGA it may take seconds
    clock = time.clock()                # to process a frame sometimes.

    while(flag):
        clock.tick()
        img = sensor.snapshot().binary([red_threshold])
        img.lens_corr(DISTORTION_FACTOR)  #进行镜头畸形矫正，里面的参数是进行鱼眼矫正的程度
        line = img.get_regression([(100,100,0,0,0,0)], robust = True)
        if (line):
            rho_err = abs(line.rho())-img.width()/2
            if line.theta()>90:
                theta_err = line.theta()-180
            else:
                theta_err = line.theta()
            count=0
            #img.draw_line(line.line(), color = 127)
            if (line.y1()-line.y2()):
                k=int((line.x1()-line.x2())/(line.y1()-line.y2())*100)
            else:
                k=0;
            aver=int((line.x1()+line.x2())/64/2*100)
            for i in range(0,64):
                for j in range(0,8):
                    if img.get_pixel(i,j)==(255,255,255):
                        count=count+1
            #print(count)
            uart.write('aver'+str(aver))
            uart.write('count'+str(count))
            uart.write('k'+str(k))
grey_threshold=[0,125]

def cut_num(img):
    roi=[]
    blobs2 = img.find_blobs([grey_threshold])
      
    if(0<len(blobs2)<=4):
        for i in range(0,len(blobs2)):
            if debug:
                img.draw_rectangle(blobs2[i].rect())
            roi[i]=blobs2[i]
    return roi

def count_x(img,x,y,w,h,rate):    
    #h串几个点
    for i in range(x,x+w):
        count=0 
        temp=0
        if temp!=(img.get_pixel(i,y+h*rate)==(255,255,255)):
            count1=count+1             
        temp=(img.get_pixel(i,y+h/3)==(255,255,255))
        if debug:
            img.set_pixel(i,y+h/3)=(100,0,0)
    return count

def count_y(img,x,y,w,h,rate):    
    #w串几个点y
    for i in range(y,y+h):
        count=0 
        temp=0
        if temp!=(img.get_pixel(x+w*rate,i)==(255,255,255)):
            count1=count+1             
        temp=(img.get_pixel(x+w*rate,i)==(255,255,255))
        if debug:
            img.set_pixel(x+w*rate,i)=(100,0,0)
    return count

def density_roi(img,x,y,w,h):
    #输入为roi，输出为roi的density
    count =0
    for i in range(x,x+w):
            for j in range(y,y+h):
                if img.get_pixel(i,j)==(255,255,255):
                    count=count+1
    density=count/(w*h)
    return density
#def num(roi):



while(1):
    img = sensor.snapshot().binary([black_threshold])
    roi=[]
    roi=cut_num(img)
