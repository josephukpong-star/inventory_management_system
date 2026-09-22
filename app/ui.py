from app.models import Product
def format_currency(amount):
    return f"₦{amount:,.2f}"
def display_menu():
    print("========================================")
    print("       INVENTORY MANAGEMENT SYSTEM")
    print("========================================")
    print()
    print("1. Add Product")
    print("2. View Products")
    print("3. Search Product")
    print("4. Stock In")
    print("5. Stock Out")
    print("6. Remove Product")
    print("7. Inventory Summary")
    print("8. Save Inventory")
    print("9. Load Inventory")
    print("10. Category Summary")
    print("11. Inventory Report")
    print("12. Transaction History")
    print("13. Transaction Summary")
    print("14. Transaction Value Summary")
    print("15. Exit")
    print("16. Dashboard")
    print("17. Inventory Alerts")
    print("18. Save Inventory Report")
    print("19. Update Product")
    print("20. View Removed Products")
    print("21. Restore Product")
    print("22. Permanently Delete Product")
    print("23. View Deleted Products History")
def get_menu_choice():
    while True:
        try:
            choice = int(input("Choose an option: "))
            if 1 <= choice <= 23:
                return choice
            print("Invalid choice. Please enter a number between 1 and 23.")
        except ValueError:
            print("Invalid input. Please enter a number.")
def get_stock_status(quantity, low_stock_threshold=5):
    if isinstance(low_stock_threshold, bool) or not isinstance(low_stock_threshold, int):
        raise ValueError("Low stock threshold must be an integer")
    if low_stock_threshold < 0:
        raise ValueError("Low stock threshold cannot be negative")
    if quantity == 0:
        return "OUT OF STOCK"
    elif quantity <= low_stock_threshold:
        return "LOW STOCK"
    else:
        return "IN STOCK"       
def display_products(products):
    print("========================================")
    print("           INVENTORY PRODUCTS")
    print("========================================")
    if not products:
        print("No products found")
        return
    for product in products:
        print()
        print(f"ID: {product.product_id}")
        print(f"Name: {product.name}")
        print(f"Price: {format_currency(product.price)}")
        print(f"Quantity: {product.quantity}")
        stock_status = get_stock_status(product.quantity)
        print(f"Stock Status: {stock_status}") 
def display_removed_products(products):
    print("========================================")
    print("            REMOVED PRODUCTS")
    print("========================================")
    if not products:
        print("No removed products found")
        return
    for product in products:
        print()
        print(f"ID: {product.product_id}")
        print(f"Name: {product.name}")
        print(f"Price: {format_currency(product.price)}")
        print(f"Quantity: {product.quantity}")
        print(f"Category: {product.category}")
def display_deleted_products(deleted_records):
    print("\nDELETED PRODUCTS HISTORY")
    if not deleted_records:
        print("No deleted products found")
        return
    for record in deleted_records:
        product = record["product"]
        print(f"ID: {product.product_id}")
        print(f"Name: {product.name}")
        print(f"Price: {format_currency(product.price)}")
        print(f"Quantity: {product.quantity}")
        print(f"Category: {product.category}")
        print(f"Deleted At: {record['deleted_at']}")
        print(f"Action: {record['action']}")
        print("-" * 30)
def get_product_input():
    while True:
        try:
            product_id = int(input("Enter Product ID: "))
            break
        except ValueError:
            print("Invalid Product ID. Please enter a number.")
    name = input("Enter Product Name: ")
    while True:
        try:
            price = float(input("Enter Product Price: "))
            if price < 0:
                print("Price cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid Price. Please enter a number.")
    while True:
        try:
            quantity = int(input("Enter Product Quantity: "))
            if quantity < 0:
                print("Quantity cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid Quantity. Please enter a whole number.")
    category = input("Enter Product Category: ")
    return Product(product_id, name, price, quantity, category)
def get_product_update_input():
    product_id = get_product_id()
    name = input("Enter new product name (press Enter to keep current): ")
    while True:
        price_input = input("Enter new product price (press Enter to keep current): ")
        if price_input == "":
            price = None
            break
        try:
            price = float(price_input)
            if price < 0:
                print("Price cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid Price. Please enter a number.")
    category = input("Enter new product category (press Enter to keep current): ")
    return product_id, name or None, price, category or None
def get_search_term():
    return input("Enter search term: ")
def get_product_id():
    while True:
        try:
            product_id = int(input("Enter Product ID: "))
            return product_id
        except ValueError:
            print("Invalid Product ID. Please enter a number.")
def get_restore_product_id():
    while True:
        try:
            product_id = int(input("Enter Product ID to restore: "))
            return product_id
        except ValueError:
            print("Invalid Product ID. Please enter a number.")
def get_permanently_delete_product_id():
    while True:
        try:
            return int(input("Enter Product ID to permanently delete: "))
        except ValueError:
            print("Invalid Product ID. Please enter a number.")
def get_confirmation(prompt):
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ("y", "n"):
            return response == "y"
        print("Invalid input. Please enter y or n.")
