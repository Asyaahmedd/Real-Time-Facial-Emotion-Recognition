# import libraries
import numpy as np
import cv2
from PIL import Image 

import tflite_runtime.interpreter as tflite

import time
import os

# Raspberypi Python Model
import picamera
import RPi.GPIO as GPIO  
  


####### variables  initialization ######

# Global variables
STATE_FLAGE = False
GLOBAL_QUOTE = ""

# Store quotes on dictionary
my_dict = {}
my_dict["happy"] = [['I accept that', 'happiness is my', 'true nature'],
                   ['I am worthy of', 'feeling happy'],
                   ['Joy is the essence', 'of my being'],
                   ['I feel happy with', 'myself as a person'],
                   ['I experience joy in', 'everything I do'],
                   ['My choice to be', 'happy keeps me in', 'a perfect health'],
                   ['Good things belong', 'to me']]
                   
my_dict['sad']=[['You are in charge', 'of your happiness'],
               ['You have made it', 'this far, Do not', 'stop now'],
               ['You are resilient', 'in the face of any', 'challenge'],
               ['Everything will', 'work out perfect', 'for you'],
               ['You deserve love,', 'joy, and happiness'],
               ['You deserve', 'everything good'],
               ['No one is perfect,', 'forgive yourself'],
               ['You can handle this'],
               ['With time and', 'effort, you will be', 'better']]

my_dict['angry']= [['Acknowledge your', 'feelings without', 'losing control'],
                  ['Breathe deeply'],
                  ['Release your anger,', 'choose peace'],
                  ['Take a break if you', 'need'],
                  ['Take a step back', 'and remain in', 'control']]

my_dict["neutral"] = [['Comfort is in', 'expressing your', 'emotions.'],
                     ['Release', 'your feelings'],
                     ['Express', 'your feelings'],
                     ['Do not let life', 'shut you up']] 


my_dict["surprise"] = [['ohh, seems', 'something good has', 'happened'],
                      ['Let life surprise', 'you'],
                      ['Surprise is the', 'greatest gift which', 'life can grant us'],
                      ['Sometimes,', 'surprises are the', 'best'],
                      ['There is some sort', 'of magic in the', 'unexpected']]

mapping = {0:'angry',1:'happy',2:'neutral',3:'sad',4:'surprise'}



def loadModel(fileName):
    """ 
      This function take model path to load then return  
    
    Parameter:
      fileName: str refere to model path 

    Return:
      interpreter model

    """

    interpreter = tflite.Interpreter(model_path=fileName)
    interpreter.allocate_tensors()
    
    return interpreter

def showQuote(LCD , label = None ):
    """
      Show quote of specific emotion if found OR show random Quotes on LCD
      
      Parameter :
        LCD : LCD_LINE  object to show qoutes on LCD
        label : str type refere to emotion type 
    """

    global STATE_FLAGE 
    global GLOBAL_QUOTE

    if label :
        # show quotes of this label
        rand = np.random.randint(0,len(my_dict[label]))
        quotes = my_dict[label][rand] 
        # loop over all quotes of this emotion = label
        for i in  range(len(quotes))  :
            #  print on LCD 
           lcd_string(quotes[i] , LCD[i])
           print(quotes[i])
        
    else:
        # show random quotes
        temp_quotes = GLOBAL_QUOTE

        while GLOBAL_QUOTE == temp_quotes:
              
            rand = np.random.randint(0,5)
            label = mapping[rand]
            quotes = my_dict[label][np.random.randint(0,len(my_dict[label]))]  # must send this list to function to show on LCD
            temp_quotes = "".join(quotes)
            
        # loop over all quotes of this emotion = label
        for i in  range(len(quotes)) :
            lcd_string(quotes[i] , LCD[i])
            print(quotes[i])

        # loop to add sleep (9000000 ~= 4.5s) and read button state     
        for i in range(9000000):
            state =  GPIO.input(button)
            # break if button clicked
            if not state:
                  
                STATE_FLAGE= True
                break        
                
        GLOBAL_QUOTE = temp_quotes        

