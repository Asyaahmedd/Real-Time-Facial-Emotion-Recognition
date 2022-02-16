#Import resources and create up a Button conncted to pin 3 

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
Button = 3
GPIO.setup(Button,GPIO.IN,pull_up_down=GPIO.PUD_UP)


#Loop to keep taking pictures every time the button is pressed
while True:
    button_state = GPIO.input(Button)
    if button_state ==False:
        camera.start_preview()
        sleep(5)
        camera.capture('/home/pi/Desktop/image.jpg')
    if button_state == True:
        camera.stop_preview()
    sleep(1)