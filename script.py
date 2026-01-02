import datetime
import json
import os

# Database files
DB_FILE = "market_data.json"
INVENTORY_FILE = "inventory_data.json"

# Admin password for special actions
ADMIN_PASSWORD = "1234"


# --- Helper Functions for User Data ---

def load_users():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "lova": {"password": "lova", "balance": 50000, "receipts": []},
            "yuval": {"password": "zona", "balance": 100, "receipts": []},
            "admin": {"password": "1234", "balance": 10000000, "receipts": []}
        }
        save_users(initial_data)
        return initial_data
    with open(DB_FILE, "r") as f:
        data = json.load(f)
        for user in data:
            if "receipts" not in data[user]:
                data[user]["receipts"] = []
        return data


def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return []
    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)


def save_inventory(data):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_confirm(prompt):
    while True:
        choice = input(f"{prompt} (y/n) » ").lower().strip()
        if choice == 'y': return True
        if choice == 'n': return False
        print("  ❌ Invalid input. Please enter 'y' or 'n'.")


def verify_password_with_limit(correct_password, limit=3):
    attempts = limit
    while attempts > 0:
        entered_pass = input(f"  🔑 Enter password ({attempts} attempts left) » ")
        if entered_pass == correct_password:
            return True
        attempts -= 1
        if attempts > 0:
            print(f"  ❌ Incorrect password.")
    print("  🚫 Too many failed attempts.")
    return False


# --- Stock Management Function ---

def validate_and_get_qty(product):
    while True:
        try:
            req_qty = int(input(f"  🔢 How many {product['name']}? (In Stock: {product['stock']}) » "))
            if req_qty <= 0:
                print("  ⚠️ Please enter a positive number.")
                continue

            if req_qty <= product['stock']:
                return req_qty
            else:
                print(f"  ❌ There are not enough products for your request. Only {product['stock']} left.")
                if get_confirm("  🤔 Do you want to change the quantity?"):
                    continue
                else:
                    print("  ↩️ Returning to main menu...")
                    return None
        except ValueError:
            print("  ⚠️ Invalid input. Please enter a number.")


# Initial Load
users = load_users()
inventory = load_inventory()
promo_codes = {"king10": 0.1, "backend20": 0.2, "LOVA": 1.0}

