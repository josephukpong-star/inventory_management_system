from flask import (Flask, render_template, request, session, redirect, url_for, flash, abort,)  # pyright: ignore[reportMissingImports]
from datetime import date, datetime, timedelta
from collections import defaultdict
from functools import wraps
from dotenv import load_dotenv
import os
from web.auth import authenticate_user
from app.inventory_service import InventoryService
from app.models import Product
from app.config import DEFAULT_INVENTORY_FILE, DEFAULT_BACKUP_DIRECTORY

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

def is_admin_user():
    """Return True only for an authenticated administrator."""
    return ("username" in session and (session.get("role") or "").strip().casefold() == "admin")


@app.context_processor
def inject_user_permissions():
    """Make the administrator status available to all templates."""
    return {"is_admin": is_admin_user()}


def login_required(view_function):
    """Require an authenticated session to access a route."""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("home"))
        return view_function(*args, **kwargs)

    return wrapped_view


def admin_required(view_function):
    """Require an administrator account to access a route."""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("home"))

        if not is_admin_user():
            abort(403)

        return view_function(*args, **kwargs)

    return wrapped_view


def parse_transaction_datetime(transaction):
    """Parse a transaction timestamp, safely handling invalid records."""
    timestamp = transaction.get("timestamp")

    if not timestamp:
        return None

    try:
        return datetime.fromisoformat(timestamp)
    except (TypeError, ValueError):
        return None


def filter_transactions_by_period(transactions, period, specific_date=None,
                                  start_date=None, end_date=None):
    """Filter transactions using predefined or custom date ranges."""
    today = date.today()

    if period == "all":
        return list(transactions)

    if period == "today":
        start, end = today, today
    elif period == "yesterday":
        start = end = today - timedelta(days=1)
    elif period == "this_week":
        start = today - timedelta(days=today.weekday())
        end = today
    elif period == "last_week":
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
    elif period == "this_month":
        start = today.replace(day=1)
        end = today
    elif period == "last_month":
        end = today.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
    elif period == "specific_date":
        try:
            start = end = date.fromisoformat(specific_date or "")
        except ValueError:
            return []
    elif period == "custom":
        try:
            start = date.fromisoformat(start_date or "")
            end = date.fromisoformat(end_date or "")
        except ValueError:
            return []

        if start > end:
            return []
    else:
        return []

    filtered = []

    for transaction in transactions:
        timestamp = parse_transaction_datetime(transaction)

        if timestamp is None:
            continue

        transaction_date = timestamp.date()

        if start <= transaction_date <= end:
            filtered.append(transaction)

    return filtered


def filter_transactions_by_type(transactions, transaction_filter):
    """Filter stock movements by transaction type or stock-out reason."""
    if transaction_filter == "all":
        return list(transactions)

    if transaction_filter == "sales":
        return [item for item in transactions if item.get("type") == "STOCK-OUT" and item.get("reason") == "Sale"]

    if transaction_filter == "stock_in":
        return [item for item in transactions if item.get("type") == "STOCK-IN"]

    if transaction_filter == "stock_out":
        return [item for item in transactions if item.get("type") == "STOCK-OUT"]

    reason_filters = {"damaged_goods": "Damaged Goods", "internal_use": "Internal Use", "gift_free_issue": "Gift/Free Issue", "other": "Other",}

    if transaction_filter in reason_filters:
        reason = reason_filters[transaction_filter]
        return [item for item in transactions if item.get("type") == "STOCK-OUT" and item.get("reason") == reason]

    return []


def safe_transaction_for_staff(transaction):
    """
    Return only operational information for staff.
    Selling prices and amounts are available for actual sales only.
    """
    safe_record = {"product_id": transaction.get("product_id"), "product_name": transaction.get("product_name", "Unknown product"), "type": transaction.get("type"), "quantity": transaction.get("quantity", 0), "timestamp": transaction.get("timestamp", ""), "reason": transaction.get("reason", ""),}
    is_sale = (transaction.get("type") == "STOCK-OUT" and transaction.get("reason") == "Sale")
    if is_sale:
        safe_record["price"] = transaction.get("price")
        safe_record["total_value"] = transaction.get("sales_value", 0)
        safe_record["sales_value"] = transaction.get("sales_value", 0)

    return safe_record

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
@login_required
def dashboard():
    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    dashboard_data = inventory_service.get_dashboard_data()
    transactions = inventory_service.get_transactions()
    alerts = inventory_service.get_inventory_alerts()

    # Hide financial information from non-admin users.
    if not is_admin_user():
        dashboard_data = dashboard_data.copy()

        private_fields = ("total_value", "category_values", "inventory_value_percentage", "top_products_by_value", "top_products_with_values", "top_product", "top_category", "stock_in_value", "stock_out_sales_value", "cost_of_goods_sold", "gross_profit",)
        for field in private_fields:
            dashboard_data.pop(field, None)
        transactions = [safe_transaction_for_staff(transaction) for transaction in transactions]
    # IMPORTANT: This return statement must remain inside dashboard().
    return render_template("dashboard.html", username=session["username"], role=session["role"], dashboard_data=dashboard_data, transactions=transactions, alerts=alerts,)

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
@login_required
def transactions():
    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)
    transactions = inventory_service.get_transactions()
    if not is_admin_user():
        transactions = [ safe_transaction_for_staff(transaction) for transaction in transactions ]
    return render_template( "transactions.html", username=session["username"], role=session["role"], transactions=transactions, )

