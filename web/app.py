from flask import (Flask, render_template, request, session, redirect, url_for, flash, abort,)  # pyright: ignore[reportMissingImports]
from datetime import date, datetime, timedelta
from collections import defaultdict
from functools import wraps
from dotenv import load_dotenv
import os
import math
import copy
from web.auth import authenticate_user, create_staff_user, load_users
from app.inventory_service import InventoryService
from app.models import Product
from app.config import DEFAULT_INVENTORY_FILE, DEFAULT_BACKUP_DIRECTORY

load_dotenv()

# Keep test data separate from the normal inventory and backups.
TEST_MODE = os.getenv("IMS_TEST_MODE", "false").casefold() in {
    "true",
    "1",
    "yes",
}

if TEST_MODE:
    INVENTORY_FILE = "data/inventory_test.json"
    BACKUP_DIRECTORY = "data/test_backups"
else:
    INVENTORY_FILE = DEFAULT_INVENTORY_FILE
    BACKUP_DIRECTORY = DEFAULT_BACKUP_DIRECTORY

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing. Configure it in your .env file.")

app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.getenv("FLASK_HTTPS_ONLY", "False").casefold() in {"true", "1", "yes"},)

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
@app.route("/staff")
@admin_required
def staff():
    """Display account usernames and roles without exposing password hashes."""
    users = load_users()
    safe_users = [{"username": user.get("username", ""), "role": user.get("role", "Staff"),} for user in users]

    return render_template("staff.html", users=safe_users)


@app.route("/staff/add", methods=["POST"])
@admin_required
def add_staff():
    """Create a staff account from the administrator's form."""
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    try:
        create_staff_user(username, password)
        flash("Staff account created successfully.", "success")
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("staff"))

@app.route("/dashboard")
@login_required
def dashboard():
    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

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
    inventory_service.load_inventory(INVENTORY_FILE)

    if request.method == "POST":
        try:
            product_id = int(request.form.get("product_id", ""))
            name = request.form.get("name", "").strip()
            price = float(request.form.get("price", ""))
            selling_price = float(request.form.get("selling_price", ""))
            quantity = 0
            category = request.form.get("category", "").strip() or "Uncategorized"

            # Preserve compatibility with older product submissions.
            base_unit = request.form.get("base_unit", "unit").strip() or "unit"

            def read_units(name_field, factor_field):
                unit_names = request.form.getlist(name_field)
                unit_factors = request.form.getlist(factor_field)

                if len(unit_names) != len(unit_factors):
                    raise ValueError("Each packaging unit must have a matching conversion factor.")
                units = []

                for unit_name, factor_text in zip(unit_names, unit_factors):
                    unit_name = unit_name.strip()
                    factor_text = factor_text.strip()

                    # Ignore an optional row only when both fields are empty.
                    if not unit_name and not factor_text:
                        continue

                    if not unit_name or not factor_text:
                        raise ValueError("Enter both the unit name and conversion factor.")

                    try:
                        factor = float(factor_text)
                    except ValueError:
                        raise ValueError("Conversion factors must be valid numbers.") from None

                    if not math.isfinite(factor) or factor <= 0:
                        raise ValueError("Conversion factors must be positive, finite numbers.")

                    units.append({"name": unit_name, "base_quantity": (int(factor) if factor.is_integer() else factor),})
                return units

            purchase_units = read_units("purchase_unit_name", "purchase_unit_factor",)
            selling_units = read_units("selling_unit_name", "selling_unit_factor",)

            product = Product(product_id, name, price, quantity, category, base_unit=base_unit, purchase_units=purchase_units, selling_units=selling_units, selling_price=selling_price,)
            inventory_service.add_product(product)
            inventory_service.save_inventory(INVENTORY_FILE)
            flash("Product added successfully!", "success")
            return redirect(url_for("products"))

        except (ValueError, TypeError, OverflowError) as exc:
            return render_template("add_product.html", username=session["username"], role=session["role"], error=str(exc),)
    return render_template("add_product.html", username=session["username"], role=session["role"],)

@app.route("/products/remove", methods=["POST"])
@admin_required
def remove_product():
    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    product_id = int(request.form.get("product_id"))

    inventory_service.remove_product(product_id)
    inventory_service.save_inventory(INVENTORY_FILE)

    return redirect(url_for("products"))

@app.route("/products/deleted-history")
def deleted_history():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    deleted_products = inventory_service.get_deleted_products()

    return render_template("deleted_history.html", username=session["username"], role=session["role"], deleted_products=deleted_products,)

