from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from utils.decorators import login_required

analytics_blueprint = Blueprint("analytics", __name__, template_folder="/workspaces/NEA/warehouse_system/templates")

@analytics_blueprint.route("/analytics", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("analytics.html")

    data = request.get_json()
    print("POST", data)
