from flask import Flask, render_template, request, session, redirect, url_for, flash  # type: ignore
from dotenv import load_dotenv
import os

from web.auth import authenticate_user
from app.inventory_service import InventoryService
from app.models import Product
from app.config import DEFAULT_INVENTORY_FILE, DEFAULT_BACKUP_DIRECTORY

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = authenticate_user(username, password)

    if user:
        session["username"] = user["username"]
        session["role"] = user["role"]

        return redirect(url_for("dashboard"))

    return "Invalid username or password."

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    dashboard_data = inventory_service.get_dashboard_data()

    transactions = inventory_service.get_transactions()

    alerts = inventory_service.get_inventory_alerts()

    return render_template("dashboard.html", username=session["username"], role=session["role"], dashboard_data=dashboard_data, transactions=transactions, alerts=alerts)

@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    if request.method == "POST":
        product_id = int(request.form.get("product_id"))
        name = request.form.get("name")
        price = float(request.form.get("price"))
        quantity = int(request.form.get("quantity"))
        category = request.form.get("category")

        product = Product(product_id, name, price, quantity, category,)

        inventory_service.add_product(product)
        inventory_service.save_inventory(DEFAULT_INVENTORY_FILE)

        return redirect(url_for("products"))

    return render_template("add_product.html", username=session["username"], role=session["role"],)

@app.route("/products/remove", methods=["POST"])
def remove_product():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    product_id = int(request.form.get("product_id"))

    inventory_service.remove_product(product_id)
    inventory_service.save_inventory(DEFAULT_INVENTORY_FILE)

    return redirect(url_for("products"))

@app.route("/products/deleted-history")
def deleted_history():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    deleted_products = inventory_service.get_deleted_products()

    return render_template("deleted_history.html", username=session["username"], role=session["role"], deleted_products=deleted_products,)

@app.route("/products/restore", methods=["POST"])
def restore_product():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    product_id = int(request.form.get("product_id"))

    inventory_service.restore_product(product_id)
    inventory_service.save_inventory(DEFAULT_INVENTORY_FILE)

    return redirect(url_for("products"))

@app.route("/products/delete-permanently", methods=["POST"])
def permanently_delete_product():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    product_id = int(request.form.get("product_id"))

    inventory_service.permanently_delete_product(product_id)
    inventory_service.save_inventory(DEFAULT_INVENTORY_FILE)

    return redirect(url_for("removed_products"))

@app.route("/products/removed")
def removed_products():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    removed_products = inventory_service.removed_products

    return render_template("removed_products.html", username=session["username"], role=session["role"], removed_products=removed_products,)

@app.route("/products/update", methods=["GET", "POST"])
def update_product():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    if request.method == "POST":
        product_id = int(request.form.get("product_id"))

        name = request.form.get("name")
        price_input = request.form.get("price")
        category = request.form.get("category")

        price = float(price_input) if price_input else None

        inventory_service.update_product(product_id, name=name or None, price=price, category=category or None,)

        inventory_service.save_inventory(DEFAULT_INVENTORY_FILE)

        return redirect(url_for("products"))

    product_id = request.args.get("product_id", "")

    return render_template("update_product.html", username=session["username"], role=session["role"], product_id=product_id,)

@app.route("/products")
def products():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    products = inventory_service.products

    return render_template("products.html", username=session["username"], role=session["role"], products=products)

@app.route("/stock", methods=["GET", "POST"])
def stock():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    if request.method == "POST":
        action = request.form.get("action")

        try:
            product_id = int(request.form.get("product_id", ""))
            quantity = int(request.form.get("quantity", ""))

            if action == "stock_in":
                price = float(request.form.get("price", ""))
                inventory_service.stock_in(product_id, quantity, price=price)
                success_message = "Stock In completed successfully."

            elif action == "stock_out":
                price = float(request.form.get("price", ""))
                inventory_service.stock_out(product_id, quantity, price=price)
                success_message = "Stock Out completed successfully."

            else:
                raise ValueError("Please select a valid stock action.")

            inventory_service.save_inventory(DEFAULT_INVENTORY_FILE)
            flash(success_message, "success")

        except (ValueError, TypeError) as error:
            flash(str(error), "error")

        return redirect(url_for("stock"))

    products = inventory_service.products
    return render_template(
"stock.html", username=session["username"], role=session["role"], products=products,)

@app.route("/sales", methods=["GET", "POST"])
def sales():
    if "username" not in session:
        return "Please log in first."
    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)
    if request.method == "POST":
        try:
            product_id = int(request.form.get("product_id", ""))
            quantity = int(request.form.get("quantity", ""))
            price = float(request.form.get("price", ""))
            inventory_service.stock_out(product_id, quantity, price=price, reason="Sale",)
            inventory_service.save_inventory(DEFAULT_INVENTORY_FILE)
            flash("Sale recorded successfully.", "success")
        except (ValueError, TypeError) as error:
            flash(str(error), "error")
        return redirect(url_for("sales"))
    products = inventory_service.products
    return render_template("sales.html", username=session["username"], role=session["role"], products=products,)

@app.route("/transactions")
def transactions():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    transactions = inventory_service.get_transactions()

    return render_template("transactions.html", username=session["username"], role=session["role"], transactions=transactions)

@app.route("/reports")
def reports():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    report_data = inventory_service.get_dashboard_data()

    return render_template("reports.html", username=session["username"], role=session["role"], report_data=report_data)

@app.route("/backups", methods=["GET", "POST"])
def backups():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()

    if request.method == "POST":
        inventory_service.create_backup(DEFAULT_INVENTORY_FILE, DEFAULT_BACKUP_DIRECTORY)

        return redirect(url_for("backups"))

    backups = inventory_service.list_backups(DEFAULT_BACKUP_DIRECTORY)

    return render_template("backups.html", username=session["username"], role=session["role"], backups=backups)

@app.route("/view-backup")
def view_backup():
    if "username" not in session:
        return "Please log in first."

    backup_file = request.args.get("backup_file")

    if not backup_file:
        return "No backup file selected."

    backup_path = os.path.join(DEFAULT_BACKUP_DIRECTORY, os.path.basename(backup_file))
    
    if not os.path.exists(backup_path):
        return "Backup file not found."

    with open(backup_path, "r", encoding="utf-8") as file:
        backup_data = __import__("json").load(file)

    return render_template("backup_details.html", username=session["username"], role=session["role"], backup_file=backup_file, backup_data=backup_data)

@app.route("/restore-backup", methods=["POST"])
def restore_backup():
    if "username" not in session:
        return "Please log in first."

    backup_file = request.form.get("backup_file")

    if not backup_file:
        return "No backup file selected."

    inventory_service = InventoryService()

    backup_path = backup_file

    inventory_service.safe_restore_backup(backup_path, DEFAULT_INVENTORY_FILE, DEFAULT_BACKUP_DIRECTORY)

    return redirect(url_for("backups"))

@app.route("/logout")
def logout():
    session.clear()
    return "You have been logged out."

if __name__ == "__main__":
    app.run(debug=True)