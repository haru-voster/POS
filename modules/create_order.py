import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QMainWindow, QPushButton, QFrame, QLineEdit, QHBoxLayout, QStatusBar
from PyQt5 import uic

from config import CURRENCY
from modules.orders import Orders
from modules.update_order import UpdateOrder
from service.db_service import DBService


class CreateOrder:
    def __init__(self):
        super(CreateOrder, self).__init__()

        self.cart_items = []
        self.create_order_dialog= QDialog()

        uic.loadUi('ui/create_order_dialog.ui', self.create_order_dialog)
        self.items_browser_list_widget = self.create_order_dialog.findChild(QListWidget, 'itemsBrowserListWidget')
        self.cart_list_widget = self.create_order_dialog.findChild(QListWidget, 'cart_list_widget')

        self.cart_statusbar = self.create_order_dialog.findChild(QStatusBar, 'cart_statusbar')

        self.corders_category_combo = self.create_order_dialog.findChild(QComboBox, 'corders_category_combo')
        self.corders_category_combo.currentTextChanged.connect(self.filter_items)

        self.corders_search_input = self.create_order_dialog.findChild(QLineEdit, 'corders_search_input')
        self.corders_search_input.textChanged.connect(self.performSearch)

        self.create_order_btn = self.create_order_dialog.findChild(QPushButton, 'create_order_btn')
        self.create_order_btn.clicked.connect(self.createOrder)

        self.cart_total_label = self.create_order_dialog.findChild(QLabel, 'cart_total_label')
        self.cart_table_combo = self.create_order_dialog.findChild(QComboBox, 'cart_table_combo')

        self.customer_name_input = self.create_order_dialog.findChild(QLineEdit, 'customer_name_input')
        self.customer_mobile_input = self.create_order_dialog.findChild(QLineEdit, 'customer_mobile_input')
        self.customer_address_input = self.create_order_dialog.findChild(QLineEdit, 'customer_address_input')

        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, item_price TEXT, item_qty TEXT);''')
        connection.close()

    def showDialog(self):
        print("Creating order dialog...")
        self.create_order_dialog.showMaximized()
        self.loadItemsList()
        self.load_categories_in_combo()
        self.loadCartList()
        self.load_tables_in_combo()
        self.calculateCartTotal()
        self.create_order_dialog.show()

    def loadItemsList(self, category_filter=None, search_term=None):
        items = DBService.fetch_items(category_filter=category_filter, search_term=search_term)
        if not self.items_browser_list_widget:
            print("List widget not initialized.")
            return

        self.items_browser_list_widget.clear()  # Clear existing items

        for index, (item_id, item_name, item_category, item_price, mtype, variation_names, variation_prices) in enumerate(items):
            # Create item widget for each item
            item_widget = QWidget()
            item_layout = QVBoxLayout()

            # Set background color based on type (Veg/Non-Veg)
            background_color = "#D4F7C5" if mtype == "Veg" else "#FFD1D1"
            item_widget.setStyleSheet(f"background-color: {background_color}; border-radius: 10px;")

            # Item name label
            text_up_label = QLabel(item_name)
            text_up_label.setStyleSheet("font-size: 12px; color: #333; font-weight: bold; margin-right: 10px; margin-bottom: 10px")
            text_up_label.setWordWrap(True)
            text_up_label.setFixedWidth(130)
            text_up_label.setFixedHeight(50)
            text_up_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            # Add variation label if variations exist, otherwise show item price
            if variation_names and variation_prices:
                variation_list = variation_names.split(",")
                price_list = variation_prices.split(",")
                variation_text = "\n".join(
                    [f"{name.strip()} - {CURRENCY}{price.strip()}" for name, price in zip(variation_list, price_list)]
                )
                variation_label = QLabel(variation_text)
                variation_label.setStyleSheet("font-size: 12px; color: #333; font-weight: bold; margin-right: 10px;")
                variation_label.setWordWrap(True)
                variation_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            else:
                variation_label = QLabel(f"{CURRENCY}{item_price}")
                variation_label.setStyleSheet("font-size: 12px; color: #333; font-weight: bold; margin-right: 10px;")
                variation_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            variation_label.setWordWrap(True)
            variation_label.setFixedWidth(130)
            variation_label.setFixedHeight(60)
            variation_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            # "Add" button
            add_button = QPushButton("Add")
            add_button.setStyleSheet("background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px; margin-top: 20px")
            add_button.clicked.connect(lambda checked, item_id=item_id : self.addItemToOrder(item_id))
            # Add widgets to layout
            item_layout.addWidget(text_up_label)
            item_layout.addWidget(variation_label)  # Add variation label here
            item_layout.addWidget(add_button)
            item_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            item_widget.setLayout(item_layout)

            # Add item to the list widget
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.items_browser_list_widget.addItem(list_item)
            self.items_browser_list_widget.setItemWidget(list_item, item_widget)

    def loadCartList(self):

        items = DBService.get_cart_items()
        # Clear the cart list widget
        self.cart_list_widget.clear()

        # Iterate through the fetched items
        for index, (cart_id, item_name, item_price, item_qty) in enumerate(items):
            item_widget = QWidget()
            item_layout = QHBoxLayout()  # Using a horizontal layout

            item_price = item_price.replace(",", "")  # Remove commas in case of formatted numbers

            try:
                item_price = float(item_price)
            except (ValueError, TypeError):
                item_price = 0.0  # Set to 0.0 or any default value if conversion fails

            # Concatenate name and price in the label
            name_label = QLabel(f"{item_name} ({CURRENCY}{item_price:.2f})")
            name_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
            name_label.setFixedWidth(400)

            # Quantity label
            qty_label = QLabel(str(item_qty))
            qty_label.setStyleSheet("font-size: 12px; color: #333;")
            qty_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

            try:
                total_price = float(item_price) * int(item_qty)  # Calculate total price
            except ValueError:
                total_price = 0.0  # Default to 0 if the price or quantity is not numeric

            # Create total label with formatted total_price to 2 decimal places
            total_label = QLabel("{}{:.2f}".format(CURRENCY, total_price))
            total_label.setStyleSheet("font-size: 12px; color: #333; font-weight: bold;")

            # "+" button to increment quantity
            increment_button = QPushButton("+")
            increment_button.setStyleSheet(
                "background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px;"
            )
            increment_button.setFixedSize(20, 20)
            increment_button.clicked.connect(lambda checked, cart_id=cart_id: self.updateQuantity(cart_id, 1))

            # "-" button to decrement quantity
            decrement_button = QPushButton("-")
            decrement_button.setStyleSheet(
                "background-color: #FF5C5C; color: white; font-weight: bold; padding: 5px; border-radius: 5px;"
            )
            decrement_button.setFixedSize(20, 20)
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

    def addItemToOrder(self, item_id):
        if DBService.getVariationCount(item_id) == 0:
            DBService.add_item_to_cart(item_id)
            self.loadCartList()
            self.calculateCartTotal()
        else:
            # Show dialog for variations
            self.cart_variation_dialog = QDialog()
            uic.loadUi('ui/cart_variation.ui', self.cart_variation_dialog)

            # Clear and populate variation list
            cart_variation_list = self.cart_variation_dialog.findChild(QListWidget, 'cart_variation_list')
            cart_variation_list.clear()

            variations = DBService.fetch_variations(item_id)
            for vid, v_name, v_price in variations:
                print(v_name)
                variation_widget = QWidget()
                variation_layout = QVBoxLayout()

                # Variation Name Label
                name_label = QLabel(v_name)
                name_label.setStyleSheet("font-size: 12px; color: #333; font-weight: bold;")
                name_label.setFixedWidth(70)
                name_label.setFixedHeight(30)
                name_label.setWordWrap(True)
                name_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

                # Variation Price Label
                price_label = QLabel(f"{CURRENCY}{v_price}")
                price_label.setStyleSheet("font-size: 12px; color: #333;")
                price_label.setAlignment(Qt.AlignCenter)

                # Add Button
                add_button = QPushButton("Add")
                add_button.setStyleSheet("background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
                add_button.clicked.connect(lambda checked, var_id=vid: self.addVariationToCart(var_id))

                # Add widgets to layout
                variation_layout.addWidget(name_label)
                variation_layout.addWidget(price_label)
                variation_layout.addWidget(add_button)
                variation_widget.setLayout(variation_layout)

                # Add variation widget to list
                list_item = QListWidgetItem()
                list_item.setSizeHint(variation_widget.sizeHint())
                cart_variation_list.addItem(list_item)
                cart_variation_list.setItemWidget(list_item, variation_widget)

            self.cart_variation_dialog.exec_()


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


    def updateQuantity(self, cart_id, change):
        DBService.update_quantity(cart_id, change)
        self.loadCartList()
        self.calculateCartTotal()

    def load_tables_in_combo(self):
        tables = DBService.fetch_tables()
        self.cart_table_combo.clear()
        self.cart_table_combo.addItem('Dine')

        for table in tables:
            self.cart_table_combo.addItem(str(table[1]))

        self.cart_table_combo.addItem('Delivery')

    def createOrder(self):
        # Corrected: Remove trailing commas
        shop_table = self.cart_table_combo.currentText()
        name = self.customer_name_input.text().upper()
        mobile = self.customer_mobile_input.text()
        address = self.customer_address_input.text().upper()
        DBService.create_order(shop_table, name, mobile, address)
        self.loadCartList()  # Refresh cart UI
        self.calculateCartTotal()  # Update total label
        self.create_order_dialog.close()


    def calculateCartTotal(self):
        cart_total = DBService.calculate_cart_total()
        self.cart_total_label.setText("{}{:.2f}".format(CURRENCY, cart_total))

    def addVariationToCart(self, variation_id):
        if DBService.add_variation_to_cart(variation_id):
            self.cart_variation_dialog.close()
            self.loadCartList()
            self.calculateCartTotal()



