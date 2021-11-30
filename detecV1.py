global mode
mode=0
red_threshold  = (0, 25, 40, 70, 20, 50)
black_threshold  = (-5, 25, -15, 15, -15, 15)
THRESHOLD = (10, 57, 11, 82, -14, 47) # Grayscale threshold for dark things...
#black_threshold  = (20, 40, -10, 10, -10, 10)
#red_thereshold =(37, 62, 6, 80, -38, 83)
import sensor, image, time
from pyb import UART
LINE_COLOR_thereshold = [(0, 200)]
uart = UART(3, 115200)
from pyb import LED
red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)
flag=1
DISTORTION_FACTOR = 1.5#畸变矫正因子
ROIS = {                                 #ROIS将镜头的画面分割为5个区域分别找寻色块
    'down': (0, 55, 64, 8),
    'middle': (0, 28, 64, 8),
    'up': (0, 0, 64, 8),
    'left': (0, 0, 8, 64),
    'right': (56, 0, 8, 64)
}
sensor.reset()
def cut_num(img):
    #img = sensor.snapshot().binary([black_threshold])
    roi=[]

    blobs=img.find_blobs([black_threshold],roi=(0,0,320,200),x_stride=10,y_stride=30,invert=1,area_threshold=20)
    #blobs=img.find_blobs([black_threshold],roi=(0,0,320,120),x_stride=15,y_stride=15,invert=1,area_threshold=10)

    if(0<len(blobs)<=4):
        roi=[]
        for i in range(0,len(blobs)):
            #img.draw_rectangle(blobs[i].rect())
            #print(blobs[i].x())
            roi.append(blobs[i].x())
            roi.append(blobs[i].y())
            roi.append(blobs[i].w())
            roi.append(blobs[i].h())
    return roi

def density(img,x,y,w,h,rate1,rate2,rate3,rate4):#w*rate1,h*rate3
    count=0
    area=0.001
    for i in range(x+int(w*rate1),x+int(w*rate2)):
        for j in range(y+int(h*rate3),y+int(h*rate4)):
            area=area+1
            if (img.get_pixel(i,j)==(255,255,255)):
                count = count+1
    return count/area

def density7878(img,x,y,w,h):
    count =0
    area=0.001
    for i in range(x+w-int(w/8),x+w):
        for j in range(y+h-int(h/8),y+h):
            area=area+1
            if (img.get_pixel(i,j)==(255,255,255)):
                count = count+1
    return count/area
def bubble_sort(list):
    l = len(list)
    for i in range(l-1,0,-1):
        for j in range(i):
            if list[j][0] > list[j+1][0]:
                list[j],list[j+1] = list[j+1],list[j]
    return list


def xunxian():
    while(mode==1):
        #clock.tick()
        #
        img = sensor.snapshot().binary([black_threshold])
        img=img.mean_pool(5,4)
        img.lens_corr(DISTORTION_FACTOR)  #进行镜头畸形矫正，里面的参数是进行鱼眼矫正的程度
        img.dilate(1)
        img.erode(1)
        img.dilate(2)
        blobs=img.find_blobs([black_threshold],roi=(5,0,40,40),x_stride=3,y_stride=3,invert=1,area_threshold=10)
        stop_flag=0
        if(0<len(blobs)):
            stop_flag=len(blobs)



        img = sensor.snapshot().binary([THRESHOLD])
        img=img.mean_pool(5,4)
        img.lens_corr(DISTORTION_FACTOR)  #进行镜头畸形矫正，里面的参数是进行鱼眼矫正的程度
        line = img.get_regression([(100,255)], robust = True)
        if (line):
            rho_err = abs(line.rho())-img.width()/2
            if line.theta()>90:
                theta_err = line.theta()-180
            else:
                theta_err = line.theta()
            count=0
            img.draw_line(line.line(), color = 127)
            if (line.y1()-line.y2()):
                k=int((line.x1()-line.x2())/(line.y1()-line.y2())*100)
            else:
                k=0;
            aver=int((line.x1()+line.x2())/64/4*100)
            for i in range(0,64):
                for j in range(0,8):
                    if img.get_pixel(i,j)==(255,255,255):
                        count=count+1
            #print(count)
            count=int(count/512*100)
            if stop_flag>6:
                count=99
            uart.write('aver'+str(aver+10))
            if (count>90):
             count=89
            uart.write('count'+str(count+10))
            #print(count)
            #计算角度
            k=line.theta()
            #print(k)
            if(k>90):
                k=-(180-k)-10
                #print(k)
            else :
                k=k+10
                #print(2)
            uart.write('k'+str(k))
            #换行
            data=bytearray([0x0d,0x0a])
            uart.write(data)

            if uart.any():
                a=uart.readline()
                print(a)
                global mode
                mode=0