@app.route("/products/restore", methods=["POST"])
@admin_required
def restore_product():
    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    product_id = int(request.form.get("product_id"))

    inventory_service.restore_product(product_id)
    inventory_service.save_inventory(INVENTORY_FILE)

    return redirect(url_for("products"))

@app.route("/products/delete-permanently", methods=["POST"])
@admin_required
def permanently_delete_product():
    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    product_id = int(request.form.get("product_id"))

    inventory_service.permanently_delete_product(product_id)
    inventory_service.save_inventory(INVENTORY_FILE)

    return redirect(url_for("removed_products"))

@app.route("/products/removed")
def removed_products():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    removed_products = inventory_service.removed_products

    return render_template("removed_products.html", username=session["username"], role=session["role"], removed_products=removed_products,)

@app.route("/products/update", methods=["GET", "POST"])
def update_product():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    if request.method == "POST":
        try:
            product_id = int(request.form.get("product_id", ""))

            name = request.form.get("name", "").strip()
            price_input = request.form.get("price", "").strip()
            selling_price_input = request.form.get("selling_price", "").strip()
            category = request.form.get("category", "").strip()
            base_unit = request.form.get("base_unit", "").strip()

            def read_units(name_field, factor_field):
                unit_names = request.form.getlist(name_field)
                unit_factors = request.form.getlist(factor_field)

                if len(unit_names) != len(unit_factors):
                    raise ValueError(
                        "Each packaging unit must have a matching conversion factor."
                    )

                units = []

                for unit_name, factor_text in zip(unit_names, unit_factors):
                    unit_name = unit_name.strip()
                    factor_text = factor_text.strip()

                    if not unit_name and not factor_text:
                        continue

                    if not unit_name or not factor_text:
                        raise ValueError(
                            "Enter both the unit name and conversion factor."
                        )

                    try:
                        factor = float(factor_text)
                    except ValueError:
                        raise ValueError(
                            "Conversion factors must be valid numbers."
                        ) from None

                    if not math.isfinite(factor) or factor <= 0:
                        raise ValueError(
                            "Conversion factors must be positive, finite numbers."
                        )

                    units.append({
                        "name": unit_name,
                        "base_quantity": (
                            int(factor) if factor.is_integer() else factor
                        ),
                    })

                return units

            purchase_units = read_units(
                "purchase_unit_name",
                "purchase_unit_factor",
            )
            selling_units = read_units(
                "selling_unit_name",
                "selling_unit_factor",
            )

            inventory_service.update_product(
                product_id,
                name=name or None,
                price=float(price_input) if price_input else None,
                selling_price=(
                    float(selling_price_input)
                    if selling_price_input
                    else None
                ),
                category=category or None,
                base_unit=base_unit or None,
                purchase_units=purchase_units,
                selling_units=selling_units,
            )

            inventory_service.save_inventory(INVENTORY_FILE)

            flash("Product updated successfully!", "success")
            return redirect(url_for("products"))

        except (ValueError, TypeError, OverflowError) as exc:
            flash(f"Unable to update product: {exc}", "error")
            return redirect(
                url_for(
                    "update_product",
                    product_id=request.form.get("product_id", ""),
                )
            )

    product_id = request.args.get("product_id", "")

    try:
        product = (
            inventory_service.get_product(int(product_id))
            if product_id
            else None
        )
    except (ValueError, TypeError):
        product = None

    if product_id and product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products"))

    return render_template(
        "update_product.html",
        username=session["username"],
        role=session["role"],
        is_admin=session.get("role") == "admin",
        product=product,
        product_id=product_id,
    )

@app.route("/products")
def products():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    products = inventory_service.products

    return render_template("products.html", username=session["username"], role=session["role"], products=products)

