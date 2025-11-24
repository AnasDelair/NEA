from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from utils.decorators import login_required

invoices_blueprint = Blueprint("invoices", __name__, template_folder="/workspaces/NEA/warehouse_system/templates")

@invoices_blueprint.route("/invoices", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("invoices.html")

    data = request.get_json()
    print("POST", data)
