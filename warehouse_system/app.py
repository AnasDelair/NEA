from flask import Flask, render_template, redirect, url_for, session
from sitemap.auth.routes import auth_blueprint
from sitemap.analytics.routes import analytics_blueprint
from sitemap.invoices.routes import invoices_blueprint
from sitemap.inventory.routes import inventory_blueprint
from sitemap.warehouse.routes import warehouse_blueprint
from utils.decorators import login_required
from dotenv import load_dotenv
from os import environ as env
from modules.database import Database

load_dotenv()
db = Database()

app = Flask(__name__, template_folder="/workspaces/NEA/warehouse_system/templates", static_folder='/workspaces/NEA/warehouse_system/static')
app.secret_key = env.get("APP_SECRET_KEY")

app.register_blueprint(auth_blueprint)
app.register_blueprint(analytics_blueprint)
app.register_blueprint(invoices_blueprint)
app.register_blueprint(inventory_blueprint)
app.register_blueprint(warehouse_blueprint)

@app.route("/")
@login_required
def homepage():
    return redirect(url_for("analytics.index"))

if __name__ == "__main__":
    app.run(debug=True)