@app.route("/stock", methods=["GET", "POST"])
def stock():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    if request.method == "POST":
        action = request.form.get("action")

        try:
            product_id = int(request.form.get("product_id", ""))
            quantity = float(request.form.get("quantity", ""))
            unit = request.form.get("unit", "").strip() or None

            # Convert whole-number quantities back to integers.
            if quantity.is_integer():
                quantity = int(quantity)
            price = float(request.form.get("price", ""))

            if action == "stock_in":
                payment_method = request.form.get("payment_method", "").strip()

                inventory_service.stock_in(product_id, quantity, price=price, unit=unit, payment_method=payment_method,)

                success_message = "Stock In completed successfully."

            elif action == "stock_out":
                reason = request.form.get("reason", "Other").strip()

                payment_method = (request.form.get("payment_method", "").strip() if reason == "Sale" else None)

                inventory_service.stock_out(product_id, quantity, price=price, reason=reason, unit=unit, payment_method=payment_method,)

                success_message = "Stock Out completed successfully."

            else:
                raise ValueError("Please select a valid stock action.")
            inventory_service.save_inventory(INVENTORY_FILE)
            flash(success_message, "success")

        except (ValueError, TypeError, OverflowError) as error:
            flash(str(error), "error")
        return redirect(url_for("stock"))
    products = inventory_service.products
    alerts = inventory_service.get_inventory_alerts()
    return render_template("stock.html", username=session["username"], role=session["role"], products=products, alerts=alerts,)

