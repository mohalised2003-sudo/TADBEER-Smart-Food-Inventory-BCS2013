# main.py
# Entry point for the TADBEER Hybrid Food Management Console Application

from operations import RescueSystem
from utils import print_banner, display_inventory_table

def select_business_mode():
    """Let the user select an exact business type and its shelf-life unit."""
    while True:
        print("\n" + "*" * 62)
        print("            WELCOME TO TADBEER MANAGEMENT SYSTEM            ")
        print("*" * 62)
        print("Select Your Business Type:")
        print("1. Restaurant")
        print("2. Cafe")
        print("3. Bakery")
        print("4. Supermarket / Grocery Store")
        
        choices = {
            "1": ("Restaurant", "hours"),
            "2": ("Cafe", "hours"),
            "3": ("Bakery", "hours"),
            "4": ("Supermarket / Grocery Store", "days"),
        }
        mode = input("Enter choice (1-4): ").strip()
        if mode in choices:
            return choices[mode]
        print("[!] Invalid choice. Please enter a number from 1 to 4.")

def display_main_menu():
    """Function 1: Main interactive menu loop driving the TADBEER application."""
    business_type, time_unit = select_business_mode()
    system = RescueSystem(business_type, time_unit)

    while True:
        print_banner(business_type)
        print("1. Add Perishable Inventory")
        print("2. Run Smart Routing (Auto-Discount & Donation Check)")
        print("3. Process Sale / Record Donation")
        print("4. View Current Inventory")
        print("5. Generate Impact Report")
        print("6. Exit")
        print("-" * 62)

        choice = input("Select an option (1-6): ").strip()

        if choice == '1':
            system.add_inventory()
        elif choice == '2':
            system.process_smart_logic()
        elif choice == '3':
            system.process_transactions()
        elif choice == '4':
            system.refresh_inventory()
            display_inventory_table(system.inventory, time_unit)
        elif choice == '5':
            system.generate_impact_report()
            print("[OK] Returning to the main menu.")
        elif choice == '6':
            system.save_data()
            print("TADBEER System closed. Thank you for supporting SDG 2: Zero Hunger!")
            break
        else:
            print("[!] Invalid selection. Please choose a number between 1 and 6.")

# Program execution entry point
if __name__ == "__main__":
    display_main_menu()