def get_quantity_change():
    while True:
        try:
            quantity_change = int(input("Enter quantity change: "))
            return quantity_change
        except ValueError:
            print("Invalid quantity change. Please enter a whole number.")
def display_inventory_summary(summary):
    print("========================================")
    print("         INVENTORY SUMMARY")
    print("========================================")
    print(f"Total Products: {summary['total_products']}")
    print(f"Total Quantity: {summary['total_quantity']}")
    print(f"Total Inventory Value: {format_currency(summary['total_value'])}")
    print(f"Low Stock: {summary['low_stock_count']}")
    print(f"Out of Stock: {summary.get('out_of_stock_count', 0)}")
def display_inventory_report(report):
    print(report)
def display_transaction_history(transactions):
    print("============================================================")
    print("                    TRANSACTION HISTORY")
    print("============================================================")
    if not transactions:
        print("No transactions found.")
        return
    for transaction in transactions:
        print()
        print(f"Product ID:     {transaction['product_id']}")
        print(f"Product Name:   {transaction['product_name']}")
        print(f"Type:           {transaction['type']}")
        print(f"Quantity:       {transaction['quantity']}")
        print(f"Unit Price:     {format_currency(transaction['price'])}")
        print(f"Total Value:    {format_currency(transaction['total_value'])}")
        print(f"Timestamp:      {transaction['timestamp']}")
        print("------------------------------------------------------------")
    print(f"Total Transactions: {len(transactions)}")
def display_category_summary(summary):
    print("========================================")
    print("          CATEGORY SUMMARY")
    print("========================================")
    if not summary:
        print("No categories found.")
        return
    for category, data in summary.items():
        print()
        print(f"Category: {category}")
        print(f"Products: {data['product_count']}")
        print(f"Quantity: {data['total_quantity']}")
        print(f"Value: {format_currency(data['total_value'])}")
def display_dashboard(dashboard_data):
    print("========================================")
    print("          INVENTORY DASHBOARD")
    print("========================================")
    print()
    print(f"Total Products:       {dashboard_data['total_products']}")
    print(f"Total Quantity:       {dashboard_data['total_quantity']}")
    print(
        f"Inventory Value:      "
        f"{format_currency(dashboard_data['total_value'])}")
    print()
    print(f"In Stock:             {dashboard_data['in_stock']}")
    print(f"Low Stock:            {dashboard_data['low_stock']}")
    print(f"Out of Stock:         {dashboard_data['out_of_stock']}")
    print()
    print(f"Stock Health:         {dashboard_data['stock_health']:.2f}%")
    print(f"Top Product:          {dashboard_data['top_product']}")
    print(f"Top Category:         {dashboard_data.get('top_category')}")
    print()
    print("Top Products by Inventory Value:")
    top_products_with_values = dashboard_data.get("top_products_with_values", [])
    if top_products_with_values:
        for position, product in enumerate(top_products_with_values, start=1):
            print(f"{position}. {product['name']} - " f"{format_currency(product['value'])}")
    else:
        top_products_by_value = dashboard_data.get("top_products_by_value", [])
        for position, product in enumerate(top_products_by_value, start=1): 
            print(f"{position}. {product}")
    print()
    attention_count = dashboard_data.get("attention_count")
    if attention_count is not None:
        print(f"Attention Required: {attention_count}")
    else:
        print("Attention Required:")
    attention_products = dashboard_data.get("attention_products", [])
    if attention_products:
        for product in attention_products:
            print(f"- {product}")
    else:   
        print("None")
    print()
    print("Inventory Value Distribution:")
    inventory_value_percentage = dashboard_data.get("inventory_value_percentage", {})
    for product, percentage in inventory_value_percentage.items():
        print(f"{product}: {percentage:.2f}%")
    print()
    print("Categories:")
    for category, value in dashboard_data.get("category_values", {}).items():
        print(f"{category}: {format_currency(value)}")
    print()
    print("========================================")
def display_inventory_alerts(alerts):
    print("========================================")
    print("          INVENTORY ALERTS")
    print("========================================")
    if not alerts:
        print("No inventory alerts.")
    else:
        for alert in alerts:
            print(f"{alert['product_name']} - " f"{alert['status']} - " f"{alert['quantity']} units")
    print("========================================")
def display_transaction_summary(summary):
    print("========================================")
    print("       TRANSACTION SUMMARY")
    print("========================================")
    print()
    print(f"Total Transactions: {summary['total_transactions']}")
    print( f"Stock-In Transactions: " f"{summary['stock_in_transactions']}")
    print(f"Stock-Out Transactions: " f"{summary['stock_out_transactions']}")
    print(f"Total Stock-In Quantity: " f"{summary['total_stock_in_quantity']}")
    print(f"Total Stock-Out Quantity: " f"{summary['total_stock_out_quantity']}")
    print()
    print("========================================")
def display_transaction_value_summary(summary):
    print("========================================")
    print("     TRANSACTION VALUE SUMMARY")
    print("========================================")
    print()
    print(f"Total Stock-In Value: " f"{format_currency(summary['total_stock_in_value'])}")
    print(f"Total Stock-Out Value: " f"{format_currency(summary['total_stock_out_value'])}")
    print()
    print("========================================")