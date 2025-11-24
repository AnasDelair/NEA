from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from utils.decorators import login_required

inventory_blueprint = Blueprint("inventory", __name__, template_folder="/workspaces/NEA/warehouse_system/templates")

@inventory_blueprint.route("/inventory", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("inventory.html")

    data = request.get_json()
    print("POST", data)
