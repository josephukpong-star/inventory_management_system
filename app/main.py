from app.inventory_service import InventoryService
from app import ui
def main(file_path="data/inventory.json"):
    inventory = InventoryService()
    while True:
        ui.display_menu()
        choice = ui.get_menu_choice()
        try:
            if choice == 1:
                product = ui.get_product_input()
                inventory.add_product(product)
                print("Product added successfully.")
            elif choice == 2:
                products = inventory.get_all_products()
                ui.display_products(products)
            elif choice == 3:
                search_term = ui.get_search_term()
                results = inventory.search_products(search_term)
                ui.display_products(results)
            elif choice == 4:
                product_id = ui.get_product_id()
                quantity = ui.get_quantity_change()
                inventory.stock_in(product_id, quantity)
                print("Stock added successfully.")
            elif choice == 5:
                product_id = ui.get_product_id()
                quantity = ui.get_quantity_change()
                inventory.stock_out(product_id, quantity)
                print("Stock removed successfully.")
            elif choice == 6:
                product_id = ui.get_product_id()
                inventory.remove_product(product_id)
                print("Product removed successfully.")
            elif choice == 7:
                summary = inventory.get_inventory_summary()
                ui.display_inventory_summary(summary)
            elif choice == 8:
                inventory.save_inventory(file_path)
                print("Inventory saved successfully.")
            elif choice == 9:
                inventory.load_inventory(file_path)
                print("Inventory loaded successfully.")
            elif choice == 10:
                summary = inventory.get_category_summary()
                ui.display_category_summary(summary)
            elif choice == 11:
                report = inventory.generate_inventory_report()
                ui.display_inventory_report(report)
            elif choice == 12:
                transactions = inventory.get_transactions()
                ui.display_transaction_history(transactions)
            elif choice == 13:
                summary = inventory.get_transaction_summary()
                ui.display_transaction_summary(summary)
            elif choice == 14:
                summary = inventory.get_transaction_value_summary()
                ui.display_transaction_value_summary(summary)
            elif choice == 15:
                print("Goodbye!")
                break
            elif choice == 16:
                dashboard_data = inventory.get_dashboard_data()
                ui.display_dashboard(dashboard_data)
            elif choice == 17:
                alerts = inventory.get_inventory_alerts()
                ui.display_inventory_alerts(alerts)
            elif choice == 18:
                inventory.save_inventory_report("inventory_report.txt")
                print("Inventory report saved successfully.")
        except ValueError as error:
            print(f"Error: {error}")
        except FileNotFoundError:
            print("Error: Inventory file was not found.")
        except OSError as error:
            print(f"Error accessing inventory file: {error}")
    return inventory
if __name__ == "__main__":
    main()