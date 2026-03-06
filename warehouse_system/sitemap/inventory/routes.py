from flask import Blueprint, render_template, request, jsonify
from utils.decorators import login_required
from modules.services import Services

inventory_blueprint = Blueprint("inventory", __name__, template_folder="/workspaces/NEA/warehouse_system/templates")

@inventory_blueprint.route("/inventory", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        filter_type = request.args.get("filter", "all")
        
        products = Services.inventory.fetch_inventory(filter_type)

        return render_template(
            "inventory.html",
            inventory=products,
            filter=filter_type
        )

    data = request.get_json()
    print("POST action data:", data)

    # Example: receiving new pallets
    action = data.get("action")
    if action == "receive_stock":
        product_id = data.get("product_id")
        pallets = data.get("pallets")  # list of dicts: {quantity, location_id}

        success = Services.inventory.receive_stock(product_id, pallets)
        if success:
            return jsonify({"success": True, "message": "Stock received"})
        else:
            return jsonify({"success": False, "message": "Failed to receive stock"})

    return jsonify({"success": False, "message": "Unknown action"})

@inventory_blueprint.route("/inventory/search")
@login_required
def search_products():
    query = request.args.get("q", "")

    if not query:
        return jsonify([])

    results = Services.inventory.search_products(query)

    return jsonify(results)