@app.route("/sales", methods=["GET", "POST"])
def sales():
    if "username" not in session:
        return "Please log in first."

    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    if request.method == "POST":
        try:
            # Read all product lines submitted by the form.
            product_ids = request.form.getlist("product_id")
            quantities = request.form.getlist("quantity")
            prices = request.form.getlist("price")
            selling_units = request.form.getlist("selling_unit")

            # Support older forms that submit quantities in the base unit.
            if not selling_units:
                selling_units = [""] * len(product_ids)

            payment_method = request.form.get("payment_method", "").strip()

            valid_payment_methods = {"Cash", "Bank Transfer", "Cheque",}

            if payment_method not in valid_payment_methods:
                raise ValueError("Please select a valid payment method.")

            # Require at least one product line.
            if not product_ids:
                raise ValueError("Please add at least one product to the sale.")

            # Every product line must contain all required fields.
            if not (len(product_ids) == len(quantities) == len(prices) == len(selling_units)):
                raise ValueError("The sale contains incomplete product lines. " "Please review the form and try again.")

            # Validate every line before changing inventory.
            validated_lines = []
            seen_product_ids = set()

            for (raw_product_id, raw_quantity, raw_price, raw_unit,) in zip(product_ids, quantities, prices, selling_units,):
                try:
                    product_id = int(raw_product_id)
                    quantity = int(raw_quantity)
                    price = float(raw_price)
                except (ValueError, TypeError):
                    raise ValueError("Each product line must have a valid product, " "whole-number quantity, and selling price.")

                unit = raw_unit.strip().lower()

                product = inventory_service.get_product(product_id)

                if not unit:
                    # Legacy products may use the default "unit" base unit.
                    # Preserve the original stock-out behavior for those products.
                    unit = None if product.base_unit == "unit" else product.base_unit

                if quantity <= 0:
                    raise ValueError("Sale quantities must be greater than zero.")

                if not math.isfinite(price) or price < 0:
                    raise ValueError("Selling prices must be valid, " "non-negative numbers.")

                if product_id in seen_product_ids:
                    raise ValueError("Each product can appear only once per sale. " "Please combine duplicate product lines.")

                seen_product_ids.add(product_id)

                product = inventory_service.get_product(product_id)

                # Validate the selected unit and convert the requested
                # quantity to the product's base unit without changing stock.
                if unit is None:
                    # Legacy/default products use the original base-unit behavior.
                    base_quantity = quantity
                    selected_unit = None
                    factor = 1
                else:
                    base_quantity, selected_unit, factor = (inventory_service._convert_to_base_units(product, quantity, unit, "Stock-out",))

                if base_quantity <= 0:
                    raise ValueError("Sale quantities must be greater than zero.")

                if base_quantity > product.quantity:
                    raise ValueError(f"Insufficient stock for {product.name}. " f"Available: {product.quantity} " f"{product.base_unit}; " f"requested: {base_quantity} " f"{product.base_unit}.")

                validated_lines.append({"product_id": product_id, "quantity": quantity, "price": price, "unit": selected_unit, "base_quantity": base_quantity, "conversion_factor": factor,})

            # Preserve the in-memory state before changing inventory.
            original_quantities = {product.product_id: product.quantity for product in inventory_service.products}

            original_transactions = copy.deepcopy(inventory_service.transactions)

            # One reference shared by all lines in this sale.
            sale_reference = (f"SALE-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

            try:
                for line in validated_lines:
                    inventory_service.stock_out(line["product_id"], line["quantity"], price=line["price"], reason="Sale", unit=line["unit"],)

                    transaction = inventory_service.transactions[-1]
                    transaction["payment_method"] = payment_method
                    transaction["sale_reference"] = sale_reference

                # Save only after every product line succeeds.
                inventory_service.save_inventory(INVENTORY_FILE)

            except Exception:
                # Restore in-memory stock and transaction history if
                # processing or saving fails.
                for product in inventory_service.products:
                    if product.product_id in original_quantities:
                        product.quantity = original_quantities[product.product_id]

                inventory_service.transactions = original_transactions
                raise

            flash(f"Sale recorded successfully. " f"Sale reference: {sale_reference}", "success",)

        except (ValueError, TypeError) as error:
            app.logger.exception("Sale validation or processing failed.")
            flash(str(error), "error")

        except OSError:
            app.logger.exception("Failed to save the sale.")

            flash("The sale could not be saved because of a storage error. " "Please check the inventory before trying again.", "error",)

        return redirect(url_for("sales"))

    products = inventory_service.products

    return render_template("sales.html", username=session["username"], role=session["role"], products=products,)

@app.route("/transactions")
@login_required
def transactions():
    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)

    all_transactions = inventory_service.get_transactions()

    # Apply staff restrictions before passing transaction data to the template.
    if not is_admin_user():
        all_transactions = [safe_transaction_for_staff(transaction) for transaction in all_transactions]

    search_query = request.args.get("search", "").strip().casefold()
    transaction_type = request.args.get("type", "").strip().upper()
    reason_filter = request.args.get("reason", "").strip()
    payment_filter = request.args.get("payment_method", "").strip()
    period = request.args.get("period", "all").strip().lower()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    status_filter = request.args.get("status", "").strip().lower()

    today = date.today()
    date_from = None
    date_to = None

    if period == "today":
        date_from = today
        date_to = today
    elif period == "yesterday":
        date_from = today - timedelta(days=1)
        date_to = date_from
    elif period == "week":
        date_from = today - timedelta(days=today.weekday())
        date_to = today
    elif period == "month":
        date_from = today.replace(day=1)
        date_to = today
    elif period == "custom":
        try:
            if start_date:
                date_from = date.fromisoformat(start_date)
            if end_date:
                date_to = date.fromisoformat(end_date)

            if date_from and date_to and date_from > date_to:
                flash("The start date cannot be after the end date.", "error")
                date_from = None
                date_to = None
                period = "all"
        except ValueError:
            flash("Please enter valid custom dates.", "error")
            date_from = None
            date_to = None
            period = "all"

    filtered_transactions = []

    for transaction in all_transactions:
        original_transaction = transaction

        # Cancellation information is retained only for safe display.
        is_cancelled = bool(original_transaction.get("cancelled", False))

        if status_filter == "cancelled" and not is_cancelled:
            continue
        if status_filter == "active" and is_cancelled:
            continue

        current_type = str(transaction.get("type", "")).upper()
        if transaction_type and current_type != transaction_type:
            continue

        current_reason = str(transaction.get("reason", "Unspecified"))
        if reason_filter and current_reason != reason_filter:
            continue

        current_payment = str(transaction.get("payment_method") or "Unspecified")
        if payment_filter and current_payment != payment_filter:
            continue

        if search_query:
            product_name = str(transaction.get("product_name", "Unknown product")).casefold()
            product_id = str(transaction.get("product_id", ""))

            if (search_query not in product_name and search_query not in product_id.casefold()):
                continue

        timestamp = str(transaction.get("timestamp", ""))
        transaction_date = None

        try:
            if timestamp:
                transaction_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()
        except ValueError:
            transaction_date = None

        if date_from and (transaction_date is None or transaction_date < date_from):
            continue

        if date_to and (transaction_date is None or transaction_date > date_to):
            continue

        # Add safe display metadata without exposing other original fields.
        if is_admin_user():
            display_transaction = dict(transaction)
        else:
            display_transaction = {"product_id": transaction.get("product_id"), "product_name": transaction.get("product_name", "Unknown product"), "type": transaction.get("type"), "quantity": transaction.get("quantity", 0), "timestamp": transaction.get("timestamp", ""), "reason": transaction.get("reason", ""), "cancelled": is_cancelled,}

            is_sale = (transaction.get("type") == "STOCK-OUT" and transaction.get("reason") == "Sale" and not is_cancelled)

            if is_sale:
                display_transaction["price"] = transaction.get("price")
                display_transaction["sales_value"] = transaction.get("sales_value", 0)

        display_transaction["payment_method"] = current_payment

        filtered_transactions.append(display_transaction)

    # Preserve chronological display order; the template need not reverse it.
    filtered_transactions.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True,)

    # Filter choices come from the actual transaction history.
    reasons = sorted({str(transaction.get("reason", "Unspecified")) for transaction in all_transactions})

    payment_methods = ["Cash", "Bank Transfer", "Cheque", "Unspecified"]

    return render_template("transactions.html", username=session["username"], role=session["role"], transactions=filtered_transactions, search_query=request.args.get("search", ""), selected_type=transaction_type, selected_reason=reason_filter, selected_payment_method=payment_filter, selected_period=period, start_date=start_date, end_date=end_date, selected_status=status_filter, reasons=reasons, payment_methods=payment_methods, is_admin=is_admin_user(),)

