import datetime
import json
import os

# שם הקובץ שבו נשמור את יתרת המשתמשים
DB_FILE = "../market_data.json"


# --- פונקציות לניהול מסד הנתונים ---
def load_users():
    """טוען משתמשים מקובץ. אם לא קיים, יוצר נתונים ראשוניים."""
    if not os.path.exists(DB_FILE):
        initial_data = {
            "lova": {"password": "lova", "balance": 50000},
            "yuval": {"password": "zona", "balance": 100},
            "l": {"password": "l", "balance": 1000},
            "admin": {"password": "1234", "balance": 10000000},
            "guest": {"password": "0000", "balance": 500}
        }
        save_users(initial_data)
        return initial_data
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    """שומר את המילון המעודכן לקובץ JSON"""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# טעינת המשתמשים
users = load_users()

# --- Promo Codes ---
promo_codes = {
    "king10": 0.1,
    "backend20": 0.2,
    "LOVA": 1.0
}

# --- Products Inventory ---
inventory = [
    {"name": "laptop", "price": 1200, "category": "electronics"},
    {"name": "mouse", "price": 50, "category": "electronics"},
    {"name": "shirt", "price": 100, "category": "fashion"},
    {"name": "headphones", "price": 300, "category": "electronics"},
    {"name": "t-shirt", "price": 80, "category": "fashion"},
    {"name": "shoes", "price": 150, "category": "fashion"},
    {"name": "pizza", "price": 20, "category": "food"},
    {"name": "pasta", "price": 25, "category": "food"},
    {"name": "monitor", "price": 400, "category": "electronics"},
    {"name": "phone", "price": 800, "category": "electronics"},
    {"name": "salad", "price": 15, "category": "food"},
    {"name": "weed", "price": 200, "category": "drugs"},
    {"name": "cocaine", "price": 500, "category": "drugs"},
    {"name": "kristina", "price": 10000, "category": "bitches"},
    {"name": "yuvalzona", "price": 999999, "category": "bitches"},
    {"name": "tzur karton", "price": 1, "category": "bitches"},
    {"name": "LSD", "price": 300, "category": "drugs"},
    {"name": "burger", "price": 10, "category": "food"},
    {"name": "jeans", "price": 120, "category": "fashion"},
    {"name": "tablet", "price": 600, "category": "electronics"},
    {"name": "chocolate", "price": 5, "category": "food"},
    {"name": "haroin", "price": 400, "category": "drugs"},
    {"name": "M4A1", "price": 1500, "category": "weapons"},
    {"name": "AK-47", "price": 1300, "category": "weapons"},
    {"name": "sniper rifle", "price": 2000, "category": "weapons"},
    {"name": "pistol", "price": 800, "category": "weapons"},
    {"name": "grenade", "price": 300, "category": "weapons"},
    {"name": "drone", "price": 2500, "category": "electronics"},
    {"name": "smartwatch", "price": 350, "category": "electronics"},
    {"name": "uliya", "price": 1000, "category": "bitches"},
    {"name": "lova", "price": 100000000000000, "category": "bitches"},
    {"name": "ice cream", "price": 7, "category": "food"},
    {"name": "cola", "price": 3, "category": "food"},
    {"name": "tesla", "price": 80000, "category": "cars"},
    {"name": "bmw", "price": 70000, "category": "cars"},
    {"name": "audi", "price": 60000, "category": "cars"},
    {"name": "mercedes", "price": 90000, "category": "cars"},
    {"name": "ferrari", "price": 250000, "category": "cars"},
    {"name": "lamborghini", "price": 300000, "category": "cars"},
    {"name": "rpg", "price": 5000, "category": "weapons"},
    {"name": "knife", "price": 150, "category": "weapons"},
    {"name": "chiken wigs", "price": 12, "category": "food"},
    {"name": "fish and chips", "price": 15, "category": "food"},
    {"name": "brain", "price": 1000000, "category": "yuval"},
    {"name": "soul", "price": 500000, "category": "yuval"},
    {"name": "body repairer", "price": 300000, "category": "yuval"},
    {"name": "big dick", "price": 10000000, "category": "yuval"},
    {"name": "remove kriz", "price": 2000000, "category": "yuval"},
    {"name": "brain cells", "price": 500000, "category": "yuval"},
    {"name": "cofe ", "price": 67, "category": "food"},
    {"name": "c4", "price": 1000, "category": "weapons"},
    {"name": "chicken", "price": 150, "category": "food"},
]

