#Test the camera via the command line
raspistill -o Desktop/image.jpg


#Take images from camera Raspberry pi for testing
from picamera import PiCamera
from time import sleep

#Loop to take thirty pictures in a row
camera = PiCamera()
camera.start_preview()
for i in range(30):
    sleep(0.05)
    camera.capture('/home/pi/Desktop/image%s.jpg' % i)
camera.stop_preview()
