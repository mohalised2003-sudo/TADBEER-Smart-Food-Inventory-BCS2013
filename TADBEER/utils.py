# Formatted console output for TADBEER.

import datetime


def print_banner(business_type):
    print("\n" + "=" * 68)
    print("          TADBEER: SMART FOOD & INVENTORY MANAGEMENT")
    print(f"    Business type: {business_type}")
    print("=" * 68)


def display_inventory_table(inventory, time_unit):
    if not inventory:
        print("\n[!] Inventory is currently empty.")
        return
    print("\n" + "-" * 94)
    print(f"{'No.':<4} {'Item Name':<28} {'Qty':<6} {'Orig. RM':<10} "
          f"{'Curr. RM':<10} {'Left':<14} {'Status'}")
    print("-" * 94)
    for index, item in enumerate(inventory, start=1):
        remaining = f"{item.time_left:.2f} {time_unit}"
        print(f"{index:<4} {item.name[:27]:<28} {item.quantity:<6} "
              f"{item.original_price:<10.2f} {item.current_price:<10.2f} "
              f"{remaining:<14} {item.status}")
    print("-" * 94)


def print_impact_receipt(revenue, discount_savings, sold_count, donated_count,
                         wasted_count, waste_log, business_type):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "=" * 68)
    print("              TADBEER - SUSTAINABILITY IMPACT RECEIPT")
    print("=" * 68)
    print(f"Date/Time                  : {now}")
    print(f"Sector                     : {business_type}")
    print("SDG Alignment              : SDG 2 (Zero Hunger) & SDG 12 (Responsible Consumption)")
    print("-" * 68)
    print(f"Sales revenue recorded     : RM {revenue:.2f}")
    print(f"Customer discount savings  : RM {discount_savings:.2f}")
    print(f"Items sold                  : {sold_count} units")
    print(f"Donation entries (simulation): {donated_count} units")
    print(f"Items expired and wasted   : {wasted_count} units")
    print("-" * 68)
    if waste_log:
        print("Expired batches recorded:")
        for entry in waste_log:
            print(f" -> {entry['name']}: {entry['quantity']} unit(s)")
    elif wasted_count == 0:
        print("[INFO] No expired inventory has been recorded in this system yet.")
    print("=" * 68 + "\n")