# --- Main System Loop ---
while True:
    print("\n" + "═" * 45)
    print("║       SECURE LOGIN - MARKET SYSTEM v12      ║")
    print("═" * 45)

    logged_in = False
    current_user = ""
    attempts = 3

    while attempts > 0:
        u_input = input("  👤 Username » ")
        p_input = input("  🔑 Password » ")

        if u_input in users and users[u_input]["password"] == p_input:
            current_user = u_input
            print(f"\n✅ Access Granted! Welcome, {current_user.upper()}.")
            print(f"💰 Your Current Balance: ${users[current_user]['balance']:,.2f}")
            logged_in = True
            break
        else:
            attempts -= 1
            print(f"❌ Invalid login. ({attempts} attempts left)")

    if not logged_in:
        print("\n🚫 System Locked.")
        break

    while logged_in:
        user_cart = []
        total_sum = 0
        keep_shopping = True
        categories = sorted(list(set(item["category"] for item in inventory)))

        while keep_shopping:
            print("\n" + "─" * 40)
            print(f"  MAIN MENU - USER: {current_user.upper()} | BALANCE: ${users[current_user]['balance']:,.2f}")
            for i, cat in enumerate(categories, 1):
                print(f"  [{i}] {cat.capitalize()}")

            user_input = input("\n  🛒 Select category (or 'logout') » ").lower()
            if user_input == 'logout':
                logged_in = False
                break

            cat_choice = ""
            if user_input.isdigit() and 0 < int(user_input) <= len(categories):
                cat_choice = categories[int(user_input) - 1]
            elif user_input in categories:
                cat_choice = user_input
            else:
                print("  ⚠️ Category not found!");
                continue

            while keep_shopping:
                print(f"\n" + "═" * 10 + f" {cat_choice.upper()} MENU " + "═" * 10)
                items_in_cat = [i for i in inventory if i["category"] == cat_choice]
                for i, item in enumerate(items_in_cat, 1):
                    print(f"  [{i}] {item['name']:<15} | ${item['price']:,.2f}")

                item_input = input(f"\n  📦 Select item (number/name) or 'back' » ").lower()
                if item_input == 'back': break

                found_item = None
                if item_input.isdigit():
                    idx = int(item_input) - 1
                    if 0 <= idx < len(items_in_cat): found_item = items_in_cat[idx]
                else:
                    found_item = next((i for i in items_in_cat if i["name"].lower() == item_input), None)

                if found_item:
                    try:
                        qty = int(input(f"  🔢 How many units? » "))
                        if qty > 0:
                            user_cart.append({"name": found_item["name"], "price": found_item["price"], "quantity": qty,
                                              "total": found_item["price"] * qty})
                            total_sum += found_item["price"] * qty
                            print(f"  ✨ Added.")
                    except ValueError:
                        print("  ⚠️ Enter a valid number.")

                print("\n  [1] Buy more | [2] Categories | [3] Checkout")
                step = input("  🚀 What next? » ")
                if step == '1': continue
                if step == '2': break
                if step == '3': keep_shopping = False; break

        if logged_in and user_cart:
            vip_discount = total_sum * 0.15 if total_sum > 1000000 else 0
            sub_total = total_sum - vip_discount
            promo_discount = 0
            promo_code_name = "None"

            while True:
                has_promo = input("\n  🎟️ Use promo code? (y/n) » ").lower()
                if has_promo == 'y':
                    code = input("  🔑 Enter code » ")
                    if code in promo_codes:
                        promo_discount = sub_total * promo_codes[code]
                        promo_code_name = code
                        break
                    else:
                        print("  ❌ Wrong promo code. try again.")
                elif has_promo == 'n':
                    break
                else:
                    print("  ❌ Invalid input (y/n).")

            final_total = sub_total - promo_discount
            print("\n" + "─" * 45)
            print(f"  TOTAL PRICE: ${final_total:,.2f}")
            print(f"  YOUR BALANCE: ${users[current_user]['balance']:,.2f}")

            # --- חלק אישור התשלום המתוקן ---
            if users[current_user]['balance'] >= final_total:
                while True:  # לולאה שמוודאת קלט תקין של y/n
                    confirm = input("\n  💳 Confirm Payment? (y/n) » ").lower()
                    if confirm == 'y':
                        users[current_user]['balance'] -= final_total
                        save_users(users)

                        print("\n" + "█" * 45)
                        print(f"          OFFICIAL RECEIPT - {current_user.upper()} ")
                        print(f"          DATE: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} ")
                        print("█" * 45)
                        for p in user_cart:
                            print(f"  {p['quantity']} x {p['name']:<15} | ${p['total']:>10,.2f}")
                        print("─" * 45)
                        if vip_discount > 0: print(f"  VIP DISCOUNT: {'':<15} -${vip_discount:>10,.2f}")
                        if promo_discount > 0: print(f"  PROMO ({promo_code_name}): {'':<9} -${promo_discount:>10,.2f}")
                        print(f"  FINAL TOTAL PAID: {'':<11} ${final_total:>10,.2f}")
                        print(f"  REMAINING BALANCE: {'':<10} ${users[current_user]['balance']:>10,.2f}")
                        print("█" * 45)

                        # --- חלק הפקדת כסף מתוקן ---
                        while True:
                            print("\n" + "─" * 45)
                            add_money = input("  💰 Would you like to deposit more money? (y/n) » ").lower()
                            if add_money == 'y':
                                try:
                                    amount = float(input("  💵 Enter amount to deposit » "))
                                    if amount > 0:
                                        users[current_user]['balance'] += amount
                                        save_users(users)
                                        print(
                                            f"  ✅ Deposit successful! New balance: ${users[current_user]['balance']:,.2f}")
                                        break  # יוצא מלולאת הפקדת הכסף
                                    else:
                                        print("  ⚠️ Amount must be positive.")
                                except ValueError:
                                    print("  ⚠️ Invalid number.")
                            elif add_money == 'n':
                                print("  Returning to menu...")
                                break  # יוצא מלולאת הפקדת הכסף
                            else:
                                print("  ❌ Invalid input. Please enter 'y' or 'n'.")

                        break  # יוצא מלולאת אישור התשלום (כי התשלום בוצע)

                    elif confirm == 'n':
                        print("\n❌ Transaction Cancelled by User.")
                        break  # יוצא מלולאת אישור התשלום
                    else:
                        print("  ❌ Invalid input. Please enter 'y' or 'n'.")
            else:
                print("\n🚫 TRANSACTION DECLINED: Insufficient funds!")



            user_cart = []  # איפוס הסל לסוף הקנייה