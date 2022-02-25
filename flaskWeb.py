from flask import Flask, render_template, request, redirect, url_for, make_response
import pyrebase

app = Flask(__name__)
app.config['SECRET_KEY'] = "asdcbsxnxacdaskchds" #encrypts cookies and session data related to website, it can be whatever we want

#TODO:
# 3. Scale the graph (small, medium, large)
# 4. handling overly high temp or overly low temp
# 5. push to github and host to heroku

config = {
  "apiKey": "UQRozP504TUPpyaneeiagExDT8fdp6jj3piA7G7Q",
  "authDomain": "team6lab1.firebaseapp.com",
  "databaseURL": "https://team6lab1-default-rtdb.firebaseio.com",
  "storageBucket": "team6lab1.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

global_temp = "fahrenheit"

# Routes
@app.route("/", methods=["GET","POST"])
def home():
    return render_template("home.html", tempC = getTempC(), 
    tempF = getTempF(), temp = getTemp(), virtualButton = getVirtualButton(), 
    sensor = getSensor(), switch= getSwitch())

# switch the button state ON/OFF
@app.route("/push", methods=["POST"])
def push():
    currentVB = getVirtualButton()
    if currentVB == "False":
        currentVB = "True"
    else:
        currentVB = "False"
    setVirtualButton(currentVB)
    data = {"button":currentVB}
    response = make_response(data)
    response.content_type = 'application/json'
    return response

# switch between C and F
@app.route("/switchTemp", methods=["POST"])
def switchTemp():
    global global_temp
    if global_temp == "fahrenheit":
        global_temp = "celcius"
    else:
        global_temp = "fahrenheit"
    data = {"metric":global_temp}
    response = make_response(data)
    response.content_type = 'application/json'
    return response

@app.route("/setData", methods=["POST"])
def setData():
    metric = request.form["metric"]
    maxTemp = request.form["maxTemp"]
    minTemp = request.form["minTemp"]
    phoneNumber = request.form["phoneNumber"]
    maxTempC , minTempC, maxTempF, minTempF = 0 ,0 ,0 ,0
    if metric == "c":
        maxTempC = maxTemp
        minTempC = minTemp 
        maxTempF = str((float(maxTemp) * (9/5)) + 32)
        minTempF = str((float(minTemp) * (9/5)) + 32)
    else:
        maxTempC = str((float(maxTemp) - 32) * (5/9))
        minTempC = str((float(minTemp) - 32) * (5/9))
        maxTempF = maxTemp
        minTempF = minTemp
    db.child("Status").child("MaxTempC").set(maxTempC)
    db.child("Status").child("MinTempC").set(minTempC)
    db.child("Status").child("MaxTempF").set(maxTempF)
    db.child("Status").child("MinTempF").set(minTempF)
    db.child("Status").child("PhoneNumber").set(phoneNumber)
    data = {"message":"success"}
    response = make_response(data)
    response.content_type = 'application/json'
    return response

    

@app.route('/temp', methods=["GET"])
def temp():
    metric = getTemp()
    tempC = getTempC()
    tempF = getTempF()

    data = {"tempC": str(tempC), "tempF": str(tempF), "metric": metric, "sensor":getSensor(), "switch":getSwitch()}

    response = make_response(data)

    response.content_type = 'application/json'

    return response

# Methods 

def getTempC():
    tempC = db.child("Temperatures").child("TempC").get().val()
    return tempC

def getTempF():
    tempF = db.child("Temperatures").child("TempF").get().val()
    return tempF

def getSwitch():
    switch = db.child("Status").child("Switch").get().val()
    return switch

def getSensor():
    sensor = db.child("Status").child("Sensor").get().val()
    return sensor

def getTemp():
    return global_temp

def getVirtualButton():
    virtualButton = db.child("Status").child("VirtualButton").get().val()
    return virtualButton

def setVirtualButton(st):
    db.child("Status").child("VirtualButton").set(st)
    return

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")

if __name__ == '__main__':
    app.run(debug=True)  # update flask server with changes we make


