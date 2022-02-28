# trisentosa, meesam, som, jessie
# SeniorDesign Lab 1

'''    THIS FILE IS TO BE RUN ON THE RASPBERRY PI
- create a new python file in the root directory of the raspi using "nano test.py"
- copy all the code below and paste it in test.py, now save it
- run the python file from root directory using "python test.py"
'''
import os
import glob
import time
import datetime
import RPi.GPIO as GPIO
from RPLCD import CharLCD
from gpiozero import Button, LED    # https://gpiozero.readthedocs.io/en/stable/index.html
import pyrebase
from twilio.rest import Client
from dotenv import load_dotenv

#Env Variable
load_dotenv()
TWILIO_TOKEN = os.getenv("TWILLIO_TOKEN")
TWILLIO_SID = os.getenv("TWILLIO_SID")
FIREBASE_KEY = os.getenv("FIREBASE_KEY")

'''  Configuring LCD  '''

lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)

'''  Button/Switch states  '''
# Using buttons with raspberry pi:  https://gpiozero.readthedocs.io/en/v1.1.0/api_input.html
#                                   https://roboticadiy.com/connect-push-button-with-raspberry-pi-4/
#                                   https://www.rototron.info/using-an-lcd-display-with-inputs-interrupts-on-raspberry-pi/

# Connect button to GPIO2  
button = Button(2)
#buttonState = False

# Connect switch to GPIO17
switch = Button(17)
# switchState = False

# lED connected to GPIO27
led = LED(27)


'''                 Connecting to temp sensor and retrieving data                   '''

# Start/Initialize the GPIO Pins
os.system('modprobe w1-gpio')  # Turns on the GPIO module
os.system('modprobe w1-therm') # Turns on the Temperature module

'''                   Firebase database initialization and sending temperature data                       '''
config = {
  "apiKey": FIREBASE_KEY,
  "authDomain": "team6lab1.firebaseapp.com",
  "databaseURL": "https://team6lab1-default-rtdb.firebaseio.com",
  "storageBucket": "team6lab1.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Set status of the sensor to True, indicating that it's working
db.child("Status").child("Sensor").set("True")

# Main while loop
while True:
    
    while True:
        try:
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28*')[0] 
            device_file = device_folder + '/w1_slave'
        except:
            lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33,31,29,23], numbering_mode=GPIO.BOARD, auto_linebreaks=True)
            lcd.write_string("Sensor unplugged")
            db.child("Status").child("Sensor").set("False")
           
            db.child("Temperatures").child("TempC").set("False")
            db.child("Temperatures").child("TempF").set("False")
            continue
        else:
            lcd.clear
            db.child("Status").child("Sensor").set("True")
            break

    def read_temp_raw():
        f = open(device_file, 'r') 
        lines = f.readlines() 
        f.close()
        return lines
    # Converting raw temperature data from the sensor to temperature in Celsius and Fahrenheit
    # CELSIUS CALCULATION
    def read_temp_c():
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
              time.sleep(0.2)
              lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
           temp_string = lines[1][equals_pos+2:]
           temp_c = int(temp_string) / 1000.0 # TEMP_STRING IS THE SENSOR OUTPUT, MAKE SURE IT'S AN INTEGER TO DO THE MATH
           temp_c = str(round(temp_c, 1))  # ROUND THE RESULT TO 1 PLACE AFTER THE DECIMAL, THEN CONVERT IT TO A STRING
           return temp_c

    #  FAHRENHEIT CALCULATION
    def read_temp_f():
        temp_f = round(((float(read_temp_c())*9/5)+32),1)
        return str(temp_f)

    maxTempC = db.child("Status").child("MaxTempC").get().val()
    minTempC = db.child("Status").child("MinTempC").get().val()
    maxTempF = db.child("Status").child("MaxTempF").get().val()
    minTempF = db.child("Status").child("MinTempF").get().val()

    def highTemp():
        '''This function pulls data from the web interface for max/min temperatures which will be our extreme temperatures.     
           Returns True if current temperature sensed by sensor is above/below set temperatures'''

        if (float(read_temp_c()) > float(maxTempC)) or (float(read_temp_f()) > float(maxTempF)):
           return True
        else:
           return False
    def lowTemp():
        if (float(read_temp_c()) < float(minTempC)) or (float(read_temp_f()) < float(minTempF)):
           return True
        else:
           return False

    def sendSms(toNumber):
        '''Takes phone number as arg to the function and sends extreme temperatures sms notification to that phone number'''

        account_sid = TWILLIO_SID 
        auth_token = TWILLIO_TOKEN
        client = Client(account_sid, auth_token) 
   
        if highTemp():
           client.messages.create(  
           messaging_service_sid='MG1d68b0889c53c0e566a20d215b56b359',       
           to=str(toNumber),
           body= "🥵 High temperature reached: " + read_temp_c() + "°" + "C" + " / " + read_temp_f() + "°" + "F" )
        elif lowTemp():
             client.messages.create(  
             messaging_service_sid='MG1d68b0889c53c0e566a20d215b56b359',       
             to=str(toNumber),
             body= "🥶 Low temperature reached: " + read_temp_c() + "°" + "C" + " / " + read_temp_f() + "°" + "F"             
            )
  
    if highTemp() or lowTemp():
        phoneNumber = db.child("Status").child("PhoneNumber").get().val() 
        sendSms(phoneNumber)

    if switch.is_pressed and (db.child("Status").child("Sensor").get().val() == "True"):
        led.on()
        db.child("Status").child("Switch").set("True")
        if button.is_pressed or (db.child("Status").child("VirtualButton").get().val() == "True") :
            #lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33,31,29,23], numbering_mode=GPIO.BOARD, auto_linebreaks=False, backlight_enabled=Tru>
            lcd.cursor_pos = (0, 0)    
            lcd.write_string("Temp: " + read_temp_c() + chr(223) + "C")
            lcd.cursor_pos = (1, 0)
            lcd.write_string("Temp: " + read_temp_f() + chr(223) + "F")

            stateIO = {
                "Button" : "True"
                #"Switch" : switchState
            }

        elif not (button.is_pressed):
            lcd.clear()
            lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33,31,29,23], numbering_mode=GPIO.BOARD, auto_linebreaks=False, backlight_enabled=False)
            stateIO = {
                "Button" : "False"
                #"Switch" : switchState
            }

        db.child("States").set(stateIO)

        temperatureData = {
            "TempC": read_temp_c(),
            "TempF": read_temp_f(), 
            "Time" : time.time()
        }

        print("TempC = " , db.child("Temperatures").child("TempC").get().val() )
        print("TempC = " , db.child("Temperatures").child("TempF").get().val() )

        db.child("Temperatures").set(temperatureData)
    
    elif (switch.is_pressed) and (db.child("Status").child("Sensor").get().val() == "False"):
        led.on()
        db.child("Status").child("Sensor").set("False")

        lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33,31,29,23], numbering_mode=GPIO.BOARD, auto_linebreaks=True)
        lcd.write_string("Sensor unplugged!")

        db.child("Temperatures").child("TempC").set("False")
        db.child("Temperatures").child("TempF").set("False")

        print("TempC = " , db.child("Temperatures").child("TempC").get().val() )
        print("TempC = " , db.child("Temperatures").child("TempF").get().val() )

    else:
        led.off()
        db.child("Temperatures").child("TempC").set("False")
        db.child("Temperatures").child("TempF").set("False")

        print("TempC = " , db.child("Temperatures").child("TempC").get().val() )
        print("TempF = " , db.child("Temperatures").child("TempF").get().val() )
        
        db.child("Status").child("Switch").set("False")




