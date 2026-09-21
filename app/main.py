from app.inventory_service import InventoryService
from app import ui
def add_product(inventory):
    product = ui.get_product_input()
    inventory.add_product(product)
    print("Product added successfully.")
def update_product(inventory):
    product_id, name, price, category = ui.get_product_update_input()
    inventory.update_product(product_id, name=name, price=price, category=category)
    print("Product updated successfully.")
def view_products(inventory):
    products = inventory.get_all_products()
    ui.display_products(products)
def view_removed_products(inventory):
    products = inventory.get_removed_products()
    ui.display_removed_products(products)
def view_deleted_products(inventory):
    products = inventory.get_deleted_products()
    ui.display_deleted_products(products)
def restore_product(inventory):
    product_id = ui.get_restore_product_id()
    inventory.restore_product(product_id)
    print("Product restored successfully.")
def permanently_delete_product(inventory):
    product_id = ui.get_permanently_delete_product_id()
    confirmed = ui.get_confirmation("Are you sure you want to permanently delete this product? (y/n): ")
    if not confirmed:
        print("Permanent deletion cancelled.")
        return
    inventory.permanently_delete_product(product_id)
    print("Product permanently deleted successfully.")
def search_products(inventory):
    search_term = ui.get_search_term()
    results = inventory.search_products(search_term)
    ui.display_products(results)
def stock_in(inventory):
    product_id = ui.get_product_id()
    quantity = ui.get_quantity_change()
    inventory.stock_in(product_id, quantity)
    print("Stock added successfully.")
def stock_out(inventory):
    product_id = ui.get_product_id()
    quantity = ui.get_quantity_change()
    inventory.stock_out(product_id, quantity)
    print("Stock removed successfully.")
def remove_product(inventory):
    product_id = ui.get_product_id()
    confirmed = ui.get_confirmation("Are you sure you want to remove this product?")
    if not confirmed:
        print("Product removal cancelled.")
        return
    inventory.remove_product(product_id)
    print("Product removed successfully.")
def show_inventory_summary(inventory):
    summary = inventory.get_inventory_summary()
    ui.display_inventory_summary(summary)
def save_inventory(inventory, file_path):
    inventory.save_inventory(file_path)
    print("Inventory saved successfully.")
def load_inventory(inventory, file_path):
    inventory.load_inventory(file_path)
    print("Inventory loaded successfully.")
def show_category_summary(inventory):
    summary = inventory.get_category_summary()
    ui.display_category_summary(summary)
def show_inventory_report(inventory):
    report = inventory.generate_inventory_report()
    ui.display_inventory_report(report)
def save_inventory_report(inventory):
    inventory.save_inventory_report("inventory_report.txt")
    print("Inventory report saved successfully.")
def show_transaction_history(inventory):
    transactions = inventory.get_transactions()
    ui.display_transaction_history(transactions)
def show_transaction_summary(inventory):
    summary = inventory.get_transaction_summary()
    ui.display_transaction_summary(summary)
def show_transaction_value_summary(inventory):
    summary = inventory.get_transaction_value_summary()
    ui.display_transaction_value_summary(summary)
def show_dashboard(inventory):
    dashboard_data = inventory.get_dashboard_data()
    ui.display_dashboard(dashboard_data)
def show_inventory_alerts(inventory):
    alerts = inventory.get_inventory_alerts()
    ui.display_inventory_alerts(alerts)
def main(file_path="data/inventory.json"):
    inventory = InventoryService()
    while True:
        ui.display_menu()
        choice = ui.get_menu_choice()
        try:
            if choice == 1:
                add_product(inventory)
            elif choice == 2:
                view_products(inventory)
            elif choice == 3:
                search_products(inventory)
            elif choice == 4:
                stock_in(inventory)
            elif choice == 5:
                stock_out(inventory)
            elif choice == 6:
                remove_product(inventory)
            elif choice == 7:
                show_inventory_summary(inventory)
            elif choice == 8:
                save_inventory(inventory, file_path)
            elif choice == 9:
                load_inventory(inventory, file_path)
            elif choice == 10:
                show_category_summary(inventory)
            elif choice == 11:
                show_inventory_report(inventory)
            elif choice == 12:
                show_transaction_history(inventory)
            elif choice == 13:
                show_transaction_summary(inventory)
            elif choice == 14:
                show_transaction_value_summary(inventory)
            elif choice == 15:
                print("Goodbye!")
                break
            elif choice == 16:
                show_dashboard(inventory)
            elif choice == 17:
                show_inventory_alerts(inventory)
            elif choice == 18:
                save_inventory_report(inventory)
            elif choice == 19:
                update_product(inventory)
            elif choice == 20:
                view_removed_products(inventory)
            elif choice == 21:
                restore_product(inventory)
            elif choice == 22:
                permanently_delete_product(inventory)
            elif choice == 23:
                view_deleted_products(inventory)
        except ValueError as error:
            print(f"Error: {error}")
        except FileNotFoundError:
            print("Error: Inventory file was not found.")
        except OSError as error:
            print(f"Error accessing inventory file: {error}")
    return inventory
if __name__ == "__main__":
    main()