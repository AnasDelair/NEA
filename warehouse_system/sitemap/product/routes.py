from flask import Blueprint, render_template
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