# --- Main Loop ---
while True:
    print("\n" + "═" * 45)
    print("║    DATABASE-DRIVEN MARKET SYSTEM v27        ║")
    print("═" * 45)

    logged_in = False
    current_user = ""
    user_cart = []
    total_sum = 0

    u_input = input("  👤 Username » ")
    if u_input in users:
        if verify_password_with_limit(users[u_input]["password"]):
            current_user = u_input
            print(f"\n✅ Access Granted! Welcome, {current_user.upper()}.")
            logged_in = True
        else:
            continue
    else:
        print("  ❌ User not found.")
        continue

    while logged_in:
        keep_shopping = True
        categories = sorted(list(set(item["category"] for item in inventory)))

        while keep_shopping:
            print("\n" + "─" * 40)
            print(f"  MAIN MENU - USER: {current_user.upper()} | BALANCE: ${users[current_user]['balance']:,.2f}")
            for i, cat in enumerate(categories, 1):
                print(f"  [{i}] {cat.capitalize()}")
            print(f"  [9] 📜 History Settings | [10] 🔐 Password")

            if current_user == "admin":
                print(f"  [11] ⚙️ ADMIN SETTINGS")

            user_input = input("\n  🛒 Choice » ").lower()

            if user_input == 'logout':
                logged_in = False
                break

            # --- History Settings (New Option 9) ---
            if user_input == '9':
                print("\n" + "📜" + "─" * 10 + " HISTORY SETTINGS " + "─" * 10)
                print("  [1] View Receipt History")
                print("  [2] Delete All History")
                print("  [3] Back")
                hist_choice = input("\n  🚀 Selection » ")

                if hist_choice == '1':
                    user_receipts = users[current_user].get("receipts", [])
                    if not user_receipts:
                        print("\n  📭 No receipts found in history.")
                    else:
                        print(f"\n--- {current_user.upper()}'S HISTORY ---")
                        for idx, r in enumerate(user_receipts, 1):
                            print(f"\n Receipt #{idx}:\n{r}\n" + "─" * 40)

                elif hist_choice == '2':
                    if get_confirm("  ⚠️ Are you sure you want to PERMANENTLY delete all history?"):
                        users[current_user]["receipts"] = []
                        save_users(users)
                        print("  ✅ History cleared successfully.")
                continue

            # --- Admin Settings Menu ---
            if user_input == '11' and current_user == "admin":
                print("\n" + "🛠️" + "─" * 10 + " ADMIN SETTINGS " + "─" * 10)
                print("  [1] Add New Product")
                print("  [2] Deposit Balance to User")
                print("  [3] Back")
                admin_choice = input("\n  🚀 Select Admin Action » ")

                if admin_choice == '1':
                    new_name = input("  Product Name » ").lower()
                    try:
                        new_price = float(input("  Price » "))
                        new_cat = input("  Category » ").lower()
                        new_stock = int(input("  Initial Stock » "))
                        inventory.append(
                            {"name": new_name, "price": new_price, "category": new_cat, "stock": new_stock})
                        save_inventory(inventory)
                        print(f"  ✅ Added {new_name} to database!")
                    except ValueError:
                        print("  ⚠️ Invalid input.")

                elif admin_choice == '2':
                    target_user = input("  👤 Enter target username » ").lower()
                    if target_user in users:
                        try:
                            amount = float(input(f"  💵 Amount to add to {target_user} » "))
                            if amount > 0:
                                users[target_user]['balance'] += amount
                                save_users(users)
                                print(
                                    f"  ✅ Success! {target_user}'s new balance: ${users[target_user]['balance']:,.2f}")
                            else:
                                print("  ⚠️ Amount must be positive.")
                        except ValueError:
                            print("  ⚠️ Invalid amount.")
                    else:
                        print("  ❌ User not found.")
                continue

            # --- Change Password Logic ---
            if user_input == '10':
                if get_confirm("\n  🔐 Change password?"):
                    if verify_password_with_limit(users[current_user]["password"]):
                        new_p = input("  🆕 New password » ")
                        sec_new_p = input("  🔄 Enter your new password again » ")
                        if new_p == sec_new_p:
                            users[current_user]["password"] = new_p
                            save_users(users)
                            print("  ✅ Success! Password updated.")
                        else:
                            print("  ❌ Error: The new passwords do not match.")
                continue

            # Category Selection
            cat_choice = ""
            if user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(categories): cat_choice = categories[idx]
            elif user_input in categories:
                cat_choice = user_input

            if not cat_choice: continue

            # --- Shopping Loop ---
            while keep_shopping:
                print(f"\n" + "═" * 10 + f" {cat_choice.upper()} MENU " + "═" * 10)
                items_in_cat = [i for i in inventory if i["category"] == cat_choice]
                for i, item in enumerate(items_in_cat, 1):
                    print(f"  [{i}] {item['name']:<15} | ${item['price']:,.2f} (Stock: {item['stock']})")

                item_input = input(f"\n  📦 Select item or 'back' » ").lower()
                if item_input == 'back': break

                found_item = None
                if item_input.isdigit():
                    idx = int(item_input) - 1
                    if 0 <= idx < len(items_in_cat): found_item = items_in_cat[idx]
                else:
                    found_item = next((i for i in items_in_cat if i["name"].lower() == item_input), None)

                if found_item:
                    qty = validate_and_get_qty(found_item)
                    if qty:
                        user_cart.append({"name": found_item["name"], "price": found_item["price"], "quantity": qty,
                                          "total": found_item["price"] * qty})
                        total_sum += found_item["price"] * qty
                        print(f"  ✨ Added.")
                    else:
                        break

                # --- Decision Loop ---
                while True:
                    if user_cart:
                        print("\n  🛒 CURRENT CART:")
                        for i, p in enumerate(user_cart, 1):
                            print(f"  [{i}] {p['quantity']} x {p['name']:<12} | ${p['total']:,.2f}")
                        print(f"  Subtotal: ${total_sum:,.2f}")

                    print("\n  [1] Buy more | [2] Categories | [3] Checkout | [4] Remove Item")
                    step = input("  🚀 Choice » ")

                    if step == '1':
                        break
                    elif step == '2':
                        cat_choice = "";
                        break
                    elif step == '3':
                        keep_shopping = False;
                        break
                    elif step == '4':
                        try:
                            rem_idx = int(input("  🗑️ Item number » ")) - 1
                            if 0 <= rem_idx < len(user_cart):
                                rem_qty = int(input(f"  Units to remove? » "))
                                item = user_cart[rem_idx]
                                if rem_qty >= item['quantity']:
                                    popped = user_cart.pop(rem_idx)
                                    total_sum -= popped['total']
                                else:
                                    item['quantity'] -= rem_qty
                                    total_sum -= rem_qty * item['price']
                                    item['total'] = item['quantity'] * item['price']
                                print("  ✅ Cart updated.")
                            else:
                                print("  ❌ Invalid.")
                        except:
                            print("  ⚠️ Error.")
                        continue
                    else:
                        print("  ❌ Choose 1-4.")
                if step == '2' or not keep_shopping: break

        # --- Checkout Process ---
        if logged_in and user_cart:
            print("\n" + "─" * 45)
            promo_discount = 0
            applied_code = "None"
            if get_confirm("  🎟️ Promo code?"):
                code = input("  🔑 Code » ")
                if code in promo_codes:
                    promo_discount = total_sum * promo_codes[code]
                    applied_code = code
                    print(f"  ✅ Discount: -${promo_discount:,.2f}")

            final_total = total_sum - promo_discount

            if users[current_user]['balance'] >= final_total:
                if get_confirm(f"  💳 Pay ${final_total:,.2f}?"):
                    for cart_item in user_cart:
                        for inv_item in inventory:
                            if inv_item['name'] == cart_item['name']:
                                inv_item['stock'] -= cart_item['quantity']
                    save_inventory(inventory)

                    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                    receipt_lines = [f"  DATE: {timestamp}", "  " + "─" * 35]
                    for p in user_cart:
                        receipt_lines.append(f"  • {p['quantity']} x {p['name']:<12} | ${p['total']:>10,.2f}")
                    receipt_lines.append("  " + "─" * 35)
                    receipt_lines.append(f"  Subtotal:        ${total_sum:>10,.2f}")
                    if promo_discount > 0:
                        receipt_linesx.append(f"  Promo ({applied_code}): -${promo_discount:>10,.2f}")
                    receipt_lines.append(f"  FINAL TOTAL:     ${final_total:>10,.2f}")

                    users[current_user]['balance'] -= final_total
                    full_receipt = "\n".join(receipt_lines)
                    users[current_user]["receipts"].append(full_receipt)
                    save_users(users)

                    print("\n" + "█" * 45 + f"\n          OFFICIAL RECEIPT\n{full_receipt}\n" + "█" * 45)
                else:
                    print("\n❌ Cancelled.")
            else:
                print("\n🚫 Insufficient funds!")
            user_cart = [];
            total_sum = 0