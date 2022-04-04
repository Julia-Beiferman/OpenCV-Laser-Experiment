import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

PIXELWIDTH = 1240
PIXELHEIGHT = 1080

xarray = []
yarray = []

def IntersectionOfLaserAndGuess(GuessedDistance, DistanceFromCameraToLaser, AngleOfLaser):
    temp = math.tan(AngleOfLaser*math.pi/180.0) #tan of laser angle converted to degrees
    x = (GuessedDistance-DistanceFromCameraToLaser*temp)/temp #equation of x intercept
    return x

#given an x position, determine what the y value based on a two point line segment
def Interpolate(x1, x2, y1, y2, x):
    if x2-x1==0:
        return -1
    m = (y2-y1)/(x2-x1)
    b = y1-m*x1
    y = m*x+b
    return y

# pixnum is from 0 to PIXELWIDTH
def CalcDistance(pixnum, distance, angle):
    xarray.clear()
    yarray.clear()
    answer = 0
    DistanceFromCameraToLaser = distance # inches
    AngleOfLaser = angle # degrees
    CameraFrustrumAngle = 69.18457738 #degrees
    for guess in np.arange (1, 49,0.001): #continually check all distances from 0 to 50 in 
        xlimit = guess*math.tan(CameraFrustrumAngle/2*(math.pi/180)) #find the x limitation of the camera for the guessed target line
        xIntercept = IntersectionOfLaserAndGuess(guess, DistanceFromCameraToLaser, AngleOfLaser) #find x position of the intersection between the laser and guessed target line
        pixelNumber = int(Interpolate(-xlimit, xlimit, PIXELWIDTH, 0, xIntercept)) #find the the pixel number for the previous x position

        #ignore this
        if pixelNumber >=0 and pixelNumber<=PIXELWIDTH: 
            xarray.append(guess)
            yarray.append(pixelNumber)
    
        if int(pixnum)==int(pixelNumber): #if the pixel number of the guess = the pixel number found by opencv return the guessed distance
            answer = guess
        
    
    return answer


def nothing(x):
    pass

#Testing plots
#CalcDistance(147, 90, 18)
#plt.figure()
#plt.plot(xarray, yarray, label='linear')
#plt.legend()
#plt.draw()
#plt.show()


cap = cv2.VideoCapture(1)
cap.set(3,1240)
cap.set(4,1080)


#cv2.namedWindow('gray')
cv2.namedWindow('frame')
cv2.createTrackbar('Hlow','gray',0,255,nothing)
cv2.createTrackbar('Hhigh','gray',0,255,nothing)
cv2.createTrackbar('Slow','gray',0,255,nothing)
cv2.createTrackbar('Shigh','gray',0,255,nothing)
cv2.createTrackbar('Vlow','gray',0,255,nothing)
cv2.createTrackbar('Vhigh','gray',0,255,nothing)
cv2.createTrackbar('distance', 'frame', 1, 20, nothing)
cv2.createTrackbar('angle', 'frame', 30, 90, nothing)


kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    _, frame = cap.read()
    #horizontal_img = cv2.flip( img, 0 )
    frame = cv2.flip(frame, 1)

    blur = cv2.GaussianBlur(frame, (5,5), 0)
    #cv2.imshow('blur', blur)
    
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

   
    distance_fromcam_tolaser = cv2.getTrackbarPos('','gray')


    hlow = cv2.getTrackbarPos('Hlow','gray')
    hhigh = cv2.getTrackbarPos('Hhigh','gray')
    sslow = cv2.getTrackbarPos('Slow','gray')
    shigh = cv2.getTrackbarPos('Shigh','gray')
    vlow = cv2.getTrackbarPos('Vlow','gray')
    vhigh = cv2.getTrackbarPos('Vhigh','gray')

    distancefromcameratolaser = cv2.getTrackbarPos('distance','frame')
    angleoflaser = cv2.getTrackbarPos('angle','frame')


    #lower_red = np.array([hlow,sslow,vlow])
    #upper_red = np.array([hhigh,shigh,vhigh])
    lower_red = np.array([112,51,210])
    upper_red = np.array([230,255,255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    #mask = cv2.inRange(frame, lower_red, upper_red)
    res = cv2.bitwise_and(frame, frame, mask = mask)


########
     #morphology
   # maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
   # maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

    #cv2.imshow('mask', mask)


    #maskFinal=maskClose
    #conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    #conts=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[1]
    conts=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[1]

    cv2.drawContours(frame,conts,-1,(255,0,0),3)
    kk = len(conts)
    if kk > 1:
        kk = 1
    for i in range(kk):
        x,y,w,h=cv2.boundingRect(conts[i])
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255), 2)
       
        xx = x+w/2
        pixstr = "x="+str(int(xx))
        cv2.putText(frame, pixstr, (x,y), font, 1, (200,255,255), 2, cv2.LINE_AA)
       
        answer = CalcDistance(int(xx), distancefromcameratolaser, angleoflaser)
        if answer==0:
           mystr = 'not found'
        else:
            mystr = 'dist='+"{0:3.2f}".format(answer)+' inches'
            
        #cv2.putText(frame, pixstr, (10,50), font, 1, (200,255,255), 2, cv2.LINE_AA)
        
        cv2.putText(frame, mystr, (10,50), font, 1, (200,255,255), 2, cv2.LINE_AA)
       
######    

    cv2.line(frame, (int(PIXELWIDTH/2), 0), (int(PIXELWIDTH/2), PIXELHEIGHT), (255,255,255), 2)

    #cv2.line(res, (0,0), (150,150), (255, 255, 255), 6)

    kernel = np.ones((15,15), np.float32)/225
    #smoothed = cv2.filter2D(res, -1, kernel)
    #blur = cv2.GaussianBlur(res, (15,15), 0)
    #median = cv2.medianBlur(res,15)
    #bilateral = cv2.bilateralFilter(res, 15, 75, 75)


   
    gray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY);

  



    cv2.imshow('frame', frame)
   

    k = cv2.waitKey(5) & 0xFF

    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