# ectract face from one image
def extract_face(filename, required_size=(112,92)):
    """
        extract face from image
      Parameter :
         filename : str for image path 
         required_size: image resizing factor
      Return :
         numpy array of image OR None if Extraction Failed 
           
    """
      
    image = Image.open(filename)
    gray_img = cv2.cvtColor(np.float32(image), cv2.COLOR_BGR2GRAY)
    try:
        
      haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
      faces_rect = haar_cascade.detectMultiScale(np.array(gray_img, dtype='uint8'), scaleFactor=1.1, minNeighbors=9)
      (x,y,w,h)=faces_rect[0]  
      pixels = np.asarray(image)
      faces = pixels[y:y + h, x:x + w]
      image = Image.fromarray(faces)
      image = image.convert('RGB')
      image = image.resize(required_size)
      face_array = np.asarray(image)

    except:
      return None
      
    return face_array
 
def predict(fileName,interpreter):
    """
        This function make a prediction to get image emotion
        
      Parameter:
        fileName : str refere to model path 
        interpreter: tflite_runtime.interpreter model 
      Return:
        label of image emotion or just message if prediction Failed 

    """  
  
    input_details = interpreter.get_input_details()[0]['index']
    output_details = interpreter.get_output_details()[0]['index'] 
    
    output = extract_face(fileName)
    if output is None :
      return "Can't Find Your Face !!"
      
    # face = Image.fromarray(output)
    img_array = np.array(output,dtype=np.float32)
    img_batch = np.expand_dims(img_array, axis=0)
      
    interpreter.set_tensor(input_details, img_batch)
    interpreter.invoke()

    predictions=interpreter.get_tensor(output_details)
    label = np.argmax(predictions)

    predicted_label = mapping[label] 
    print(predicted_label)

    return predicted_label


# ######   LCD  Variables  #######

# Define GPIO to LCD mapping
# Define GPIO to LCD mapping
LCD_RS = 26
LCD_E  = 24
LCD_D4 = 22
LCD_D5 = 18
LCD_D6 = 16
LCD_D7 = 12
 
# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE = [0x80 , 0xC0 ,0x94 , 0xD4] 

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_toggle_enable():
    # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)



def lcd_byte(bits, mode):

  GPIO.output(LCD_RS, mode) 
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 

def lcd_init():
      
      # Initialise LCD
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_string(message,line):
      
  """ Send string to display"""
 
  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_main():
      # Main program block
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
 
  # Initialise display
  lcd_init()

def lcd_clear():

  """ Delete LCD Screen  """

  for i in range(4):
    lcd_string("",LCD_LINE[i])


# Model Loading 
interpreter = loadModel("./model.tflite")
button = 3   # 3 refere to Pin Number on Raspberrypi BOARD

# take photo  
def take_phote(camera):
    """
      function to capture photo using camera and save it specific path 

      Parameters : 
        camera : PiCamera Object

      Return :
        path of captured image  

    """
    image_path = "/home/pi/project/frame.jpg"
    counter = 0

    if  os.path.exists(image_path) :
        os.remove(image_path)

    while not os.path.exists(image_path):
        camera.capture('./frame.jpg')
        counter+=1

        if counter >=5:
            return None

    return image_path 


def setup():
      # Button Setup on RespberryPi Board
       GPIO.setmode(GPIO.BOARD)
       GPIO.setup(button, GPIO.IN) 
  
def loop():
      # this STATE_FLAGE to handle case if button pressed during random Quotes showing
        global STATE_FLAGE
        
        while True:
            # read button state 
            button_state = GPIO.input(button)
            #clear LCD from previous Output 
            lcd_clear()
            # start Random Quotes
            showQuote(LCD = LCD_LINE)

            if  button_state == False or STATE_FLAGE == True:
                STATE_FLAGE = False  
                print('Button Pressed…')
                lcd_clear()
                # to close camera after photo capturing
                with picamera.PiCamera() as camera : 
                    image_path = take_phote(camera)

                    if image_path:
                        label = predict(image_path , interpreter)
                        
                        lcd_string (label ,LCD_LINE[0])
                        time.sleep(2)

                        # if label not an emotion ( Face Extraction Failed )
                        if label not in my_dict.keys():
                          continue
                       
                        showQuote(LCD = LCD_LINE , label = label)
                        time.sleep(2)
                    else:
                        print("Taking Photo Fail")   


def endprogram():
    GPIO.cleanup()

if __name__ == '__main__':
         setup()
         lcd_main()
         try:
                 loop()
         except KeyboardInterrupt:
                 print('keyboard interrupt detected')
                 endprogram()

