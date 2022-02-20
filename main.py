# trisentosa, meesamA
# SeniorDesign Lab 1

'''         THIS FILE IS TO BE RUN ON THE RASPBERRY PI
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
import gpiozero     # https://gpiozero.readthedocs.io/en/stable/index.html
import pyrebase

'''  Configuring LCD  '''

lcd_display = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)

'''  Button/Switch states  '''
# Using buttons with raspberry pi:  https://gpiozero.readthedocs.io/en/v1.1.0/api_input.html
#                                   https://roboticadiy.com/connect-push-button-with-raspberry-pi-4/
#                                   https://www.rototron.info/using-an-lcd-display-with-inputs-interrupts-on-raspberry-pi/

# Connect button to GPIO17  - BUY JUMPER CABLES MALE-TO-FEMALE
button = gpiozero.Button(17)
buttonState = False

# Connect switch to GPIO27
switch = gpiozero.Button(27)
switchState = False


'''                 Connecting to temp sensor and retrieving data                   '''

# Start/Initialize the GPIO Pins
os.system('modprobe w1-gpio')  # Turns on the GPIO module
os.system('modprobe w1-therm') # Turns on the Temperature module

# ADD A CHECK TO SEE IF SENSOR GOT DISCONNECTED OR NOT

# Look for temperature sensor
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0] 
device_file = device_folder + '/w1_slave'

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

# Following needs to be in while loop to update continuously 
temperatureData = {
    "TempC": read_temp_c(),
    "TempF": read_temp_f(),
}
# state of the button and switches
# stateIO = {
#     "Button": buttonState,
#     "Switch": switchState
# }
db.child("Temperatures").set(temperatureData)
# db.child("States").set(stateIO)


time.sleep(1)

# firbase method send temp_C to firebase 

while True:
    # Print temp to LCD
    lcd.cursor_pos = (0, 0)    
    lcd.write_string("Temp: " + read_temp_c() + chr(223) + "C")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Temp: " + read_temp_f() + chr(223) + "F")
    
    temperatureData = {
        "TempC": read_temp_c(),
        "TempF": read_temp_f(),  
    }
    db.child("Temperatures").set(temperatureData)

    print(db.child("Temperatures").child("TempC").get().val() )

    time.sleep(1)


GPIO.cleanup() # cleanup all GPIO
lcd.clear()