@app.route("/transactions/cancel-sale/<transaction_id>", methods=["POST"])
@admin_required
def cancel_sale_route(transaction_id):
    """Allow administrators to cancel a recorded sale."""

    reason = request.form.get("cancellation_reason", "").strip()

    try:
        inventory_service = InventoryService()
        inventory_service.load_inventory(INVENTORY_FILE)

        inventory_service.cancel_sale(transaction_id=transaction_id, reason=reason, file_path=INVENTORY_FILE,)

        flash("Sale cancelled successfully. The stock has been restored.", "success",)

    except (ValueError, TypeError) as error:
        flash(str(error), "error")

    except OSError:
        app.logger.exception("Failed to save the sale cancellation.")
        flash("The sale cancellation could not be saved. Please check the inventory.", "error",)

    return redirect(url_for("transactions"))

@app.route("/reports")
@login_required
def reports():
    inventory_service = InventoryService()
    inventory_service.load_inventory(INVENTORY_FILE)
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
        inventory_service.create_backup(INVENTORY_FILE, BACKUP_DIRECTORY)

        return redirect(url_for("backups"))

    backups = inventory_service.list_backups(BACKUP_DIRECTORY)

    return render_template("backups.html", username=session["username"], role=session["role"], backups=backups)

@app.route("/view-backup")
def view_backup():
    if "username" not in session:
        return "Please log in first."

    backup_file = request.args.get("backup_file")

    if not backup_file:
        return "No backup file selected."

    backup_path = os.path.join(BACKUP_DIRECTORY, os.path.basename(backup_file))
    
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
    backup_path = os.path.join(BACKUP_DIRECTORY, backup_filename,)

    # Never attempt to restore a file that does not exist.
    if not os.path.isfile(backup_path):
        flash("Backup file not found. No changes were made.", "error")
        return redirect(url_for("backups"))

    inventory_service = InventoryService()

    try:
        # Preserve the existing inventory in a new backup before restoring.
        inventory_service.safe_restore_backup(backup_path, INVENTORY_FILE, BACKUP_DIRECTORY,)
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
    inventory_service.load_inventory(INVENTORY_FILE)

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
    inventory_service.load_inventory(INVENTORY_FILE)

    transactions = inventory_service.get_transactions()

    period = request.args.get("period", "all")

    filtered_transactions = filter_transactions_by_period(transactions, period, specific_date=request.args.get("date"), start_date=request.args.get("start_date"), end_date=request.args.get("end_date"),)

    sales = [item for item in filtered_transactions if item.get("type") == "STOCK-OUT" and item.get("reason") == "Sale" and not item.get("cancelled", False)]

    stock_in_transactions = [item for item in filtered_transactions if item.get("type") == "STOCK-IN"]

    revenue = sum(item.get("sales_value", 0) or 0 for item in sales)

    cash_received = sum(item.get("sales_value", 0) or 0 for item in sales if item.get("payment_method") == "Cash")

    bank_transfer_received = sum(item.get("sales_value", 0) or 0 for item in sales if item.get("payment_method") == "Bank Transfer")

    cheque_received = sum(item.get("sales_value", 0) or 0 for item in sales if item.get("payment_method") == "Cheque")

    unspecified_payment_total = sum(item.get("sales_value", 0) or 0 for item in sales if item.get("payment_method") not in {"Cash", "Bank Transfer", "Cheque"})

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

    return render_template( "financial_review.html", username=session["username"], role=session["role"], period=period, revenue=revenue, cost_of_goods_sold=cost_of_goods_sold, gross_profit=gross_profit, stock_in_value=stock_in_value, sales_count=len(sales), profitability_rows=profitability_rows, cash_received=cash_received, bank_transfer_received=bank_transfer_received, cheque_received=cheque_received, unspecified_payment_total=unspecified_payment_total, )

if __name__ == "__main__":
    app.run(debug=True)