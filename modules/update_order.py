import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QMainWindow, \
    QPushButton, QFrame, QLineEdit, QHBoxLayout, QStatusBar, QMessageBox
from PyQt5 import uic

from config import CURRENCY
from service.db_service import DBService
from service.log_service import LogService
from service.print_service import PrintService


class UpdateOrder:
    def __init__(self):
        super(UpdateOrder, self).__init__()
        self.order_id = None
        self.cart_items = []

        self.update_order_dialog = QDialog()
        uic.loadUi('ui/update_order_dialog.ui', self.update_order_dialog)

        self.items_browser_list_widget = self.update_order_dialog.findChild(QListWidget, 'itemsBrowserListWidget')
        self.cart_list_widget = self.update_order_dialog.findChild(QListWidget, 'cart_list_widget')

        self.cart_statusbar = self.update_order_dialog.findChild(QStatusBar, 'cart_statusbar')

        self.corders_category_combo = self.update_order_dialog.findChild(QComboBox, 'corders_category_combo')
        self.corders_category_combo.currentTextChanged.connect(self.filter_items)

        self.corders_search_input = self.update_order_dialog.findChild(QLineEdit, 'corders_search_input')
        self.corders_search_input.textChanged.connect(self.performSearch)

        self.update_order_btn = self.update_order_dialog.findChild(QPushButton, 'update_order_btn')
        self.update_order_btn.clicked.connect(self.updateOrder)

        self.print_btn = self.update_order_dialog.findChild(QPushButton, 'update_print_btn')
        self.print_btn.clicked.connect(self.printOrder)

        self.cart_total_label = self.update_order_dialog.findChild(QLabel, 'cart_total_label')
        self.cart_table_combo = self.update_order_dialog.findChild(QComboBox, 'cart_table_combo')

        self.customer_name_input = self.update_order_dialog.findChild(QLineEdit, 'customer_name_input')
        self.customer_mobile_input = self.update_order_dialog.findChild(QLineEdit, 'customer_mobile_input')
        self.customer_address_input = self.update_order_dialog.findChild(QLineEdit, 'customer_address_input')
        self.customer_discount_input = self.update_order_dialog.findChild(QLineEdit, 'customer_discount_input')

        self.cart_order_status_combo = self.update_order_dialog.findChild(QComboBox, 'cart_order_status_combo')
        self.cart_order_status_combo.currentIndexChanged.connect(self.updateOrderStatus)

    def showDialog(self, order_id):
        self.order_id = order_id
        self.update_order_dialog.showMaximized()
        # Load data before showing the dialog
        self.load_categories_in_combo()
        self.load_tables_in_combo()
        self.loadOrderDetails()
        self.loadCartList()
        self.calculateOrderTotal()
        self.loadItemsList()
        self.update_order_dialog.show()



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
        items = DBService.fetch_items(category_filter=category_filter, search_term=search_term)

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
            text_up_label.setStyleSheet(
                "font-size: 12px; color: #333; font-weight: bold; margin-right: 10px; margin-bottom: 10px")
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
            add_button.clicked.connect(lambda checked, item_id=item_id: self.addItemToOrder(item_id))
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

        items = DBService.get_order_items(self.order_id)
        # Clear the cart list widget
        self.cart_list_widget.clear()

        # Iterate through the fetched items
        for index, (item_id, item_name, item_qty, item_price) in enumerate(items):
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

            # Total price label
            total_price = float(item_price) * int(item_qty)
            total_label = QLabel("{}{:.2f}".format(CURRENCY, total_price))
            total_label.setStyleSheet("font-size: 12px; color: #333; font-weight: bold;")

            # "+" button to increment quantity
            increment_button = QPushButton("+")
            increment_button.setStyleSheet(
                "background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px;"
            )
            increment_button.setFixedSize(20, 20)
            increment_button.clicked.connect(lambda checked, id=item_id: self.updateQuantity(id, 1))

            # "-" button to decrement quantity
            decrement_button = QPushButton("-")
            decrement_button.setStyleSheet(
                "background-color: #FF5C5C; color: white; font-weight: bold; padding: 5px; border-radius: 5px;"
            )
            decrement_button.setFixedSize(20, 20)
            decrement_button.clicked.connect(lambda checked, id=item_id: self.updateQuantity(id, -1))

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

    def updateQuantity(self, id, change):
        DBService.update_order_quantity(id, change)
        self.loadCartList()
        self.calculateOrderTotal()

    def addItemToOrder(self, item_id):
        if DBService.getVariationCount(item_id) == 0:
            DBService.add_item_to_order(item_id, self.order_id)
            self.loadCartList()
            self.calculateOrderTotal()
        else:
            # Show dialog for variations
            self.cart_variation_dialog = QDialog()
            uic.loadUi('ui/cart_variation.ui', self.cart_variation_dialog)

            # Clear and populate variation list
            cart_variation_list = self.cart_variation_dialog.findChild(QListWidget, 'cart_variation_list')
            cart_variation_list.clear()

            variations = DBService.fetch_variations(item_id)
            for vid, v_name, v_price in variations:
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
                add_button.setStyleSheet(
                    "background-color: #1FD655; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
                add_button.clicked.connect(lambda checked, var_id=vid: self.addVariationToOrder(var_id))

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

    def filter_items(self, category):
        self.loadItemsList(category_filter=category)

    def performSearch(self):
        search_term = self.corders_search_input.text()
        category_filter = self.corders_category_combo.currentText()
        self.loadItemsList(category_filter=category_filter, search_term=search_term)

    def updateOrder(self):
        try:
            # Ask for confirmation before proceeding with the update
            reply = QMessageBox.question(
                None, "Confirm Update", "Are you sure you want to update the order?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                order_id = self.order_id
                name = self.customer_name_input.text().upper()
                mobile = self.customer_mobile_input.text()
                address = self.customer_address_input.text().upper()
                discount = self.customer_discount_input.text()
                amount = DBService.calculate_order_total(order_id)

                # Update order details using DBService
                success = DBService.update_order(order_id, name, mobile, address, discount, amount)

                if success:
                    QMessageBox.information(None, "Success", "Order finalized successfully!")
                    self.update_order_dialog.close()
                else:
                    QMessageBox.warning(None, "Failure", "Failed to update the order. Please try again.")
            else:
                print("Order update canceled.")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"An unexpected error occurred: {e}")
            LogService.log_error(f"Error in updateOrder: {e}", exc=True)


    def load_categories_in_combo(self):
        categories = DBService.fetch_categories()
        self.corders_category_combo.clear()
        self.corders_category_combo.addItem('All')
        for index, (category_id, category_name) in enumerate(categories):
            self.corders_category_combo.addItem(category_name, category_id)

    def load_tables_in_combo(self):
        tables = DBService.fetch_tables()
        self.cart_table_combo.clear()
        self.cart_table_combo.addItem('Delivery')
        for table in tables:
            self.cart_table_combo.addItem(str(table[1]))


    def calculateOrderTotal(self):
        cart_total = DBService.calculate_order_total(self.order_id)
        self.cart_total_label.setText("{}{:.2f}".format(CURRENCY, cart_total))


    def addVariationToOrder(self, variation_id):
        if DBService.add_variation_to_order(variation_id, self.order_id):
            self.cart_variation_dialog.close()
            self.loadCartList()
            self.calculateOrderTotal()

    def updateOrderStatus(self):
        selected_status = self.cart_order_status_combo.currentText()
        DBService.update_order_status(self.order_id, selected_status)


    def printOrder(self):
        PrintService.generate_receipt(self.order_id)


