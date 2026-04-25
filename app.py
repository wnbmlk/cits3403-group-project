from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/diary")
def diary():
    return render_template("diary.html")

if __name__ == "__main__":
    app.run(debug=True)