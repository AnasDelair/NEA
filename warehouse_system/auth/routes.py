from flask import Blueprint, render_template, request, redirect, url_for, session

auth_blueprint = Blueprint("auth", __name__, template_folder="/workspaces/NEA/warehouse_system/templates")

@auth_blueprint.route("/login")
def login():
    return render_template("login.html")