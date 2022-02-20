from flask import Flask, render_template, request
import pyrebase

app = Flask(__name__)
app.config['SECRET_KEY'] = "asdcbsxnxacdaskchds" #encrypts cookies and session data related to website, it can be whatever we want


config = {
  "apiKey": "UQRozP504TUPpyaneeiagExDT8fdp6jj3piA7G7Q",
  "authDomain": "team6lab1.firebaseapp.com",
  "databaseURL": "https://team6lab1-default-rtdb.firebaseio.com",
  "storageBucket": "team6lab1.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

virtualButton = False


# Routes

@app.route("/")
def home():
    return render_template("home.html", tempC = getTempC(), tempF = getTempF())

# @app.route("/results", methods= ["POST", "GET"])
# def results():
#     # integer = request.form.get("int_input")
#     # return render_template("home.html", results = getTempC())
#     return render_template("home.html")

def getTempC():
    tempC = db.child("Temperatures").child("TempC").get().val() + "°" + "C"
    return tempC

def getTempF():
    tempF = db.child("Temperatures").child("TempF").get().val() + "°" + "F"
    return tempF


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")


if __name__ == '__main__':
    app.run(debug=True)  # update flask server with changes we make


