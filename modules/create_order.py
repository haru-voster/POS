import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QMainWindow, \
    QPushButton, QFrame, QLineEdit, QHBoxLayout, QStatusBar
from PyQt5 import uic

from config import CURRENCY
from modules.update_order import UpdateOrder
from service.db_service import DBService


class CreateOrder:
    def __init__(self):

        self.cart_items = []

        self.create_order_window= QMainWindow()
        uic.loadUi('ui/create_order.ui', self.create_order_window)
        self.items_browser_list_widget = self.create_order_window.findChild(QListWidget, 'itemsBrowserListWidget')
        self.cart_list_widget = self.create_order_window.findChild(QListWidget, 'cart_list_widget')

        self.cart_statusbar = self.create_order_window.findChild(QStatusBar, 'cart_statusbar')

        self.corders_category_combo = self.create_order_window.findChild(QComboBox, 'corders_category_combo')
        self.corders_category_combo.currentTextChanged.connect(self.filter_items)

        self.corders_search_input = self.create_order_window.findChild(QLineEdit, 'corders_search_input')
        self.corders_search_input.textChanged.connect(self.performSearch)

        self.create_order_btn = self.create_order_window.findChild(QPushButton, 'create_order_btn')
        self.create_order_btn.clicked.connect(self.createOrder)

        self.cart_total_label = self.create_order_window.findChild(QLabel, 'cart_total_label')
        self.cart_table_combo = self.create_order_window.findChild(QComboBox, 'cart_table_combo')

        self.customer_name_input = self.create_order_window.findChild(QLineEdit, 'customer_name_input')
        self.customer_mobile_input = self.create_order_window.findChild(QLineEdit, 'customer_mobile_input')
        self.customer_address_input = self.create_order_window.findChild(QLineEdit, 'customer_address_input')
        self.customer_discount_input = self.create_order_window.findChild(QLineEdit, 'customer_discount_input')

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, item_price TEXT, item_qty TEXT);''')
        connection.close()


    def showDialog(self):
        self.create_order_window.showMaximized()
        self.create_order_window.show()
        self.loadItemsList()
        self.load_categories_in_combo()
        self.loadCartList()
        self.load_tables_in_combo()

    def loadItemsList(self, category_filter=None, search_term=None):

        items = DBService.fetch_items(category_filter=category_filter, search_term=search_term)
        if not self.items_browser_list_widget:
            print("List widget not initialized.")
            return

        self.items_browser_list_widget.clear()  # Clear existing items

        for index, (item_id, item_name, item_category, item_price, _, mtype) in enumerate(items):
            # Create item widget for each item
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
            price_label = QLabel("{}{}".format(CURRENCY, item_price))
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

    def loadCartList(self):
        # Connect to the SQLite database
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        # Fetch all items from the cart
        cursor.execute("SELECT cart_id, item_name, item_price, item_qty FROM cart")
        items = cursor.fetchall()  # This will return a list of tuples
        connection.close()

        # Clear the cart list widget
        self.cart_list_widget.clear()

        # Iterate through the fetched items
        for index, (cart_id, item_name, item_price, item_qty) in enumerate(items):
            item_widget = QWidget()
            item_layout = QHBoxLayout()  # Using a horizontal layout

            # Item name label
            name_label = QLabel(item_name)
            name_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
            name_label.setFixedWidth(200)

            # Quantity label
            qty_label = QLabel(str(item_qty))
            qty_label.setStyleSheet("font-size: 12px; color: #333;")
            qty_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

            # Total price label
            total_price = float(item_price) * int(item_qty)
            total_label = QLabel("{}{}".format(CURRENCY, item_price))
            total_label.setStyleSheet("font-size: 12px; color: #333;")

            # "+" button to increment quantity
            increment_button = QPushButton("+")
            increment_button.setStyleSheet(
                "background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px;"
            )
            increment_button.clicked.connect(lambda checked, cart_id=cart_id: self.updateQuantity(cart_id, 1))

            # "-" button to decrement quantity
            decrement_button = QPushButton("-")
            decrement_button.setStyleSheet(
                "background-color: #FF5C5C; color: white; font-weight: bold; padding: 5px; border-radius: 5px;"
            )
            decrement_button.clicked.connect(lambda checked, cart_id=cart_id: self.updateQuantity(cart_id, -1))

            # Add widgets to layout
            item_layout.addWidget(name_label)
            item_layout.addWidget(total_label)
            item_layout.addWidget(decrement_button)
            item_layout.addWidget(qty_label)
            item_layout.addWidget(increment_button)

            # Set the layout for the item widget
            item_widget.setLayout(item_layout)

            # Add item widget to the cart list
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.cart_list_widget.addItem(list_item)
            self.cart_list_widget.setItemWidget(list_item, item_widget)
            cart_total = self.calculateCartTotal()
            self.cart_total_label.setText("{}{:.2f}".format(CURRENCY, cart_total))

    def load_categories_in_combo(self):
        categories = DBService.fetch_categories()
        self.corders_category_combo.clear()
        self.corders_category_combo.addItem('All')
        for category_id, category_name in categories:
            self.corders_category_combo.addItem(category_name, category_id)


    def filter_items(self):
        selected_category = self.corders_category_combo.currentText()
        if selected_category == "All":
            selected_category = None
        self.loadItemsList(category_filter=selected_category)

    def performSearch(self):
        search_term = self.corders_search_input.text()
        category_filter = self.corders_category_combo.currentText()
        if category_filter == 'All':
            category_filter = None

        # Load filtered items into list and table widgets
        self.loadItemsList(category_filter=category_filter, search_term=search_term)


    def addItemToOrder(self, item_name, item_price, item_qty = 1):
        DBService.add_item_to_order(item_name, item_price, item_qty)
        self.loadCartList()

    def updateQuantity(self, cart_id, change):
        DBService.update_quantity(cart_id, change)
        self.loadCartList()

    def calculateCartTotal(self):
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT SUM(item_price * item_qty) FROM cart")
        result = cursor.fetchone()
        connection.close()
        total = result[0] if result[0] is not None else 0.0
        return total

    def load_tables_in_combo(self):
        tables = DBService.fetch_tables()
        self.cart_table_combo.clear()
        self.cart_table_combo.addItem('Delivery')

        for table in tables:
            self.cart_table_combo.addItem(str(table[1]))

    def createOrder(self):
        # Corrected: Remove trailing commas
        shop_table = self.cart_table_combo.currentText()
        name = self.customer_name_input.text()
        mobile = self.customer_mobile_input.text()
        address = self.customer_address_input.text()
        discount = float(self.customer_discount_input.text() or "0")  # Convert discount to float
        DBService.create_order(shop_table, name, mobile, address, discount)

        self.cart_statusbar.setStyleSheet("color : #1FD655")
        self.cart_statusbar.showMessage("Order placed successfully", 5000)
        self.loadCartList()  # Refresh cart UI
        self.calculateCartTotal()  # Update total label






