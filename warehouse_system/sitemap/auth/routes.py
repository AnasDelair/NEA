from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from modules.services import Services

auth_blueprint = Blueprint("auth", __name__, template_folder="/workspaces/NEA/warehouse_system/templates")

@auth_blueprint.route("/login", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for("homepage"))
        else:
            return render_template("login.html")

    data = request.get_json()
    password_input = data.get("password")
    
    success = Services.auth.authenticate(password_input)

    if success:
        session["logged_in"] = True
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "message": "Incorrect password."})

@auth_blueprint.route("/logout")
def logout():
    return "Log Out"