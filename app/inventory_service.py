from datetime import datetime
from app.models import Product
from app.storage import (save_inventory_data, load_inventory_data, save_inventory_report,)
class InventoryService:
    def __init__(self):
        self.products = []
        self.transactions = []
        self.removed_products = []
    def _validate_low_stock_threshold(self, low_stock_threshold):
        if isinstance(low_stock_threshold, bool) or not isinstance(low_stock_threshold, int):
            raise ValueError("Low stock threshold must be an integer")
        if low_stock_threshold < 0:
            raise ValueError("Low stock threshold cannot be negative")
        return low_stock_threshold
    def get_transactions(self):
        return self.transactions.copy()
    def _get_transaction_groups(self):
        stock_in_transactions = [transaction for transaction in self.transactions if transaction["type"] == "STOCK-IN"]
        stock_out_transactions = [transaction for transaction in self.transactions if transaction["type"] == "STOCK-OUT"]
        return stock_in_transactions, stock_out_transactions
    def get_transaction_summary(self):
        stock_in_transactions, stock_out_transactions = self._get_transaction_groups()
        return {"total_transactions": len(self.transactions), "stock_in_transactions": len(stock_in_transactions), "stock_out_transactions": len(stock_out_transactions), "total_stock_in_quantity": sum(transaction["quantity"] for transaction in stock_in_transactions), "total_stock_out_quantity": sum(transaction["quantity"] for transaction in stock_out_transactions),}
    def get_transaction_value_summary(self):
        stock_in_transactions, stock_out_transactions = self._get_transaction_groups()
        return {"total_stock_in_value": sum(transaction["total_value"] for transaction in stock_in_transactions), "total_stock_out_value": sum(transaction["total_value"] for transaction in stock_out_transactions),}
    def save_inventory(self, file_path):
        save_inventory_data(self.products, self.transactions, file_path)
    def load_inventory(self, file_path):
        self.products, self.transactions = load_inventory_data(file_path)
    def add_product(self, product):
        for existing_product in self.products:
            if existing_product.product_id == product.product_id:
                raise ValueError("Product ID already exists")
        self.products.append(product)
    def get_all_products(self):
        return self.products.copy()
    def get_removed_products(self):
        return self.removed_products.copy()
    def get_product(self, product_id):
        for product in self.products:
            if product.product_id == product_id:
                return product
        raise ValueError("Product not found")
    def update_quantity(self, product_id, amount):
        product = self.get_product(product_id)
        new_quantity = product.quantity + amount
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        product.quantity = new_quantity
    def _record_transaction(self, product, transaction_type, quantity):
        self.transactions.append({"product_id": product.product_id, "product_name": product.name, "price": product.price, "type": transaction_type, "quantity": quantity, "total_value": product.price * quantity, "timestamp": datetime.now().isoformat()})
    def stock_in(self, product_id, quantity):
        self._validate_product_id(product_id)
        self._validate_stock_quantity(quantity, "Stock-in")
        if quantity <= 0:
            raise ValueError("Stock-in quantity must be greater than zero")
        product = self.get_product(product_id)
        self.update_quantity(product_id, quantity)
        self._record_transaction(product, "STOCK-IN", quantity)
    def stock_out(self, product_id, quantity):
        self._validate_product_id(product_id)
        self._validate_stock_quantity(quantity, "Stock-out")
        if quantity <= 0:
            raise ValueError("Stock-out quantity must be greater than zero")
        product = self.get_product(product_id)
        self.update_quantity(product_id, -quantity)
        self._record_transaction(product, "STOCK-OUT", quantity)
    def update_product(self, product_id, name=None, price=None, category=None):
        product = self.get_product(product_id)
        if name is not None:
            if not name or not name.strip():
                raise ValueError("Product name cannot be empty")
            product.name = name.strip().title()
        if price is not None:
            if isinstance(price, bool) or not isinstance(price, (int, float)):
                raise ValueError("Price must be a number")
            if price < 0:
                raise ValueError("Price cannot be negative")
            product.price = price
        if category is not None:
            if not category or not category.strip():
                raise ValueError("Category cannot be empty")
            product.category = category.strip().title()
    def remove_product(self, product_id):
        product = self.get_product(product_id)
        self.products.remove(product)
        self.removed_products.append(product)
    def restore_product(self, product_id):
        for product in self.removed_products:
            if product.product_id == product_id:
                self.removed_products.remove(product)
                self.products.append(product)
                return
        raise ValueError("Removed product not found")
    def calculate_total_value(self):
        total = 0
        for product in self.products:
            total += product.price * product.quantity
        return total
    def get_low_stock_products(self, threshold=5):
        return [product for product in self.products if 0 < product.quantity <= threshold]
    def get_out_of_stock_products(self):
        return [product for product in self.products if product.quantity == 0]
    def get_product_stock_status(self, product_id, low_stock_threshold=5):
        self._validate_low_stock_threshold(low_stock_threshold)
        product = self.get_product(product_id)
        if product.quantity == 0:
            return "OUT OF STOCK"
        elif product.quantity <= low_stock_threshold:
            return "LOW STOCK"
        else:
            return "IN STOCK"
    def get_inventory_alerts(self, low_stock_threshold=5):
        self._validate_low_stock_threshold(low_stock_threshold)
        alerts = []
        for product in self.products:
            if product.quantity == 0:
                alerts.append({"product_id": product.product_id, "product_name": product.name, "status": "OUT OF STOCK", "quantity": product.quantity,})
            elif product.quantity <= low_stock_threshold:
                alerts.append({"product_id": product.product_id, "product_name": product.name, "status": "LOW STOCK", "quantity": product.quantity,})
        return alerts
    def search_products(self, search_term):
            search_term = search_term.strip().lower()
            return [product for product in self.products if search_term in product.name.lower() or search_term in product.category.lower()]
    def search_products_by_category(self, category):
        return self.get_products_by_category(category)
    def get_products_by_category(self, category):
        category = category.strip().lower()
        return [product for product in self.products if product.category.lower() == category]
    def count_products_by_category(self):
        category_counts = {}
        for product in self.products:
            category = product.category
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        return category_counts
    def total_quantity_by_category(self):
        category_quantities = {}
        for product in self.products:
            category = product.category
            if category in category_quantities:
                category_quantities[category] += product.quantity
            else:
                category_quantities[category] = product.quantity
        return category_quantities
    def total_value_by_category(self):
        category_values = {}
        for product in self.products:
            category = product.category
            product_value = product.price * product.quantity
            if category in category_values:
                category_values[category] += product_value
            else:
                category_values[category] = product_value
        return category_values
    def _build_category_summary(self, products):
        category_summary = {}
        for product in products:
            category = product.category.strip().title()
            if category not in category_summary:
                category_summary[category] = {"product_count": 0, "total_quantity": 0, "total_value": 0}
            category_summary[category]["product_count"] += 1
            category_summary[category]["total_quantity"] += product.quantity
            category_summary[category]["total_value"] += product.price * product.quantity
        return category_summary
    def get_category_summary(self):
        return self._build_category_summary(self.products)
    def get_inventory_summary(self, low_stock_threshold=5):
        self._validate_low_stock_threshold(low_stock_threshold)
        total_products = len(self.products)
        total_quantity = sum(product.quantity for product in self.products)
        total_value = self.calculate_total_value()
        low_stock_products = [product for product in self.products if 0 < product.quantity <= low_stock_threshold]
        out_of_stock_products = self.get_out_of_stock_products()
        return {"total_products": total_products, "total_quantity": total_quantity, "total_value": total_value, "low_stock_count": len(low_stock_products), "out_of_stock_count": len(out_of_stock_products)}
    def _filter_products_by_category(self, category):
        if category is None:
            return self.products
        normalized_category = category.strip().lower()
        return [product for product in self.products if product.category.lower() == normalized_category]
    def generate_inventory_report(self, low_stock_threshold=5, title="INVENTORY REPORT", category=None):
        self._validate_low_stock_threshold(low_stock_threshold)
        if not title or not str(title).strip():
            raise ValueError("Report title cannot be empty")
        if category is not None and not str(category).strip():
            raise ValueError("Category cannot be empty")
        generated_date = datetime.now().strftime("%d %B %Y %H:%M")
        products = self._filter_products_by_category(category)
        total_quantity = sum(product.quantity for product in products)
        total_value = sum(product.price * product.quantity for product in products)
        low_stock_products = [product for product in products if 0 < product.quantity <= low_stock_threshold]
        out_of_stock_products = [product for product in products if product.quantity == 0]
        low_stock_count = len(low_stock_products)
        out_of_stock_count = len(out_of_stock_products)
        summary = {"total_products": len(products), "total_quantity": total_quantity, "total_value": total_value, "low_stock_count": low_stock_count, "out_of_stock_count": out_of_stock_count,}
        transaction_summary = self.get_transaction_summary()
        transaction_value_summary = self.get_transaction_value_summary()
        report = []
        report.append("========================================")
        report.append(f"           {title}")
        report.append("========================================")
        report.append("")
        report.append(f"Report Generated: {generated_date}")
        report.append("")
        report.append(f"Total Products: {summary['total_products']}")
        report.append(f"Total Quantity: {summary['total_quantity']}")
        report.append(f"Total Inventory Value: ₦{summary['total_value']:,.2f}")
        report.append(f"Low Stock: {summary['low_stock_count']}")
        report.append(f"Out of Stock: {summary['out_of_stock_count']}")
        report.append("")
        report.append("Low Stock Products:")
        report.append("----------------------------------------")
        for product in low_stock_products:
            report.append(f"{product.name} - Quantity: {product.quantity}")
        report.append("")
        report.append("Out of Stock Products:")
        report.append("----------------------------------------")
        for product in out_of_stock_products:
            report.append(f"{product.name} - Quantity: {product.quantity} " f"- Category: {product.category}")
        report.append("")
        report.append("Stock Movement:")
        report.append("----------------------------------------")
        report.append(f"Stock-In Transactions: " f"{transaction_summary['stock_in_transactions']}")
        report.append(f"Stock-In Quantity: " f"{transaction_summary['total_stock_in_quantity']}")
        report.append(f"Stock-In Value: " f"₦{transaction_value_summary['total_stock_in_value']:,.2f}")
        report.append("")
        report.append(f"Stock-Out Transactions: " f"{transaction_summary['stock_out_transactions']}")
        report.append(f"Stock-Out Quantity: " f"{transaction_summary['total_stock_out_quantity']}")
        report.append(f"Stock-Out Value: " f"₦{transaction_value_summary['total_stock_out_value']:,.2f}")
        category_summary = self._build_category_summary(products)
        report.append("")
        report.append("Categories:")
        report.append("----------------------------------------")
        for category, data in category_summary.items():
            report.append(f"{category}")
            report.append(f"Products: {data['product_count']}")
            report.append(f"Quantity: {data['total_quantity']}")
            report.append(f"Value: ₦{data['total_value']:,.2f}")
            report.append("")
        return "\n".join(report)
    def save_inventory_report(self, file_path):
        if not file_path or not str(file_path).strip():
            raise ValueError("File path cannot be empty")
        report = self.generate_inventory_report()
        save_inventory_report(report, file_path)
    def calculate_total_inventory_value(self, products):
        return sum(product["price"] * product["quantity"] for product in products)
    def _validate_product_id(self, product_id):
        if isinstance(product_id, bool) or not isinstance(product_id, int):
            raise ValueError("Product ID must be an integer")
    def _validate_stock_quantity(self, quantity, transaction_type):
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError(f"{transaction_type} quantity must be an integer")
    def get_products_by_inventory_value(self):
        return sorted(self.products, key=lambda product: product.price * product.quantity, reverse=True)
    def get_top_products_by_inventory_value(self, limit):
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("Limit must be an integer")
        if limit <= 0:
            raise ValueError("Limit must be greater than zero")
        products = self.get_products_by_inventory_value()
        return products[:limit]
    def get_categories_by_inventory_value(self):
        category_values = self.total_value_by_category()
        return sorted(category_values.items(), key=lambda item: item[1], reverse=True)
    def get_low_stock_percentage(self, low_stock_threshold=5):
        self._validate_low_stock_threshold(low_stock_threshold)
        total_products = len(self.products)
        if total_products == 0:
            return 0.0
        low_stock_count = len(self.get_low_stock_products(low_stock_threshold))
        return (low_stock_count / total_products) * 100
    def get_out_of_stock_percentage(self):
        total_products = len(self.products)
        if total_products == 0:
            return 0.0
        out_of_stock_count = len(self.get_out_of_stock_products())
        return (out_of_stock_count / total_products) * 100
    def get_stock_health_score(self):
        total_products = len(self.products)
        if total_products == 0:
            return 0.0
        out_of_stock_count = len(self.get_out_of_stock_products())
        return ((total_products - out_of_stock_count) / total_products) * 100
    def get_stock_status_counts(self, low_stock_threshold=5):
        self._validate_low_stock_threshold(low_stock_threshold)
        return {"in_stock": len([product for product in self.products if product.quantity > low_stock_threshold]), "low_stock": len(self.get_low_stock_products(low_stock_threshold)), "out_of_stock": len(self.get_out_of_stock_products()),}
    def get_inventory_value_percentage(self):
        total_value = self.calculate_total_value()
        if total_value == 0:
            return {product.name: 0.0 for product in self.products}
        return {product.name: round(((product.price * product.quantity) / total_value) * 100, 2) for product in self.products}
    def get_dashboard_data(self, low_stock_threshold=5):
        self._validate_low_stock_threshold(low_stock_threshold)
        summary = self.get_inventory_summary(low_stock_threshold)
        stock_counts = self.get_stock_status_counts(low_stock_threshold)
        products_by_value = self.get_products_by_inventory_value()
        top_products_with_values = [{"name": product.name, "value": product.price * product.quantity} for product in products_by_value]
        top_products_by_value = [product.name for product in products_by_value]
        top_product = (products_by_value[0].name if products_by_value else None)
        category_values = self.total_value_by_category()
        inventory_value_percentage = self.get_inventory_value_percentage()
        top_category = (max(category_values, key=category_values.get) if category_values else None)
        attention_products = [product.name for product in self.products if product.quantity == 0 or product.quantity <= low_stock_threshold]
        attention_count = len(attention_products)
        return {"total_products": summary["total_products"], "total_quantity": summary["total_quantity"], "total_value": summary["total_value"], "in_stock": stock_counts["in_stock"], "low_stock": stock_counts["low_stock"], "out_of_stock": stock_counts["out_of_stock"], "stock_health": self.get_stock_health_score(), "top_product": top_product, "category_values": category_values, "inventory_value_percentage": inventory_value_percentage, "top_category": top_category, "attention_products": attention_products, "top_products_by_value": top_products_by_value, "top_products_with_values": top_products_with_values, "attention_count": attention_count,}