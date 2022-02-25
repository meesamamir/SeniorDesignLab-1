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


'''  Configuring LCD  '''

lcd_display = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)

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

# ADD A CHECK TO SEE IF SENSOR GOT DISCONNECTED OR NOT

# Look for temperature sensor

while True:
    try:
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0] 
        device_file = device_folder + '/w1_slave'
        break
    except:
        lcd.write_string("Sensor not connected!")
        db.child("Status").child("Sensor").set("False")
   

# Set status of the sensor to True, indicating that it's working
db.child("Status").child("Sensor").set("True")

# Read-in raw temperature data
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
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_f = (int(temp_string) / 1000.0) * 9.0 # TEMP_STRING IS THE SENSOR OUTPUT, MAKE SURE IT'S AN INTEGER TO DO THE MATH
        temp_f = str(round(temp_f, 1)) # ROUND THE RESULT TO 1 PLACE AFTER THE DECIMAL, THEN CONVERT IT TO A STRING
        return temp_f

'''                   Firebase database initialization and sending temperature data                       '''
config = {
  "apiKey": "UQRozP504TUPpyaneeiagExDT8fdp6jj3piA7G7Q",
  "authDomain": "team6lab1.firebaseapp.com",
  "databaseURL": "https://team6lab1-default-rtdb.firebaseio.com",
  "storageBucket": "team6lab1.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def extremeTemp():
    '''This function pulls data from the web interface for max/min temperatures which will be our extreme temperatures.     
    Returns True if current temperature sensed by sensor is above/below set temperatures'''

    maxTempC = db.child("Status").child("MaxTempC").get().val()
    minTempC = db.child("Status").child("MinTempC").get().val()

    maxTempF = db.child("Status").child("MaxTempF").get().val()
    minTempF = db.child("Status").child("MinTempF").get().val()
    
    if ((int(read_temp_c) > maxTempC) or (int(read_temp_c) < minTempC)) or ((int(read_temp_f) > maxTempF) or (int(read_temp_f) < minTempF)):
        return True
    else:
        return False

def sendSms(toNumber):
    '''Takes phone number as arg to the function and sends extreme temperatures sms notification to that phone number'''

    account_sid = 'ACc948439e80f605cc32693f38bc027052' 
    auth_token = 'cf7066bd5f2f2446e4a2b8f9094a2d5e' 
    client = Client(account_sid, auth_token) 
    
    client.messages.create(  
                              messaging_service_sid='+13194320147',       
                              to=str(toNumber),
                              body= "Extreme temperature reached: " + read_temp_c() + chr(223) + "C" + " / " + read_temp_f() + chr(223) + "F" 
                    ) 

# Main while loop
while True:
    
    while True:
        try:
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28*')[0] 
            device_file = device_folder + '/w1_slave'
        except:
            lcd.write_string("Sensor not connected!")
            db.child("Status").child("Sensor").set("False")

            db.child("Temperatures").child("TempC").set("False")
            db.child("Temperatures").child("TempF").set("False")

        else:
            db.child("Status").child("Sensor").set("True")
            break

    if extremeTemp:
        phoneNumber = db.child("Status").child("PhoneNumber").get().val() 
        sendSms(phoneNumber)

    if switch.is_pressed:
        led.on
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

        db.child("Temperatures").set(temperatureData)

        print("TempC = " , db.child("Temperatures").child("TempC").get().val() )
    
    else:
        led.off
        db.child("Temperatures").child("TempC").set("False")
        db.child("Temperatures").child("TempF").set("False")

GPIO.cleanup() # cleanup all GPIO
lcd.clear()







# if button.is_pressed or (db.child("Status").child("VirtualButton").get().val() == "True") :
    #     lcd.cursor_pos = (0, 0)    
    #     lcd.write_string("Temp: " + read_temp_c() + chr(223) + "C")
    #     lcd.cursor_pos = (1, 0)
    #     lcd.write_string("Temp: " + read_temp_f() + chr(223) + "F")

    #     stateIO = {
    #         "Button" : "True"
    #         #"Switch" : switchState
    #     }

    # else:
    #     lcd.clear()
        
    #     lcd_display.backlight_enabled = False

    #     stateIO = {
    #         "Button" : "False"
    #         #"Switch" : switchState
    #     }

    # db.child("States").set(stateIO)


    # # firbase method send temp_C to firebase 
    # temperatureData = {
    #     "TempC": read_temp_c(),
    #     "TempF": read_temp_f(), 
    #     "Time" : time.time()
    # }

    # db.child("Temperatures").set(temperatureData)


    # print(db.child("Temperatures").child("TempC").get().val() )