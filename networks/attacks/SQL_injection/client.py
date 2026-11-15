import os

import requests
from flask import Flask, render_template, request

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=base_dir+"\\htmls\\")

url = "http://localhost:8080/login"


@app.route("/")
def index():#home page
    return render_template("login.html")


@app.route("/login", methods=["POST"])#login request
def login():
    # Get the username and passwrod from the page
    username = request.form["username"]
    password = request.form["password"]

    data = {"username":username, "password":password}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        return render_template("success.html")
    else:
        return render_template("failed.html")


if __name__ == "__main__":
    app.run(debug=True)
    #open in http://localhost:5000
