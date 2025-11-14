from flask import Flask, render_template, redirect, url_for, session
from auth.routes import auth_blueprint
from utils.decorators import login_required

app = Flask(__name__, template_folder="/workspaces/NEA/warehouse_system/templates", static_folder='/workspaces/NEA/warehouse_system/static')
app.secret_key = "temp_secure_key"

app.register_blueprint(auth_blueprint)

@app.route("/")
@login_required
def homepage():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)