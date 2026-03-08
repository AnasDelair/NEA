from flask import Blueprint, render_template, request, jsonify
from utils.decorators import login_required
from modules.services import Services

product_blueprint = Blueprint(
    "product",
    __name__,
    template_folder="/workspaces/NEA/warehouse_system/templates"
)


@product_blueprint.route("/product/<int:product_id>")
@login_required
def view_product(product_id):

    product = Services.inventory.fetch_product(product_id)

    if not product:
        return "Product not found", 404

    total_cost = product["total_stock"] * (product["cost_per_unit"] or 0)
    total_value = product["total_stock"] * (product["price_per_unit"] or 0)
    profit = total_value - total_cost

    margin = 0
    if total_value > 0:
        margin = (profit / total_value) * 100

    return render_template(
        "product.html",
        product=product,
        total_cost=total_cost,
        total_value=total_value,
        profit=profit,
        margin=margin
    )


@product_blueprint.route("/product/<int:product_id>/pallets", methods=["GET"])
@login_required
def get_pallets(product_id):
    """Return all pallets for this product as JSON."""
    pallets = Services.inventory.fetch_product_pallets(product_id)
    # date_stored isn't JSON-serialisable by default, convert to string
    for p in pallets:
        if p.get("date_stored"):
            p["date_stored"] = str(p["date_stored"])
    return jsonify({"pallets": pallets})


@product_blueprint.route("/product/<int:product_id>/add_stock", methods=["POST"])
@login_required
def add_stock(product_id):
    data = request.json
    total = data.get("total")
    pallets = data.get("pallets")

    if not total or not pallets or sum(pallets) != total:
        return jsonify({"success": False, "error": "Invalid total or pallets"}), 400

    success = Services.inventory.add_pallet(product_id, pallets)
    if not success:
        return jsonify({"success": False, "error": "Not enough free locations"}), 400

    return jsonify({"success": True})


@product_blueprint.route("/product/<int:product_id>/remove_stock", methods=["POST"])
@login_required
def remove_stock(product_id):
    data = request.json
    total = data.get("total")
    pallets = data.get("pallets")  # [{"pallet_id": int, "quantity": int}, ...]

    if not total or not pallets:
        return jsonify({"success": False, "error": "Missing total or pallets"}), 400

    removal_sum = sum(p.get("quantity", 0) for p in pallets)
    if removal_sum != total:
        return jsonify({"success": False, "error": "Total does not match sum of pallet quantities"}), 400

    success = Services.inventory.remove_stock(product_id, pallets)
    if not success:
        return jsonify({"success": False, "error": "Failed to remove stock"}), 400

    return jsonify({"success": True})