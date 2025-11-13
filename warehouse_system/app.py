from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "temp_secure_key"

@app.route("/")
def homepage():
    return "test app working"

if __name__ == "__main__":
    app.run()