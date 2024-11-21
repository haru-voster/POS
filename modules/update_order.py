import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QMainWindow, \
    QPushButton, QFrame, QLineEdit, QHBoxLayout, QStatusBar
from PyQt5 import uic


class UpdateOrder:
    def __init__(self, order_id):
        self.order_id = order_id
        self.cart_items = []

        self.update_order_window = QMainWindow()
        uic.loadUi('ui/update_order.ui', self.update_order_window)

        self.items_browser_list_widget = self.update_order_window.findChild(QListWidget, 'itemsBrowserListWidget')
        self.cart_list_widget = self.update_order_window.findChild(QListWidget, 'cart_list_widget')

        self.cart_statusbar = self.update_order_window.findChild(QStatusBar, 'cart_statusbar')

        self.corders_category_combo = self.update_order_window.findChild(QComboBox, 'corders_category_combo')
        self.corders_category_combo.currentTextChanged.connect(self.filter_items)

        self.corders_search_input = self.update_order_window.findChild(QLineEdit, 'corders_search_input')
        self.corders_search_input.textChanged.connect(self.performSearch)

        self.update_order_btn = self.update_order_window.findChild(QPushButton, 'update_order_btn')
        self.update_order_btn.clicked.connect(self.updateOrder)

        self.cart_total_label = self.update_order_window.findChild(QLabel, 'cart_total_label')
        self.cart_table_combo = self.update_order_window.findChild(QComboBox, 'cart_table_combo')

        self.customer_name_input = self.update_order_window.findChild(QLineEdit, 'customer_name_input')
        self.customer_mobile_input = self.update_order_window.findChild(QLineEdit, 'customer_mobile_input')
        self.customer_address_input = self.update_order_window.findChild(QLineEdit, 'customer_address_input')
        self.customer_discount_input = self.update_order_window.findChild(QLineEdit, 'customer_discount_input')

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, item_price TEXT, item_qty TEXT);''')
        connection.close()
        self.showDialog()


    def showDialog(self):
        self.update_order_window.showMaximized()
        self.update_order_window.show()
        self.load_categories_in_combo()
        self.load_tables_in_combo()
        self.loadOrderDetails()
        self.loadItemsList()
        self.loadCartList()
        self.calculateCartTotal()

    def loadOrderDetails(self):
        """Load existing order details for update."""
        if self.order_id is None:
            return

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        # Fetch order details
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (self.order_id,))
        order = cursor.fetchone()
        if order:
            order_id, shop_table, name, mobile, address, amount, discount, status, created_at = order
            self.cart_table_combo.setCurrentText(str(shop_table))
            self.customer_name_input.setText(str(name))
            self.customer_mobile_input.setText(str(mobile))
            self.customer_address_input.setText(str(address))
            self.customer_discount_input.setText(str(discount))

        connection.close()

    def loadItemsList(self, category_filter=None, search_term=None):
        items = self.fetch_items(category_filter=category_filter, search_term=search_term)

        self.items_browser_list_widget.clear()  # Clear existing items

        for index, (item_id, item_name, item_category, item_price, _, mtype) in enumerate(items):
            item_widget = QWidget()
            item_layout = QVBoxLayout()

            # Set background color based on type (Veg/Non-Veg)
            background_color = "#D4F7C5" if mtype == "Veg" else "#FFD1D1"
            item_widget.setStyleSheet(f"background-color: {background_color}; border-radius: 10px; padding: 5px 2px;")

            # Item name label
            text_up_label = QLabel(item_name)
            text_up_label.setStyleSheet("font-size: 12px; color: #333; font-weight: bold;")
            text_up_label.setWordWrap(True)
            text_up_label.setFixedWidth(100)
            text_up_label.setFixedHeight(150)
            text_up_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            # Price label
            price_label = QLabel(item_price)
            price_label.setStyleSheet("font-size: 14px; color: #333;")
            price_label.setAlignment(Qt.AlignCenter)

            # "Add" button
            add_button = QPushButton("Add")
            add_button.setStyleSheet("background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")

            add_button.clicked.connect(lambda checked, item_id=item_id, item_name=item_name, item_price=item_price: self.addItemToOrder(item_name=item_name, item_price=item_price))
            # Add widgets to layout
            item_layout.addWidget(text_up_label)
            item_layout.addWidget(price_label)
            item_layout.addWidget(add_button)
            item_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            item_widget.setLayout(item_layout)

            # Add item to the list widget
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.items_browser_list_widget.addItem(list_item)
            self.items_browser_list_widget.setItemWidget(list_item, item_widget)

    def fetch_items(self, category_filter=None, search_term=None):
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        if category_filter and search_term:
            query = "SELECT * FROM items WHERE category = ? AND item_name LIKE ?"
            params = [category_filter, f"%{search_term}%"]
        elif category_filter:
            query = "SELECT * FROM items WHERE category = ?"
            params = [category_filter]
        elif search_term:
            query = "SELECT * FROM items WHERE item_name LIKE ?"
            params = [f"%{search_term}%"]
        else:
            query = "SELECT * FROM items"
            params = []

        cursor.execute(query, params)
        items = cursor.fetchall()
        connection.close()
        return items

    def loadCartList(self):

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        # Fetch items from the cart
        cursor.execute("SELECT item_id, order_id, item_name, item_price, item_qty FROM orders_items WHERE order_id = ?", (self.order_id,))
        items = cursor.fetchall()
        connection.close()
        self.cart_list_widget.clear()

        for index, (item_id, order_id, item_name, item_price, item_qty) in enumerate(items):
            item_widget = QWidget()
            item_layout = QHBoxLayout()

            # Item name label
            name_label = QLabel(item_name)
            name_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
            name_label.setFixedWidth(200)

            # Quantity label
            qty_label = QLabel(str(item_qty))
            qty_label.setStyleSheet("font-size: 12px; color: #333;")
            qty_label.setAlignment(Qt.AlignCenter)

            # Total price label
            total_price = float(item_price) * int(item_qty)
            total_label = QLabel(f"{total_price:.2f}")
            total_label.setStyleSheet("font-size: 12px; color: #333;")

            # "+" button to increment quantity
            increment_button = QPushButton("+")
            increment_button.setStyleSheet("background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
            increment_button.clicked.connect(lambda checked, item_id=item_id: self.updateQuantity(item_id, 1))

            # "-" button to decrement quantity
            decrement_button = QPushButton("-")
            decrement_button.setStyleSheet("background-color: #FF5C5C; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
            decrement_button.clicked.connect(lambda checked, item_id=item_id: self.updateQuantity(item_id, -1))

            item_layout.addWidget(name_label)
            item_layout.addWidget(total_label)
            item_layout.addWidget(decrement_button)
            item_layout.addWidget(qty_label)
            item_layout.addWidget(increment_button)

            item_widget.setLayout(item_layout)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.cart_list_widget.addItem(list_item)
            self.cart_list_widget.setItemWidget(list_item, item_widget)
            self.calculateCartTotal()

    def updateQuantity(self, item_id, change):

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT item_qty FROM orders_items WHERE item_id = ?", (item_id,))
        result = cursor.fetchone()

        if result:
            current_qty = int(result[0])
            new_qty = current_qty + change

            if new_qty > 0:
                cursor.execute("UPDATE orders_items SET item_qty = ? WHERE item_id = ?", (new_qty, item_id))
                connection.commit()
                self.cart_statusbar.setStyleSheet("color : #1FD655")
                self.cart_statusbar.showMessage("Qty Updated", 5000)
            else:
                cursor.execute("DELETE FROM orders_items WHERE item_id = ?", (item_id,))
                connection.commit()
                self.cart_statusbar.setStyleSheet("color : #F94449")
                self.cart_statusbar.showMessage("Item Deleted", 5000)

            amount = self.calculateCartTotal()
            cursor.execute("UPDATE orders SET amount  = ? WHERE order_id = ?", (amount, self.order_id))
            connection.commit()

        connection.close()
        self.loadCartList()


    def addItemToOrder(self, item_name, item_price, item_qty = 1):

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO orders_items (order_id, item_name, item_price, item_qty) VALUES (?, ?, ?, ?)", (self.order_id, item_name, item_price, item_qty))
            connection.commit()
            self.cart_statusbar.setStyleSheet("color : #1FD655")
            self.cart_statusbar.showMessage("Item Added to Cart", 5000)
        except sqlite3.IntegrityError:
            print("Error")
        finally:
            connection.close()

        self.loadCartList()

    def filter_items(self, category):
        self.loadItemsList(category_filter=category)

    def performSearch(self):
        search_term = self.corders_search_input.text()
        category_filter = self.corders_category_combo.currentText()
        self.loadItemsList(category_filter=category_filter, search_term=search_term)

    def updateOrder(self):
        order_id = self.order_id
        name = self.customer_name_input.text()
        mobile = self.customer_mobile_input.text()
        address = self.customer_address_input.text()
        discount = self.customer_discount_input.text()
        amount = self.calculateCartTotal()

        # Save order updates to the database
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        cursor.execute('''UPDATE orders SET name = ?, mobile = ?, address = ?, discount = ?, amount = ? WHERE order_id = ?''',(name, mobile, address, discount, amount, order_id))
        connection.commit()

        connection.close()
        self.cart_statusbar.setStyleSheet("color : #1FD655")
        self.cart_statusbar.showMessage("Order Information Updated", 5000)
        # Generate and print receipt
        receipt_text = self.generate_receipt(order_id)
        self.print_receipt(receipt_text)


    def fetch_all_categories(self):
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()
        connection.close()
        return categories

    def load_categories_in_combo(self):
        categories = self.fetch_all_categories()
        self.corders_category_combo.clear()
        self.corders_category_combo.addItem('All')
        for index, (category_id, category_name) in enumerate(categories):
            self.corders_category_combo.addItem(category_name, category_id)

    def load_tables_in_combo(self):
        tables = self.fetch_all_tables()
        self.cart_table_combo.clear()
        self.cart_table_combo.addItem('Delivery')

        for table in tables:
            self.cart_table_combo.addItem(str(table[1]))

    def fetch_all_tables(self):
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM shop_tables")
        shop_tables = cursor.fetchall()
        connection.close()
        return shop_tables

    def calculateCartTotal(self):
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT SUM(item_price * item_qty) FROM orders_items WHERE order_id = ?", (self.order_id,))
        result = cursor.fetchone()
        connection.close()
        total = result[0] if result[0] is not None else 0.0
        self.cart_total_label.setText(str(f"{total:.2f}"))
        return total

    def generate_receipt(self, order_id):

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT order_id, shop_table, name, status, created_at, amount FROM orders WHERE order_id = ?",(order_id,))
        order = cursor.fetchone()
        if not order:
            connection.close()
            return "Order not found."

        # Fetch the order items
        cursor.execute("SELECT item_name, item_qty, item_price FROM orders_items WHERE order_id = ?", (order_id,))
        items = cursor.fetchall()

        connection.close()

        # Build the receipt
        receipt = []
        receipt.append("********** RECEIPT **********")
        receipt.append(f"Order No: {order[0]}")  # order_id
        receipt.append(f"Table/Delivery: {order[1]}")  # shop_table
        receipt.append(f"Customer: {order[2]}")  # name
        receipt.append(f"Status: {order[3]}")  # status
        receipt.append(f"Date: {order[4]}")  # created_at
        receipt.append("\nItems:")
        receipt.append("-" * 30)

        total = 0

        for item in items:
            item_name = str(item[0])  # item_name (string)
            quantity = int(item[1])  # item_qty (ensure integer)
            price = float(item[2])  # item_price (ensure float)

            line_total = quantity * price  # Calculate line total
            total += line_total  # Add to total amount
            receipt.append(f"{item_name:20} x{quantity}  ₹{line_total:.2f}")  # Format receipt line

        receipt.append("-" * 30)
        receipt.append(f"Total: ₹{float(order[5]):.2f}")  # Ensure the amount is cast to float
        receipt.append("******************************")
        return "\n".join(receipt)

    def print_receipt(self, receipt_text):
        print(receipt_text)
        if not receipt_text.strip():
            print("Error: Receipt text is empty.")
            return

        # Create a QPrinter object
        printer = QPrinter(QPrinter.HighResolution)

        # Check if self is a valid QWidget; if not, use None
        parent = self if isinstance(self, QWidget) else None

        # Open the print dialog
        dialog = QPrintDialog(printer, parent)
        if dialog.exec_() == QPrintDialog.Accepted:
            try:
                # Create a QTextDocument and set the receipt text
                document = QTextDocument()
                document.setPlainText(receipt_text)

                # Print the document using the selected printer
                document.print_(printer)
                print("Receipt printed successfully.")
            except Exception as e:
                print(f"Error during printing: {e}")
        else:
            print("Printing canceled by the user.")


