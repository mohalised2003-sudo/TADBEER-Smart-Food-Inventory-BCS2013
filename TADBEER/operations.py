# Inventory, persistence, smart routing, POS transactions, and impact metrics.

import json
import math
import re
from datetime import date
from pathlib import Path

from models import FoodItem
from utils import display_inventory_table, print_impact_receipt


class RescueSystem:
    """Manage perishable inventory and record its sale, donation, and waste."""

    MAX_DISCOUNTED_QTY_PER_CUSTOMER_DAILY = 2

    def __init__(self, business_type, time_unit):
        self.business_type = business_type
        self.time_unit = time_unit
        self.inventory = []
        self.total_revenue = 0.0
        self.discount_savings = 0.0
        self.total_sold_items = 0
        self.total_donated_items = 0
        self.total_wasted_items = 0
        self.wasted_items_log = []
        self.transactions = []
        business_key = re.sub(r"[^a-z0-9]+", "_", business_type.casefold()).strip("_")
        self.data_file = Path(__file__).with_name(f"tadbeer_{business_key}_data.json")
        self.load_data()

    def _save_data(self):
        """Persist the current session data after each meaningful change."""
        data = {
            "business_type": self.business_type,
            "time_unit": self.time_unit,
            "inventory": [item.to_dict() for item in self.inventory],
            "total_revenue": self.total_revenue,
            "discount_savings": self.discount_savings,
            "total_sold_items": self.total_sold_items,
            "total_donated_items": self.total_donated_items,
            "total_wasted_items": self.total_wasted_items,
            "wasted_items_log": self.wasted_items_log,
            "transactions": self.transactions,
        }
        temporary_file = self.data_file.with_suffix(".tmp")
        try:
            temporary_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            temporary_file.replace(self.data_file)
        except OSError as error:
            print(f"[!] Data could not be saved: {error}")

    def save_data(self):
        """Public save action used when the user exits the application."""
        self._save_data()

    def load_data(self):
        """Restore saved inventory and metrics, or start with an empty system."""
        if not self.data_file.exists():
            return
        try:
            data = json.loads(self.data_file.read_text(encoding="utf-8"))
            if (data.get("time_unit") != self.time_unit
                    or data.get("business_type") != self.business_type):
                return
            self.inventory = [FoodItem.from_dict(row) for row in data.get("inventory", [])]
            self.total_revenue = float(data.get("total_revenue", 0.0))
            self.discount_savings = float(data.get("discount_savings", 0.0))
            self.total_sold_items = int(data.get("total_sold_items", 0))
            self.total_donated_items = int(data.get("total_donated_items", 0))
            self.total_wasted_items = int(data.get("total_wasted_items", 0))
            self.wasted_items_log = data.get("wasted_items_log", [])
            self.transactions = data.get("transactions", [])
            self._refresh_inventory()
            print(f"[+] Loaded saved TADBEER data from '{self.data_file.name}'.")
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            print(f"[!] Saved data could not be loaded ({error}). Starting with empty data.")

    def _refresh_inventory(self):
        """Refresh shelf-life and record each expired batch as waste once."""
        for item in self.inventory:
            item.refresh_time_left(self.time_unit)
            if item.status == "Waste (Expired)" and not item.waste_recorded:
                self._record_waste(item)

    def refresh_inventory(self):
        """Public refresh used before displaying current inventory."""
        self._refresh_inventory()
        self._save_data()

    def _record_waste(self, item):
        item.waste_recorded = True
        self.total_wasted_items += item.quantity
        self.wasted_items_log.append({"name": item.original_name, "quantity": item.quantity})

    def _discounted_units_bought_today(self, customer_code, item_name):
        """Count today's discounted units for one customer and product."""
        today = date.today().isoformat()
        normalized_name = item_name.casefold()
        return sum(
            transaction.get("quantity", 0)
            for transaction in self.transactions
            if transaction.get("transaction_date") == today
            and transaction.get("customer_code", "").casefold() == customer_code.casefold()
            and transaction.get("item", "").casefold() == normalized_name
            and transaction.get("discount_rate", 0) > 0
        )

    def add_inventory(self):
        """Prompt for a new batch and validate all numeric values."""
        print(f"\n--- ADD NEW ITEM ({self.business_type}) ---")
        name = input("Enter item name: ").strip()
        if not name:
            print("[!] Error: Item name cannot be empty.")
            return
        try:
            quantity = int(input("Enter quantity: "))
            original_price = float(input("Enter original price per unit (RM): "))
            time_left = float(input(f"Enter remaining shelf-life in {self.time_unit}: "))
            if quantity <= 0 or not math.isfinite(original_price) or original_price < 0:
                raise ValueError
            if not math.isfinite(time_left) or time_left < 0:
                raise ValueError
        except ValueError:
            print("[!] Enter a positive whole quantity and finite, non-negative price and shelf-life.")
            return

        item = FoodItem(name, quantity, original_price, time_left)
        item.refresh_time_left(self.time_unit)
        self.inventory.append(item)
        if item.status == "Waste (Expired)":
            self._record_waste(item)
        self._save_data()
        print(f"[+] Successfully added '{name}' to TADBEER inventory.")

    def process_smart_logic(self):
        """Refresh product statuses and show donation/waste alerts."""
        print("\n--- RUNNING TADBEER SMART ROUTING ALGORITHM ---")
        self._display_routing_rules()
        self._refresh_inventory()
        if not self.inventory:
            print("[!] Inventory is currently empty.")
            return
        for item in self.inventory:
            if item.status == "Urgent Donation":
                print(f"[SIMULATED DONATION ALERT]: {item.quantity}x '{item.original_name}' is ready for pickup.")
            elif item.status == "Waste (Expired)":
                print(f"[WASTE]: {item.quantity}x '{item.original_name}' is expired and cannot be sold or donated.")
        self._save_data()
        print("[OK] Smart routing complete.")
        display_inventory_table(self.inventory, self.time_unit)

    def _display_routing_rules(self):
        """Explain the thresholds used by the routing algorithm."""
        print(f"Rules (remaining shelf-life in {self.time_unit}):")
        print(f"  More than 3 {self.time_unit}: full price")
        print(f"  More than 2 and up to 3 {self.time_unit}: 15% discount")
        print(f"  From 1 to 2 {self.time_unit}: 30% discount")
        print(f"  More than 0 but less than 1 {self.time_unit}: donation category")
        print("  0 or less: expired; blocked from sale and donation")

    def process_transactions(self):
        """Sell eligible items or record an urgent-donation handoff."""
        print("\n--- POINT OF SALE (POS) & DONATION RECORD ---")
        self._refresh_inventory()
        self._save_data()
        display_inventory_table(self.inventory, self.time_unit)
        if not self.inventory:
            return
        try:
            choice = int(input("Enter item number to sell/record donation (0 to cancel): "))
            if choice == 0:
                return
            if not 1 <= choice <= len(self.inventory):
                print("[!] Invalid item number.")
                return
            item = self.inventory[choice - 1]
            if item.status == "Waste (Expired)":
                print(f"[X] Blocked: '{item.original_name}' is expired and marked as waste.")
                return
            quantity = int(input(f"Enter quantity to process (Available: {item.quantity}): "))
            if quantity <= 0 or quantity > item.quantity:
                print("[!] Invalid quantity.")
                return

            customer_code = ""
            if item.discount_rate > 0:
                customer_code = input("Enter customer code for the daily discounted-item limit: ").strip()
                if not customer_code:
                    print("[!] A customer code is required for discounted purchases.")
                    return
                already_bought = self._discounted_units_bought_today(customer_code, item.original_name)
                remaining_allowance = self.MAX_DISCOUNTED_QTY_PER_CUSTOMER_DAILY - already_bought
                if quantity > remaining_allowance:
                    print(f"[!] Daily limit: {self.MAX_DISCOUNTED_QTY_PER_CUSTOMER_DAILY} discounted units "
                          f"per customer for this item. Already purchased today: {already_bought}.")
                    return

            item.quantity -= quantity
            transaction = {
                "item": item.original_name,
                "quantity": quantity,
                "status": item.status,
                "transaction_date": date.today().isoformat(),
                "discount_rate": item.discount_rate,
            }
            if customer_code:
                transaction["customer_code"] = customer_code.casefold()
            if item.status == "Urgent Donation":
                self.total_donated_items += quantity
                transaction["value_rm"] = 0.0
                print(f"[DONATION RECORDED - SIMULATION]: {quantity}x '{item.original_name}'.")
            else:
                revenue = quantity * item.current_price
                savings = quantity * (item.original_price - item.current_price)
                self.total_revenue += revenue
                self.discount_savings += savings
                self.total_sold_items += quantity
                transaction["revenue_rm"] = round(revenue, 2)
                transaction["discount_savings_rm"] = round(savings, 2)
                print(f"[SOLD]: {quantity}x '{item.name}' sold for RM {revenue:.2f}.")
            self.transactions.append(transaction)
            if item.quantity == 0:
                self.inventory.remove(item)
            self._save_data()
        except ValueError:
            print("[!] Enter valid whole numbers for item number and quantity.")

    def generate_impact_report(self):
        """Display the accumulated impact metrics and transaction history totals."""
        self._refresh_inventory()
        self._save_data()
        print_impact_receipt(
            self.total_revenue,
            self.discount_savings,
            self.total_sold_items,
            self.total_donated_items,
            self.total_wasted_items,
            self.wasted_items_log,
            self.business_type,
        )
