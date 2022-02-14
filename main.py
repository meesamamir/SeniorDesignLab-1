from flask import Flask, render_template, request

#tri
####
#tri & meesamA
app = Flask(__name__)
app.config['SECRET_KEY'] = "asdcbsxnxacdaskchds" #encrypts cookies and session data related to website, it can be whatever we want

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")




if __name__ == '__main__':
    app.run(debug=True)  # update flask server with changes we make