def xunxian_init():
    #开启LED灯进行补光
    #sensor.reset()
    sensor.set_pixformat(sensor.RGB565)#设置图像为彩模式
    sensor.set_framesize(sensor.B64X64)  #设置像素大小
    #sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 1000)     # WARNING: If you use QQVGA it may take seconds
                    # to process a frame sometimes.

def rec_init():
    #sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(10)
    #sensor.set_auto_whitebal(False)
    #sensor.set_windowing([0,20,80,40])
    sensor.skip_frames(time = 1000)     # WARNING: If you use QQVGA it may take seconds
                    # to process a frame sometimes.


def rec_num():
    result=-1
    roi=[]
    img = sensor.snapshot().binary([black_threshold]).lens_corr(strength = 1.9, zoom = 0.9)
    #img.lengths_corr(DISTORTION_FACTOR)  #进行镜头畸形矫正，里面的参数是进行鱼眼矫正的程度
    img.dilate(1)
    img.erode(1)
    img.dilate(1)
    roi=cut_num(img)
    #print(micropython.mem_info())
    rect_num=int(len(roi)/4)
    print("ge",rect_num)
    if rect_num==1 or rect_num==2 or rect_num==4:
        result=[]
        for i in range (0,rect_num):
            x=roi[0+4*i]
            y=roi[1+4*i]
            w=roi[2+4*i]
            h=roi[3+4*i]
            #print("w",roi[2])
            #print("h",h)
            num3556=density(img,x,y,w,h,3/8,5/8,5/8,6/8)
            num0335=density(img,x,y,w,h,0/8,3/8,3/8,5/8)
            num7868=density(img,x,y,w,h,7/8,8/8,6/8,8/8)
            num0246=density(img,x,y,w,h,0/8,2/8,4/8,6/8)
            num0135=density(img,x,y,w,h,0/8,1/8,3/8,5/8)
            num2556=density(img,x,y,w,h,2/8,5/8,5/8,6/8)
            num7856=density(img,x,y,w,h,7/8,8/8,5/8,6/8)
            num4823=density(img,x,y,w,h,4/8,8/8,3/16,5/16)
            num0867=density(img,x,y,w,h,12/16,14/16,0/8,8/8)
            num0246=density(img,x,y,w,h,0/8,2/8,4/8,6/8)
            #print("num1",num4823)
            #print("num2",num0335)
            #print("num3",num0246)
            #print("num4",num0246)
            #print("num5",num0867)
            if h>2.3*w or (num0867>0.65 and num0246<0.15):
                result.append([x,1])
            elif num3556<0.1 and num0335<0.1:
                result.append([x,3])
            elif num3556>0.4 and num0335>0.3:
                result.append([x,4])
            elif num2556>0.2 and num0335<0.2 and num7868<0.1:
                result.append([x,7])
            elif num3556>0.3 and num0335<0.25 and num7856<0.15:
                result.append([x,2])
            elif num3556<0.2 and num0246<0.4 and num4823<0.2:
                result.append([x,5])
            elif num0135>0.8:
                result.append([x,6])
            elif num0135<0.6:
                result.append([x,8])
            else:
                result.append([x,1])
            #print(result)
        bubble_sort(result)
        sent=''
        for i in range(0,4):
            if result[i][1]:
                sent=sent+str(result[i][1])
            else:
                sent=sent+'9'
        uart.write(sent)
        #print(clock.fps())
        return result

clock = time.clock()
rec_init()
while(1):
    list=[]
    #rec_init()
    list=rec_num()
    if list:
        mode=1
        print("NUM",list)
    else:
        rec_num()
    xunxian()




    #print(clock.fps())






