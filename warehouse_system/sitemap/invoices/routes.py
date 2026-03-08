from flask import Blueprint, render_template, request, jsonify
from utils.decorators import login_required
from modules.services import Services

invoices_blueprint = Blueprint(
    "invoices",
    __name__,
    template_folder="/workspaces/NEA/warehouse_system/templates"
)


@invoices_blueprint.route("/invoices")
@login_required
def index():
    filter_type = request.args.get("filter", "all")

    if filter_type == "customers":
        customers = Services.invoice.fetch_customer_list()
        return render_template("invoices.html", filter=filter_type, invoices=[], customers=customers)

    invoices = Services.invoice.fetch_invoices(filter_type)
    return render_template("invoices.html", filter=filter_type, invoices=invoices, customers=[])


@invoices_blueprint.route("/invoices/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    results = Services.invoice.search_invoices(q)
    return jsonify(results)


@invoices_blueprint.route("/invoices/customers_dropdown")
@login_required
def customers_dropdown():
    customers = Services.invoice.fetch_customers_dropdown()
    return jsonify(customers)


@invoices_blueprint.route("/invoices/product_lookup")
@login_required
def product_lookup():
    stock_code = request.args.get("stock_code", "").strip()
    if not stock_code:
        return jsonify({"success": False, "error": "No stock code provided"}), 400
    product = Services.invoice.fetch_product_by_stock_code(stock_code)
    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404
    return jsonify({"success": True, "product": product})


@invoices_blueprint.route("/invoices/create", methods=["POST"])
@login_required
def create_invoice():
    data = request.json
    customer_id = data.get("customer_id")
    items = data.get("items")       # [{"product_id", "quantity", "price_each"}, ...]
    status = data.get("status")     # "draft" or "open"
    due_date = data.get("due_date")

    if not all([customer_id, items, status, due_date]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    if status not in ("draft", "open"):
        return jsonify({"success": False, "error": "Invalid status"}), 400

    result = Services.invoice.create_invoice(customer_id, items, status, due_date)
    if result is False:
        return jsonify({"success": False, "error": "Insufficient stock for one or more items"}), 400

    return jsonify({"success": True, "invoice_id": result})


@invoices_blueprint.route("/invoices/<int:invoice_id>/mark_paid", methods=["POST"])
@login_required
def mark_paid(invoice_id):
    success = Services.invoice.mark_paid(invoice_id)
    if not success:
        return jsonify({"success": False, "error": "Invoice not found or already paid"}), 400
    return jsonify({"success": True})


@invoices_blueprint.route("/invoices/<int:invoice_id>/delete", methods=["POST"])
@login_required
def delete_invoice(invoice_id):
    success = Services.invoice.delete_invoice(invoice_id)
    if not success:
        return jsonify({"success": False, "error": "Invoice not found"}), 404
    return jsonify({"success": True})


@invoices_blueprint.route("/invoices/<int:invoice_id>/open", methods=["POST"])
@login_required
def open_invoice(invoice_id):
    success = Services.invoice.save_draft_as_open(invoice_id)
    if not success:
        return jsonify({"success": False, "error": "Could not open invoice — check stock levels"}), 400
    return jsonify({"success": True})


@invoices_blueprint.route("/invoices/add_customer", methods=["POST"])
@login_required
def add_customer():
    data = request.json
    name = data.get("name", "").strip()
    address = data.get("address", "").strip()
    contact_number = data.get("contact_number", "").strip()

    if not name:
        return jsonify({"success": False, "error": "Name is required"}), 400

    customer_id = Services.invoice.add_customer(name, address, contact_number)
    return jsonify({"success": True, "customer_id": customer_id})