@app.route("/reports")
@login_required
def reports():
    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)
    report_data = inventory_service.get_dashboard_data()
    # Hide financial information from staff only.
    if not is_admin_user():
        report_data = report_data.copy()
        private_fields = ( "total_value", "category_values", "inventory_value_percentage", "top_products_by_value", "top_products_with_values", "top_product", "top_category", "stock_in_value", "stock_out_sales_value", "cost_of_goods_sold", "gross_profit", )
        for field in private_fields:
            report_data.pop(field, None)
    return render_template( "reports.html", username=session["username"], role=session["role"], report_data=report_data, )

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

    # Hide financial information from staff.
    if not is_admin_user():
        backup_data = backup_data.copy()

        # Remove product prices from the staff-facing backup data.
        backup_data["products"] = [{key: value for key, value in product.items() if key != "price"} for product in backup_data.get("products", [])]

        # Remove financial values from the staff-facing transactions.
        private_transaction_fields = {"price", "total_value", "sales_value", "inventory_cost", "cost_of_goods_sold", "gross_profit",}

        backup_data["transactions"] = [{key: value for key, value in transaction.items() if key not in private_transaction_fields} for transaction in backup_data.get("transactions", [])]

    return render_template("backup_details.html", username=session["username"], role=session["role"], backup_file=backup_file, backup_data=backup_data,)

@app.route("/restore-backup", methods=["POST"])
@admin_required
def restore_backup():
    backup_file = request.form.get("backup_file")

    if not backup_file:
        flash("No backup file selected.", "error")
        return redirect(url_for("backups"))

    # Resolve the selected filename inside the backup directory.
    backup_filename = os.path.basename(backup_file)
    backup_path = os.path.join(DEFAULT_BACKUP_DIRECTORY, backup_filename,)

    # Never attempt to restore a file that does not exist.
    if not os.path.isfile(backup_path):
        flash("Backup file not found. No changes were made.", "error")
        return redirect(url_for("backups"))

    inventory_service = InventoryService()

    try:
        # Preserve the existing inventory in a new backup before restoring.
        inventory_service.safe_restore_backup(backup_path, DEFAULT_INVENTORY_FILE, DEFAULT_BACKUP_DIRECTORY,)
    except (OSError, ValueError) as error:
        app.logger.exception("Failed to restore inventory backup")
        flash(f"Backup restoration failed: {error}", "error")
        return redirect(url_for("backups"))

    flash("Inventory restored successfully.", "success")
    return redirect(url_for("backups"))

@app.route("/logout")
def logout():
    session.clear()
    return "You have been logged out."

@app.route("/view-records")
@login_required
def view_records():
    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    transactions = inventory_service.get_transactions()

    period = request.args.get("period", "all")
    transaction_filter = request.args.get("type", "all")

    filtered_transactions = filter_transactions_by_period(transactions, period, specific_date=request.args.get("date"), start_date=request.args.get("start_date"), end_date=request.args.get("end_date"),)

    filtered_transactions = filter_transactions_by_type( filtered_transactions, transaction_filter,)

    # Sort newest first.
    filtered_transactions.sort(key=lambda item: item.get("timestamp", ""), reverse=True,)

    # Staff receive only permitted transaction fields.
    if not is_admin_user():
        filtered_transactions = [safe_transaction_for_staff(item) for item in filtered_transactions]

    sales_transactions = [item for item in filtered_transactions if item.get("type") == "STOCK-OUT" and item.get("reason") == "Sale"]

    # Only administrators receive aggregate financial totals.
    sales_total = None

    if is_admin_user():
        sales_total = sum(item.get("sales_value", 0) or 0 for item in sales_transactions)

    return render_template("view_records.html", username=session["username"], role=session["role"], transactions=filtered_transactions, period=period, transaction_filter=transaction_filter, record_count=len(filtered_transactions), sales_total=sales_total,)


@app.route("/financial-review")
@admin_required
def financial_review():
    inventory_service = InventoryService()
    inventory_service.load_inventory(DEFAULT_INVENTORY_FILE)

    transactions = inventory_service.get_transactions()

    period = request.args.get("period", "all")

    filtered_transactions = filter_transactions_by_period(transactions, period, specific_date=request.args.get("date"), start_date=request.args.get("start_date"), end_date=request.args.get("end_date"),)

    sales = [item for item in filtered_transactions if item.get("type") == "STOCK-OUT" and item.get("reason") == "Sale"]

    stock_in_transactions = [item for item in filtered_transactions if item.get("type") == "STOCK-IN"]

    revenue = sum(item.get("sales_value", 0) or 0 for item in sales)

    cost_of_goods_sold = sum(item.get("inventory_cost", 0) or 0 for item in sales)

    gross_profit = revenue - cost_of_goods_sold

    stock_in_value = sum(item.get("inventory_cost", 0) or 0 for item in stock_in_transactions)

    product_profitability = defaultdict(
        lambda: {"quantity": 0, "revenue": 0, "cost": 0,})

    for sale in sales:
        product_name = sale.get("product_name", "Unknown product")
        product_data = product_profitability[product_name]

        product_data["quantity"] += sale.get("quantity", 0) or 0
        product_data["revenue"] += sale.get("sales_value", 0) or 0
        product_data["cost"] += sale.get("inventory_cost", 0) or 0

    profitability_rows = []

    for product_name, values in product_profitability.items():
        profitability_rows.append({"product_name": product_name, "quantity": values["quantity"], "revenue": values["revenue"], "cost": values["cost"], "gross_profit": values["revenue"] - values["cost"],})

    profitability_rows.sort(key=lambda item: item["gross_profit"], reverse=True,)

    return render_template("financial_review.html", username=session["username"], role=session["role"], period=period, revenue=revenue, cost_of_goods_sold=cost_of_goods_sold, gross_profit=gross_profit, stock_in_value=stock_in_value, sales_count=len(sales), profitability_rows=profitability_rows,)

if __name__ == "__main__":
    app.run(debug=True)