import datetime
import json
import os
import tempfile
from pathlib import Path

# Database files
DB_FILE = Path("market_data.json")
INVENTORY_FILE = Path("inventory_data.json")

# Admin password for special actions
ADMIN_PASSWORD = "1234"


# --- Helper Functions for User Data ---

def _read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_atomic(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        os.replace(tmp_name, path)
    finally:
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except OSError:
            pass


def load_users():
    if not DB_FILE.exists():
        initial_data = {
            "lova": {"password": "lova", "balance": 50000, "receipts": []},
            "yuval": {"password": "zona", "balance": 100, "receipts": []},
            "admin": {"password": "1234", "balance": 10000000, "receipts": []}
        }
        save_users(initial_data)
        return initial_data

    data = _read_json(DB_FILE, default={})
    for user in data:
        if "receipts" not in data[user]:
            data[user]["receipts"] = []
    return data


def save_users(data):
    _write_json_atomic(DB_FILE, data)


def load_inventory():
    return _read_json(INVENTORY_FILE, default=[])


def save_inventory(data):
    _write_json_atomic(INVENTORY_FILE, data)


def get_confirm(prompt):
    while True:
        choice = input(f"{prompt} (y/n) » ").lower().strip()
        if choice == "y":
            return True
        if choice == "n":
            return False
        print("  ❌ Invalid input. Please enter 'y' or 'n'.")


def read_int(prompt, *, min_value=None, max_value=None, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            val = int(raw)
        except ValueError:
            print("  ⚠️ Invalid input. Please enter a whole number.")
            continue

        if min_value is not None and val < min_value:
            print(f"  ⚠️ Please enter a number >= {min_value}.")
            continue
        if max_value is not None and val > max_value:
            print(f"  ⚠️ Please enter a number <= {max_value}.")
            continue
        return val


def read_float(prompt, *, min_value=None):
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
        except ValueError:
            print("  ⚠️ Invalid input. Please enter a number.")
            continue

        if min_value is not None and val < min_value:
            print(f"  ⚠️ Please enter a number >= {min_value}.")
            continue
        return val


def verify_password_with_limit(correct_password, limit=3):
    attempts = limit
    while attempts > 0:
        entered_pass = input(f"  🔑 Enter password ({attempts} attempts left) » ")
        if entered_pass == correct_password:
            return True
        attempts -= 1
        if attempts > 0:
            print("  ❌ Incorrect password.")
    print("  🚫 Too many failed attempts.")
    return False


# --- Stock Management Function ---

def validate_and_get_qty(product):
    while True:
        req_qty = read_int(
            f"  🔢 How many {product['name']}? (In Stock: {product['stock']}) » ",
            min_value=1
        )

        if req_qty <= product["stock"]:
            return req_qty

        print(f"  ❌ There are not enough products for your request. Only {product['stock']} left.")
        if get_confirm("  🤔 Do you want to change the quantity?"):
            continue
        print("  ↩️ Returning to main menu...")
        return None


def get_categories(inventory):
    return sorted({item.get("category", "").strip().lower() for item in inventory if item.get("category")})


def history_settings_menu(users, current_user):
    print("\n" + "📜" + "─" * 10 + " HISTORY SETTINGS " + "─" * 10)
    print("  [1] View Receipt History")
    print("  [2] Delete All History")
    print("  [3] Back")
    hist_choice = input("\n  🚀 Selection » ").strip()

    if hist_choice == "1":
        user_receipts = users[current_user].get("receipts", [])
        if not user_receipts:
            print("\n  📭 No receipts found in history.")
        else:
            print(f"\n--- {current_user.upper()}'S HISTORY ---")
            for idx, r in enumerate(user_receipts, 1):
                print(f"\n Receipt #{idx}:\n{r}\n" + "─" * 40)

    elif hist_choice == "2":
        if get_confirm("  ⚠️ Are you sure you want to PERMANENTLY delete all history?"):
            users[current_user]["receipts"] = []
            save_users(users)
            print("  ✅ History cleared successfully.")


def admin_settings_menu(users, inventory):
    print("\n" + "🛠️" + "─" * 10 + " ADMIN SETTINGS " + "─" * 10)
    print("  [1] Add New Product")
    print("  [2] Deposit Balance to User")
    print("  [3] Back")
    admin_choice = input("\n  🚀 Select Admin Action » ").strip()

    if admin_choice == "1":
        new_name = input("  Product Name » ").strip().lower()
        new_price = read_float("  Price » ", min_value=0.0)
        new_cat = input("  Category » ").strip().lower()
        new_stock = read_int("  Initial Stock » ", min_value=0)

        inventory.append({"name": new_name, "price": new_price, "category": new_cat, "stock": new_stock})
        save_inventory(inventory)
        print(f"  ✅ Added {new_name} to database!")

    elif admin_choice == "2":
        target_user = input("  👤 Enter target username » ").strip().lower()
        if target_user not in users:
            print("  ❌ User not found.")
            return

        amount = read_float(f"  💵 Amount to add to {target_user} » ", min_value=0.0)
        if amount <= 0:
            print("  ⚠️ Amount must be positive.")
            return

        users[target_user]["balance"] += amount
        save_users(users)
        print(f"  ✅ Success! {target_user}'s new balance: ${users[target_user]['balance']:,.2f}")


def change_password_flow(users, current_user):
    if not get_confirm("\n  🔐 Change password?"):
        return

    if not verify_password_with_limit(users[current_user]["password"]):
        return

    new_p = input("  🆕 New password » ").strip()
    sec_new_p = input("  🔄 Enter your new password again » ").strip()

    if new_p != sec_new_p:
        print("  ❌ Error: The new passwords do not match.")
        return

    users[current_user]["password"] = new_p
    save_users(users)
    print("  ✅ Success! Password updated.")


def choose_category(categories):
    user_input = input("\n  🛒 Choice » ").strip().lower()
    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(categories):
            return categories[idx], user_input
        return "", user_input

    if user_input in categories:
        return user_input, user_input

    return "", user_input


def find_item(items_in_cat, item_input):
    item_input = item_input.strip().lower()
    if item_input.isdigit():
        idx = int(item_input) - 1
        if 0 <= idx < len(items_in_cat):
            return items_in_cat[idx]
        return None
    return next((i for i in items_in_cat if i.get("name", "").lower() == item_input), None)


def print_cart(user_cart, total_sum):
    if not user_cart:
        return
    print("\n  🛒 CURRENT CART:")
    for i, p in enumerate(user_cart, 1):
        print(f"  [{i}] {p['quantity']} x {p['name']:<12} | ${p['total']:,.2f}")
    print(f"  Subtotal: ${total_sum:,.2f}")


def remove_item_from_cart(user_cart, total_sum):
    rem_idx = read_int("  🗑️ Item number » ", min_value=1) - 1
    if not (0 <= rem_idx < len(user_cart)):
        print("  ❌ Invalid.")
        return total_sum

    item = user_cart[rem_idx]
    rem_qty = read_int("  Units to remove? » ", min_value=1)

    if rem_qty >= item["quantity"]:
        popped = user_cart.pop(rem_idx)
        total_sum -= popped["total"]
    else:
        item["quantity"] -= rem_qty
        total_sum -= rem_qty * item["price"]
        item["total"] = item["quantity"] * item["price"]

    print("  ✅ Cart updated.")
    return total_sum


def shopping_flow(users, inventory, current_user):
    user_cart = []
    total_sum = 0.0
    keep_shopping = True

    while keep_shopping:
        categories = get_categories(inventory)

        print("\n" + "─" * 40)
        print(f"  MAIN MENU - USER: {current_user.upper()} | BALANCE: ${users[current_user]['balance']:,.2f}")

        for i, cat in enumerate(categories, 1):
            print(f"  [{i}] {cat.capitalize()}")

        print("  [9] 📜 History Settings | [10] 🔐change your Password")
        if current_user == "admin":
            print("  [11] ⚙️ ADMIN SETTINGS")

        cat_choice, raw_choice = choose_category(categories)

        if raw_choice == "logout":
            return "logout", user_cart, total_sum

        if raw_choice == "9":
            history_settings_menu(users, current_user)
            continue

        if raw_choice == "10":
            change_password_flow(users, current_user)
            continue

        if raw_choice == "11" and current_user == "admin":
            admin_settings_menu(users, inventory)
            continue

        if not cat_choice:
            continue

        # --- Category Shopping Loop ---
        while True:
            print("\n" + "═" * 10 + f" {cat_choice.upper()} MENU " + "═" * 10)
            items_in_cat = [i for i in inventory if i.get("category", "").strip().lower() == cat_choice]
            if not items_in_cat:
                print("  (No items in this category)")
                break

            for i, item in enumerate(items_in_cat, 1):
                print(f"  [{i}] {item['name']:<15} | ${item['price']:,.2f} (Stock: {item['stock']})")

            item_input = input("\n  📦 Select item or 'back' » ").strip().lower()
            if item_input == "back":
                break

            found_item = find_item(items_in_cat, item_input)
            if not found_item:
                print("  ❌ Item not found.")
                continue

            qty = validate_and_get_qty(found_item)
            if qty is None:
                break

            user_cart.append({
                "name": found_item["name"],
                "price": float(found_item["price"]),
                "quantity": qty,
                "total": float(found_item["price"]) * qty
            })
            total_sum += float(found_item["price"]) * qty
            print("  ✨ Added.")

            # --- Decision Loop ---
            while True:
                print_cart(user_cart, total_sum)
                print("\n  [1] Buy more | [2] Categories | [3] Checkout | [4] Remove Item")
                step = input("  🚀 Choice » ").strip()

                if step == "1":
                    break
                if step == "2":
                    break
                if step == "3":
                    keep_shopping = False
                    break
                if step == "4":
                    if not user_cart:
                        print("  ⚠️ Cart is empty.")
                        continue
                    try:
                        total_sum = remove_item_from_cart(user_cart, total_sum)
                    except ValueError:
                        print("  ⚠️ Invalid number.")
                    except IndexError:
                        print("  ⚠️ Invalid item selection.")
                    continue

                print("  ❌ Choose 1-4.")

            if step == "2" or not keep_shopping:
                break

    return "checkout", user_cart, total_sum


def checkout_flow(users, inventory, current_user, user_cart, total_sum, promo_codes):
    if not user_cart:
        return

    print("\n" + "─" * 45)

    promo_discount = 0.0
    applied_code = "None"

    if get_confirm("  🎟️ Promo code?"):
        code = input("  🔑 Code » ").strip().lower()
        if code in promo_codes:
            promo_discount = total_sum * promo_codes[code]
            applied_code = code
            print(f"  ✅ Discount: -${promo_discount:,.2f}")
        else:
            print("  ❌ Invalid promo code.")

    final_total = total_sum - promo_discount

    if users[current_user]["balance"] < final_total:
        print("\n🚫 Insufficient funds!")
        return

    if not get_confirm(f"  💳 Pay ${final_total:,.2f}?"):
        print("\n❌ Cancelled.")
        return

    inv_by_name = {i.get("name"): i for i in inventory}
    for cart_item in user_cart:
        inv_item = inv_by_name.get(cart_item["name"])
        if inv_item is None:
            continue
        inv_item["stock"] -= cart_item["quantity"]

    save_inventory(inventory)

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    receipt_lines = [f"  DATE: {timestamp}", "  " + "─" * 35]
    for p in user_cart:
        receipt_lines.append(f"  • {p['quantity']} x {p['name']:<12} | ${p['total']:>10,.2f}")
    receipt_lines.append("  " + "─" * 35)
    receipt_lines.append(f"  Subtotal:        ${total_sum:>10,.2f}")
    if promo_discount > 0:
        receipt_lines.append(f"  Promo ({applied_code}): -${promo_discount:>10,.2f}")
    receipt_lines.append(f"  FINAL TOTAL:     ${final_total:>10,.2f}")

    users[current_user]["balance"] -= final_total
    full_receipt = "\n".join(receipt_lines)
    users[current_user]["receipts"].append(full_receipt)
    save_users(users)

    print("\n" + "█" * 45 + f"\n          OFFICIAL RECEIPT\n{full_receipt}\n" + "█" * 45)


def login_flow(users):
    u_input = input("  👤 Username » ").strip().lower()
    if u_input not in users:
        print("  ❌ User not found.")
        return None

    if not verify_password_with_limit(users[u_input]["password"]):
        return None

    print(f"\n✅ Access Granted! Welcome, {u_input.upper()}.")
    return u_input


def main():
    users = load_users()
    inventory = load_inventory()

    promo_codes = {"king10": 0.1, "backend20": 0.2, "lova": 1.0}

    while True:
        print("\n" + "═" * 45)
        print("║    DATABASE-DRIVEN MARKET SYSTEM v27        ║")
        print("═" * 45)

        current_user = login_flow(users)
        if not current_user:
            continue

        result, user_cart, total_sum = shopping_flow(users, inventory, current_user)
        if result == "logout":
            continue

        checkout_flow(users, inventory, current_user, user_cart, total_sum, promo_codes)


if __name__ == "__main__":
    main()