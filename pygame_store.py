import pygame
import pygame_gui
import json
import os
import tempfile
import datetime
from pathlib import Path

# Paths to data
DB_FILE = Path("market_data.json")
INVENTORY_FILE = Path("inventory_data.json")
THEME_FILE = Path("theme.json")

# Data Manager
class DataManager:
    @staticmethod
    def read_json(path: Path, default):
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def write_json_atomic(path: Path, data):
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

    @staticmethod
    def load_users():
        return DataManager.read_json(DB_FILE, default={})

    @staticmethod
    def save_users(data):
        DataManager.write_json_atomic(DB_FILE, data)

    @staticmethod
    def load_inventory():
        return DataManager.read_json(INVENTORY_FILE, default=[])

    @staticmethod
    def save_inventory(data):
        DataManager.write_json_atomic(INVENTORY_FILE, data)


class PygameStoreApp:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 700
        self.window_surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Neon Store System v1.0")
        
        # UI Manager
        self.manager = pygame_gui.UIManager((self.width, self.height), str(THEME_FILE) if THEME_FILE.exists() else None)
        
        # App Data
        self.users = DataManager.load_users()
        self.inventory = DataManager.load_inventory()
        self.current_user = None
        self.cart = [] # List of dicts {name, price, quantity, total}
        self.promo_codes = {"king10": 0.1, "backend20": 0.2, "lova": 1.0}
        
        # State
        self.current_screen = "login"
        self.ui_elements = [] # Store all active UI elements to clear them on screen change
        
        # Background
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill(self.manager.get_theme().get_colour("dark_bg"))
        
        self.build_login_screen()

    def clear_screen(self):
        for element in self.ui_elements:
            element.kill()
        self.ui_elements.clear()

    # --- SCREENS ---

    def build_login_screen(self):
        self.clear_screen()
        self.current_screen = "login"
        
        panel_rect = pygame.Rect(0, 0, 400, 300)
        panel_rect.center = (self.width // 2, self.height // 2)
        panel = pygame_gui.elements.UIPanel(relative_rect=panel_rect, manager=self.manager)
        self.ui_elements.append(panel)
        
        title = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(50, 20, 300, 40),
                                            text="SECURE LOGIN", manager=self.manager, container=panel,
                                            object_id=pygame_gui.core.ObjectID(class_id='@title_label', object_id='#title'))
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(50, 80, 100, 30),
                                    text="Username:", manager=self.manager, container=panel)
        self.username_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(150, 80, 200, 30),
                                                                  manager=self.manager, container=panel)
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(50, 130, 100, 30),
                                    text="Password:", manager=self.manager, container=panel)
        self.password_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(150, 130, 200, 30),
                                                                  manager=self.manager, container=panel)
        self.password_input.set_text_hidden(True)
        
        self.login_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(150, 190, 100, 40),
                                                      text="LOGIN", manager=self.manager, container=panel)
        
        self.login_error_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(50, 240, 300, 30),
                                                             text="", manager=self.manager, container=panel)

    def build_main_menu(self):
        self.clear_screen()
        self.current_screen = "main_menu"
        
        # Header
        balance = self.users[self.current_user]["balance"]
        header_text = f"USER: {self.current_user.upper()} | BALANCE: ${balance:,.2f}"
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 20, 600, 40), text=header_text, 
                                    manager=self.manager, object_id=pygame_gui.core.ObjectID(class_id='@title_label', object_id='#title'))
        self.ui_elements.append(self.manager.get_sprite_group().sprites()[-1]) # Not the cleanest but gets the UILabel

        self.cart_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 150, 20, 130, 40),
                                                     text=f"CART ({len(self.cart)})", manager=self.manager)
        self.ui_elements.append(self.cart_btn)
        
        self.logout_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 290, 20, 130, 40),
                                                       text="LOGOUT", manager=self.manager)
        self.ui_elements.append(self.logout_btn)
        
        self.history_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(20, 70, 150, 40),
                                                        text="RECEIPT HISTORY", manager=self.manager)
        self.ui_elements.append(self.history_btn)
        
        if self.current_user == "admin":
            self.admin_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 70, 150, 40),
                                                          text="ADMIN DASHBOARD", manager=self.manager)
            self.ui_elements.append(self.admin_btn)

        # Categories
        categories = sorted(list(set(item.get("category", "Uncategorized") for item in self.inventory)))
        
        scroll_panel = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect(20, 130, self.width - 40, self.height - 150),
                                                                manager=self.manager)
        self.ui_elements.append(scroll_panel)
        
        y_offset = 10
        self.category_buttons = {}
        for cat in categories:
            btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(10, y_offset, 300, 50),
                                               text=cat.upper(), manager=self.manager, container=scroll_panel)
            self.category_buttons[btn] = cat
            y_offset += 60
            
    def build_category_view(self, category):
        self.clear_screen()
        self.current_screen = "category_view"
        self.current_category = category
        
        # Header
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 20, 600, 40), text=f"CATEGORY: {category.upper()}", 
                                    manager=self.manager, object_id=pygame_gui.core.ObjectID(class_id='@title_label', object_id='#title'))
        self.ui_elements.append(self.manager.get_sprite_group().sprites()[-1])

        self.back_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 290, 20, 130, 40),
                                                     text="BACK", manager=self.manager)
        self.ui_elements.append(self.back_btn)
        
        self.cart_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 150, 20, 130, 40),
                                                     text=f"CART ({len(self.cart)})", manager=self.manager)
        self.ui_elements.append(self.cart_btn)

        # Items
        items = [i for i in self.inventory if i.get("category") == category]
        
        scroll_panel = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect(20, 80, self.width - 40, self.height - 100),
                                                                manager=self.manager)
        self.ui_elements.append(scroll_panel)
        
        y_offset = 10
        self.add_item_buttons = {}
        for item in items:
            name = item["name"]
            price = item["price"]
            stock = item.get("stock", 0)
            
            panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(10, y_offset, self.width - 80, 60),
                                                manager=self.manager, container=scroll_panel)
            
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 10, 200, 40), text=name.capitalize(),
                                        manager=self.manager, container=panel)
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(220, 10, 150, 40), text=f"Price: ${price:,.2f}",
                                        manager=self.manager, container=panel)
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(380, 10, 150, 40), text=f"Stock: {stock}",
                                        manager=self.manager, container=panel)
            
            if stock > 0:
                add_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 230, 10, 120, 40),
                                                       text="ADD TO CART", manager=self.manager, container=panel)
                self.add_item_buttons[add_btn] = item
            else:
                pygame_gui.elements.UILabel(relative_rect=pygame.Rect(self.width - 230, 10, 120, 40), text="OUT OF STOCK",
                                            manager=self.manager, container=panel)
            
            y_offset += 70

    def build_cart_screen(self):
        self.clear_screen()
        self.current_screen = "cart"
        
        # Header
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 20, 300, 40), text="YOUR CART", 
                                    manager=self.manager, object_id=pygame_gui.core.ObjectID(class_id='@title_label', object_id='#title'))
        self.ui_elements.append(self.manager.get_sprite_group().sprites()[-1])
        
        self.back_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 150, 20, 130, 40),
                                                     text="BACK TO STORE", manager=self.manager)
        self.ui_elements.append(self.back_btn)

        # Cart Items
        scroll_panel = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect(20, 80, 600, self.height - 100),
                                                                manager=self.manager)
        self.ui_elements.append(scroll_panel)
        
        y_offset = 10
        total_sum = 0
        self.remove_item_buttons = {}
        
        for idx, item in enumerate(self.cart):
            panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(10, y_offset, 550, 60),
                                                manager=self.manager, container=scroll_panel)
            
            text = f"{item['quantity']}x {item['name'].capitalize()} - ${item['total']:,.2f}"
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 10, 380, 40), text=text,
                                        manager=self.manager, container=panel)
            
            rem_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(400, 10, 100, 40),
                                                   text="REMOVE", manager=self.manager, container=panel)
            self.remove_item_buttons[rem_btn] = idx
            
            total_sum += item["total"]
            y_offset += 70
            
        self.cart_total = total_sum

        # Checkout Panel
        checkout_panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(640, 80, 340, 400),
                                                     manager=self.manager)
        self.ui_elements.append(checkout_panel)
        
        balance = self.users[self.current_user]["balance"]
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 20, 300, 30), text=f"Subtotal: ${total_sum:,.2f}",
                                    manager=self.manager, container=checkout_panel)
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 60, 300, 30), text=f"Balance: ${balance:,.2f}",
                                    manager=self.manager, container=checkout_panel)
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 110, 300, 30), text="Promo Code:",
                                    manager=self.manager, container=checkout_panel)
        self.promo_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(20, 140, 200, 30),
                                                               manager=self.manager, container=checkout_panel)
        self.apply_promo_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(230, 140, 90, 30),
                                                            text="APPLY", manager=self.manager, container=checkout_panel)
        
        self.discount_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 180, 300, 30), text="Discount: $0.00",
                                                          manager=self.manager, container=checkout_panel)
        self.final_total_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 220, 300, 30), text=f"Final Total: ${total_sum:,.2f}",
                                                             manager=self.manager, container=checkout_panel)
        
        self.checkout_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(70, 280, 200, 50),
                                                         text="CONFIRM PAYMENT", manager=self.manager, container=checkout_panel)
        self.checkout_status_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 340, 300, 30), text="",
                                                                 manager=self.manager, container=checkout_panel)
        
        self.applied_discount = 0.0
        self.applied_code = "None"

    def apply_promo(self):
        code = self.promo_input.get_text().strip().lower()
        if code in self.promo_codes:
            self.applied_discount = self.cart_total * self.promo_codes[code]
            self.applied_code = code
            self.discount_label.set_text(f"Discount: -${self.applied_discount:,.2f}")
            self.final_total_label.set_text(f"Final Total: ${(self.cart_total - self.applied_discount):,.2f}")
            self.checkout_status_label.set_text("Promo applied!")
        else:
            self.checkout_status_label.set_text("Invalid promo code.")

    def do_checkout(self):
        if not self.cart:
            self.checkout_status_label.set_text("Cart is empty.")
            return
            
        final_total = self.cart_total - self.applied_discount
        balance = self.users[self.current_user]["balance"]
        
        if balance < final_total:
            self.checkout_status_label.set_text("Insufficient funds!")
            return
            
        # Deduct balance
        self.users[self.current_user]["balance"] -= final_total
        
        # Deduct stock and build receipt
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        receipt_lines = [f"  DATE: {timestamp}", "  " + "-" * 35]
        
        inv_by_name = {i.get("name"): i for i in self.inventory}
        for cart_item in self.cart:
            inv_item = inv_by_name.get(cart_item["name"])
            if inv_item:
                inv_item["stock"] -= cart_item["quantity"]
            receipt_lines.append(f"  • {cart_item['quantity']} x {cart_item['name']:<12} | ${cart_item['total']:,.2f}")
            
        receipt_lines.append("  " + "-" * 35)
        receipt_lines.append(f"  Subtotal:        ${self.cart_total:,.2f}")
        if self.applied_discount > 0:
            receipt_lines.append(f"  Promo ({self.applied_code}): -${self.applied_discount:,.2f}")
        receipt_lines.append(f"  FINAL TOTAL:     ${final_total:,.2f}")
        
        full_receipt = "\n".join(receipt_lines)
        
        if "receipts" not in self.users[self.current_user]:
            self.users[self.current_user]["receipts"] = []
            
        self.users[self.current_user]["receipts"].append(full_receipt)
        
        # Save to DB
        DataManager.save_users(self.users)
        DataManager.save_inventory(self.inventory)
        
        # Clear cart
        self.cart = []
        self.build_cart_screen()
        self.checkout_status_label.set_text("Payment Successful!")

    def build_history_screen(self):
        self.clear_screen()
        self.current_screen = "history"
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 20, 400, 40), text="RECEIPT HISTORY", 
                                    manager=self.manager, object_id=pygame_gui.core.ObjectID(class_id='@title_label', object_id='#title'))
        self.ui_elements.append(self.manager.get_sprite_group().sprites()[-1])
        
        self.back_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 150, 20, 130, 40),
                                                     text="BACK", manager=self.manager)
        self.ui_elements.append(self.back_btn)
        
        receipts = self.users[self.current_user].get("receipts", [])
        
        scroll_panel = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect(20, 80, self.width - 40, self.height - 100),
                                                                manager=self.manager)
        self.ui_elements.append(scroll_panel)
        
        y_offset = 10
        if not receipts:
            pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, y_offset, 400, 40), text="No receipts found.",
                                        manager=self.manager, container=scroll_panel)
        else:
            for i, r in enumerate(reversed(receipts)):
                lines = r.split('\n')
                panel_height = len(lines) * 20 + 20
                panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(10, y_offset, self.width - 80, panel_height),
                                                    manager=self.manager, container=scroll_panel)
                
                for j, line in enumerate(lines):
                    pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 10 + j*20, self.width - 100, 20), text=line,
                                                manager=self.manager, container=panel)
                
                y_offset += panel_height + 10

    def build_admin_screen(self):
        self.clear_screen()
        self.current_screen = "admin"
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(20, 20, 400, 40), text="ADMIN DASHBOARD", 
                                    manager=self.manager, object_id=pygame_gui.core.ObjectID(class_id='@title_label', object_id='#title'))
        self.ui_elements.append(self.manager.get_sprite_group().sprites()[-1])
        
        self.back_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.width - 150, 20, 130, 40),
                                                     text="BACK", manager=self.manager)
        self.ui_elements.append(self.back_btn)

        # Add Funds Panel
        funds_panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(20, 80, 450, 250), manager=self.manager)
        self.ui_elements.append(funds_panel)
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 10, 200, 30), text="ADD FUNDS TO USER", manager=self.manager, container=funds_panel)
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 60, 100, 30), text="Username:", manager=self.manager, container=funds_panel)
        self.admin_user_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(120, 60, 200, 30), manager=self.manager, container=funds_panel)
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 110, 100, 30), text="Amount:", manager=self.manager, container=funds_panel)
        self.admin_amount_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(120, 110, 200, 30), manager=self.manager, container=funds_panel)
        
        self.admin_add_funds_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(120, 160, 150, 40), text="ADD FUNDS", manager=self.manager, container=funds_panel)
        self.admin_funds_status = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 210, 400, 30), text="", manager=self.manager, container=funds_panel)

    def admin_add_funds(self):
        target_user = self.admin_user_input.get_text().strip().lower()
        amount_text = self.admin_amount_input.get_text().strip()
        
        if target_user not in self.users:
            self.admin_funds_status.set_text("Error: User not found.")
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.admin_funds_status.set_text("Error: Invalid amount.")
            return
            
        self.users[target_user]["balance"] += amount
        DataManager.save_users(self.users)
        self.admin_funds_status.set_text(f"Success! Added ${amount:,.2f} to {target_user}.")

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if self.current_screen == "login":
                    if event.ui_element == self.login_btn:
                        username = self.username_input.get_text().strip().lower()
                        password = self.password_input.get_text().strip()
                        
                        if username in self.users and self.users[username]["password"] == password:
                            self.current_user = username
                            self.build_main_menu()
                        else:
                            self.login_error_label.set_text("Invalid username or password.")
                            
                elif self.current_screen == "main_menu":
                    if event.ui_element == self.logout_btn:
                        self.current_user = None
                        self.cart = []
                        self.build_login_screen()
                    elif event.ui_element == self.cart_btn:
                        self.build_cart_screen()
                    elif event.ui_element == self.history_btn:
                        self.build_history_screen()
                    elif hasattr(self, 'admin_btn') and event.ui_element == self.admin_btn:
                        self.build_admin_screen()
                    elif event.ui_element in self.category_buttons:
                        self.build_category_view(self.category_buttons[event.ui_element])
                        
                elif self.current_screen == "category_view":
                    if event.ui_element == self.back_btn:
                        self.build_main_menu()
                    elif event.ui_element == self.cart_btn:
                        self.build_cart_screen()
                    elif event.ui_element in self.add_item_buttons:
                        item = self.add_item_buttons[event.ui_element]
                        # Find if already in cart
                        found = False
                        for c_item in self.cart:
                            if c_item["name"] == item["name"]:
                                if c_item["quantity"] < item.get("stock", 0):
                                    c_item["quantity"] += 1
                                    c_item["total"] = c_item["quantity"] * c_item["price"]
                                found = True
                                break
                        if not found and item.get("stock", 0) > 0:
                            self.cart.append({
                                "name": item["name"],
                                "price": item["price"],
                                "quantity": 1,
                                "total": item["price"]
                            })
                        # Rebuild screen to update cart button count
                        self.build_category_view(self.current_category)
                        
                elif self.current_screen == "cart":
                    if event.ui_element == self.back_btn:
                        self.build_main_menu()
                    elif event.ui_element == self.apply_promo_btn:
                        self.apply_promo()
                    elif event.ui_element == self.checkout_btn:
                        self.do_checkout()
                    elif event.ui_element in self.remove_item_buttons:
                        idx = self.remove_item_buttons[event.ui_element]
                        if 0 <= idx < len(self.cart):
                            self.cart.pop(idx)
                            self.build_cart_screen()

                elif self.current_screen == "history":
                    if event.ui_element == self.back_btn:
                        self.build_main_menu()

                elif self.current_screen == "admin":
                    if event.ui_element == self.back_btn:
                        self.build_main_menu()
                    elif event.ui_element == self.admin_add_funds_btn:
                        self.admin_add_funds()

            self.manager.process_events(event)
            
        return True

    def run(self):
        clock = pygame.time.Clock()
        is_running = True
        
        while is_running:
            time_delta = clock.tick(60)/1000.0
            
            is_running = self.process_events()
            
            self.manager.update(time_delta)
            
            self.window_surface.blit(self.background, (0, 0))
            self.manager.draw_ui(self.window_surface)
            
            pygame.display.update()

if __name__ == "__main__":
    app = PygameStoreApp()
    app.run()