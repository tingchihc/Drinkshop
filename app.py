from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Input, Static, Label, DataTable, Header, Footer
from textual.coordinate import Coordinate
from decimal import Decimal
from datetime import datetime
import json

class MenuItem:
    def __init__(self, name, price, category="Regular"):
        self.name = name
        self.price = Decimal(price)
        self.category = category

class DrinkShopApp(App):
    TITLE = "🥤 Drink Shop"
    SUB_TITLE = "Order your favorite drinks"
    
    CSS = """
    Screen {
        align: center middle;
        background: $surface;
    }

    #main {
        layout: grid;
        grid-size: 2 3;
        grid-rows: 1fr 2fr 1fr;
        grid-columns: 1fr 1fr;
        grid-gutter: 1;
        background: $surface-darken-1;
        border: tall $primary;
        padding: 0;
    }

    Header {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
    }

    Footer {
        background: $primary;
        color: $text;
    }

    #customer-info {
        row-span: 1;
        column-span: 2;
        height: 100%;
        border: panel $accent;
        padding: 0 1;
    }

    #customer-info-header {
        background: $accent;
        text-align: center;
        color: $text;
        text-style: bold;
        width: 100%;
        height: 1;
    }

    #menu {
        row-span: 1;
        column-span: 1;
        height: 100%;
        border: panel $success;
        padding: 0 1;
    }

    #menu-header {
        background: $success;
        text-align: center;
        color: $text;
        text-style: bold;
        width: 100%;
        height: 1;
    }

    #cart {
        row-span: 1;
        column-span: 1;
        height: 100%;
        border: panel $warning;
        padding: 0 1;
    }

    #cart-header {
        background: $warning;
        text-align: center;
        color: $text;
        text-style: bold;
        width: 100%;
        height: 1;
    }

    #checkout {
        row-span: 1;
        column-span: 2;
        height: 100%;
        border: panel $error;
        padding: 0 1;
    }

    #checkout-header {
        background: $error;
        text-align: center;
        color: $text;
        text-style: bold;
        width: 100%;
        height: 1;
    }

    .category-label {
        text-align: center;
        background: #f3f4f6;
        color: $text;
        padding: 0;
        margin-top: 1;
        text-style: bold;
        width: 100%;
    }

    Button {
        width: 100%;
        margin: 0 0 1 0;
    }

    Input {
        margin: 0;
    }

    #cart-table {
        height: 9;
        margin: 0;
    }

    #cart-total {
        dock: bottom;
        background: $warning-lighten-2;
        text-style: bold;
        color: $text;
        height: 3;
        padding: 1;
        text-align: center;
    }

    #receipt {
        background: $background;
        color: $text;
        border: solid $accent;
        height: 5;
        margin: 0;
        padding: 0 1;
        overflow-y: auto;
    }

    #menu-container {
        height: 1fr;
        overflow-y: scroll;
        padding-right: 1;
    }

    Label {
        margin: 0;
        padding: 0;
    }

    .menu-button {
        background: $primary-lighten-3;
        color: $text;
        height: auto;
        width: 100%;
        text-align: left; /* or center if you prefer */
        padding: 0 1;
        margin-bottom: 1;
        border: none;
    }

    .menu-button:hover {
        background: $accent;
    }

    .checkout-button {
        height: auto;
        width: 1fr;
        margin: 0 1;
        min-width: 20;
        color: $text;
        background: $primary-lighten-3;
    }

    #btn-complete {
        background: $success;
        color: black;
    }

    #btn-clear {
        background: $error;
        color: $text;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $primary-darken-1;
        color: $text;
    }

    #customer-info-container {
        layout: horizontal;
        height: 5;
        align: center middle;
        margin-top: 1;
    }

    #customer-name {
        width: 30;
        height: 3;
    }

    #customer-label {
        width: 15;
        height: 1;
        padding-right: 1;
        text-align: right;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear_cart", "Clear Cart"),
        ("o", "complete_order", "Complete Order"),
        ("h", "show_help", "Help")
    ]

    def __init__(self):
        super().__init__()
        # Define the drink menu - organized by categories
        self.menu_items = [
            MenuItem("Espresso", "2.75", "Coffee"),
            MenuItem("Americano", "3.00", "Coffee"),
            MenuItem("Cappuccino", "3.75", "Coffee"),
            MenuItem("Latte", "4.00", "Coffee"),
            MenuItem("Green Tea", "2.50", "Tea"),
            MenuItem("Black Tea", "2.25", "Tea"),
            MenuItem("Chai Tea", "3.00", "Tea"),
            MenuItem("Orange Juice", "2.50", "Cold Drinks"),
            MenuItem("Lemonade", "2.25", "Cold Drinks"),
            MenuItem("Iced Tea", "2.00", "Cold Drinks"),
            MenuItem("Soda", "1.75", "Cold Drinks"),
            MenuItem("Water", "1.00", "Cold Drinks"),
        ]
        # Customer cart
        self.cart = []
        # Customer name
        self.customer_name = ""
        # Status message
        self.status_message = "Welcome to Drink Shop! Select items from the menu."

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Container(id="main"):
            # Customer info section
            with Container(id="customer-info"):
                yield Label("👤 Customer Information", id="customer-info-header")
                with Horizontal(id="customer-info-container"):
                    yield Label("Customer Name:", id="customer-label")
                    yield Input(id="customer-name", placeholder="Enter name here")
            
            # Menu section
            with Container(id="menu"):
                yield Label("🍹 Drink Menu", id="menu-header")
                with ScrollableContainer(id="menu-container"):
                    # Group menu items by category
                    categories = {}
                    for item in self.menu_items:
                        if item.category not in categories:
                            categories[item.category] = []
                        categories[item.category].append(item)
                    
                    # Create menu items grouped by category
                    for category, items in categories.items():
                        yield Label(f"{category}", classes="category-label")
                        for i, item in enumerate(items):
                            item_id = self.menu_items.index(item)
                            yield Button(f"{item.name} - ${item.price}", 
                                         id=f"menu-item-{item_id}",
                                         classes="menu-button")
            
            # Cart section
            with Container(id="cart"):
                yield Label("🛒 Your Cart", id="cart-header")
                yield DataTable(id="cart-table")
                yield Static(id="cart-total", content="Total: $0.00")
            
            # Checkout section
            with Container(id="checkout"):
                yield Label("💵 Checkout", id="checkout-header")
                with Horizontal():
                    yield Button("Complete Order", id="btn-complete", variant="success", classes="checkout-button")
                    yield Button("Clear Cart", id="btn-clear", variant="error", classes="checkout-button")
                yield Static(id="receipt", content="")
                yield Static(id="status-bar", content=self.status_message)
        
        yield Footer()

    def on_mount(self):
        # Setup the cart table
        table = self.query_one("#cart-table", DataTable)
        table.add_columns("Item", "Price", "❌")
        # Update status bar
        self.update_status("Ready to take your order! Add items from the menu.")

    def update_status(self, message):
        """Update the status bar with a message"""
        self.status_message = message
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(message)

    def action_quit(self):
        """Quit the application."""
        self.exit()

    def action_clear_cart(self):
        """Clear the cart with keyboard shortcut."""
        self.clear_cart()

    def action_complete_order(self):
        """Complete order with keyboard shortcut."""
        self.complete_order()
        
    def action_show_help(self):
        """Show help message."""
        self.update_status("HELP: Press 'q' to quit, 'c' to clear cart, 'o' to complete order")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "customer-name":
            self.customer_name = event.value
            if self.customer_name:
                self.update_status(f"Hello, {self.customer_name}! Please select your drinks.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        
        # Handle menu item buttons
        if button_id.startswith("menu-item-"):
            item_idx = int(button_id.split("-")[-1])
            self.add_to_cart(item_idx)
        
        # Handle complete order button
        elif button_id == "btn-complete":
            self.complete_order()
        
        # Handle clear cart button
        elif button_id == "btn-clear":
            self.clear_cart()

    def add_to_cart(self, item_idx):
        """Add an item to the cart"""
        item = self.menu_items[item_idx]
        self.cart.append(item)
        self.update_cart_display()
        self.update_status(f"Added {item.name} to cart (${item.price})")

    def update_cart_display(self):
        """Update the cart display with current items"""
        table = self.query_one("#cart-table", DataTable)
        table.clear()
        
        for i, item in enumerate(self.cart):
            # Create remove button for each row
            table.add_row(
                item.name,
                f"${item.price}",
                "Remove",
                key=f"remove-{i}"
            )
        
        # Update total
        total = sum(item.price for item in self.cart)
        self.query_one("#cart-total", Static).update(f"Total: ${total:.2f}\n{len(self.cart)} items in cart")

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """Handle click on a table row"""
        row_key = event.row_key
        if row_key and row_key.startswith("remove-"):
            cart_idx = int(row_key.split("-")[-1])
            removed_item = self.cart[cart_idx].name
            self.remove_from_cart(cart_idx)
            self.update_status(f"Removed {removed_item} from cart")

    def remove_from_cart(self, cart_idx):
        """Remove an item from the cart"""
        if 0 <= cart_idx < len(self.cart):
            self.cart.pop(cart_idx)
            self.update_cart_display()

    def clear_cart(self):
        """Clear all items from the cart"""
        if self.cart:
            self.cart = []
            self.update_cart_display()
            self.query_one("#receipt", Static).update("")
            self.update_status("Cart cleared")
        else:
            self.update_status("Cart is already empty")

    def complete_order(self):
        """Complete the order and generate receipt"""
        if not self.cart:
            self.query_one("#receipt", Static).update("Cart is empty - Please add items")
            self.update_status("Cannot complete order - Cart is empty")
            return
            
        if not self.customer_name:
            self.query_one("#receipt", Static).update("Please enter your name first")
            self.update_status("Cannot complete order - Name required")
            return
        
        # Generate receipt
        total = sum(item.price for item in self.cart)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        receipt = f"""
        === DRINK SHOP RECEIPT ===
        Date: {timestamp}. Customer: {self.customer_name}. Data save into folder.
        """
        
        # Group items by name for compact receipt
        tmp = {
            "username": self.customer_name,
            "time": timestamp,
            "items": []
        }

        item_counts = {}
        for item in self.cart:
            if item.name in item_counts:
                item_counts[item.name][0] += 1
            else:
                item_counts[item.name] = [1, item.price]
                
        for name, (count, price) in item_counts.items():
            item_total = count * price
            tmp["items"].append({"name": name, "count": count})
            receipt += f"{count}× {name}: ${price} each = ${item_total}\n"
        
        tmp["cost"] = str(total)

        receipt += f"""
        -------------------------
        Total Items: {len(self.cart)}
        Total: ${total:.2f}
        
        Thank you for your order!
        """
        
        self.query_one("#receipt", Static).update(receipt)
        self.update_status(f"Order completed! Total: ${total:.2f}")

        with open("data\\receipt.json", 'w', encoding='utf-8') as f:
            json.dump(tmp, f, indent=4)

if __name__ == "__main__":
    app = DrinkShopApp()
    app.run()
