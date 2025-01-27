import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QMainWindow, \
    QPushButton, QFrame, QLineEdit, QHBoxLayout, QStatusBar, QTableWidgetItem, QTableWidget, QHeaderView, QMessageBox
from PyQt5 import uic

from config import CURRENCY
from modules.update_order import UpdateOrder
from service.db_service import DBService
from service.log_service import LogService
from service.print_service import PrintService


class AllOrders:
    def __init__(self):
        self.orders_table_widget = None
        self.order_search_input = None
        self.order_search_btn = None
        self.datepicker = None



    def set_ui_elements(self, orders_table_widget, search_input, search_btn, datepicker):
        # Setup table headers
        self.orders_table_widget = orders_table_widget
        self.order_search_btn = search_btn
        self.order_search_input = search_input
        self.datepicker = datepicker
        self.orders_table_widget.setColumnCount(9)  # Adjust the number of columns as per your table
        self.orders_table_widget.setHorizontalHeaderLabels(["Order ID", "Table", "Name", "Mobile", "Address", "Amount", "Discount", "Status", "Created At"])
        self.order_search_btn.clicked.connect(self.searchOrders)

        self.datepicker.setDate(QDate.currentDate())
        self.datepicker.dateChanged.connect(self.filter_orders_by_date)

        # Stretch table columns
        self.orders_table_widget.horizontalHeader().setStretchLastSection(True)
        self.orders_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.loadOrdersFromDatabase()

    def loadOrdersFromDatabase(self):
        """Fetch orders from the database and populate the table widget."""
        try:
            # Fetch orders from the database
            orders = DBService.fetch_all_orders()

            # Clear existing rows and reset column count
            self.orders_table_widget.setRowCount(0)
            self.orders_table_widget.setColumnCount(11)  # Update for the new columns

            # Set column headers
            headers = ["Order ID", "Table", "Name", "Mobile", "Address", "Amount", "Discount", "Status", "Items", "Created At", "Action"]
            self.orders_table_widget.setHorizontalHeaderLabels(headers)

            for col_index in range(len(headers)):
                header_item = self.orders_table_widget.horizontalHeaderItem(col_index)
                if header_item:
                    header_item.setTextAlignment(Qt.AlignLeft)
                    font = QFont()  # Create a font object
                    font.setBold(True)  # Set the font weight to bold
                    header_item.setFont(font)

            # De-structure and populate the table
            for index, (order_id, shop_table, name, mobile, address, amount, discount, status, created_at, item_count) in enumerate(orders):
                # Insert a new row for each order
                self.orders_table_widget.insertRow(index)

                # Column 0: Order ID
                item_order_id = QTableWidgetItem(str(order_id))
                self.orders_table_widget.setItem(index, 0, item_order_id)

                # Column 1: Table
                item_shop_table = QTableWidgetItem(shop_table)
                self.orders_table_widget.setItem(index, 1, item_shop_table)

                # Column 2: Customer Name
                item_name = QTableWidgetItem(name)
                self.orders_table_widget.setItem(index, 2, item_name)

                # Column 3: Mobile
                item_mobile = QTableWidgetItem(mobile)
                self.orders_table_widget.setItem(index, 3, item_mobile)

                # Column 4: Address
                item_address = QTableWidgetItem(address)
                self.orders_table_widget.setItem(index, 4, item_address)

                # Column 5: Total Amount
                item_amount = QTableWidgetItem(f"{CURRENCY}{float(amount):.2f}")
                self.orders_table_widget.setItem(index, 5, item_amount)

                # Column 6: Discount
                item_discount = QTableWidgetItem(f"{CURRENCY}{float(discount):.2f}")
                self.orders_table_widget.setItem(index, 6, item_discount)

                # Column 7: Status
                item_status = QTableWidgetItem(status)
                self.orders_table_widget.setItem(index, 7, item_status)

                # Convert created_at (assumed to be in string format like '2024-12-08 15:30:00')
                created_datetime = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                formatted_date = created_datetime.strftime("%d-%m-%Y %I:%M %p")

                # Column 8: Items
                item_count_widget = QTableWidgetItem(str(item_count))
                self.orders_table_widget.setItem(index, 8, item_count_widget)

                # Column 8: Created At
                item_created_at = QTableWidgetItem(formatted_date)
                self.orders_table_widget.setItem(index, 9, item_created_at)

                # Column 10: Actions (Edit, View, Print, Delete - All in one column)
                action_widget = QWidget()  # Create a widget to hold the buttons
                action_layout = QHBoxLayout(action_widget)  # Use a horizontal layout to arrange buttons side by side

                # Print Button
                action_btn_print = QPushButton()
                action_btn_print.setIcon(QIcon('icon/print.png'))  # Replace with your icon path
                action_btn_print.setToolTip("Print Order")
                action_btn_print.setFixedSize(15, 15)
                action_btn_print.setStyleSheet("background: transparent; border: none;")
                action_btn_print.clicked.connect(lambda _, order_id=order_id: self.printOrder(order_id))
                # Delete Button
                action_btn_delete = QPushButton()
                action_btn_delete.setIcon(QIcon('icon/delete.png'))  # Replace with your icon path
                action_btn_delete.setToolTip("Delete Order")
                action_btn_delete.setFixedSize(15, 15)
                action_btn_delete.setStyleSheet("background: transparent; border: none;")
                action_btn_delete.clicked.connect(lambda _, order_id=order_id: self.deleteOrder(order_id))

                action_layout.addWidget(action_btn_print)
                action_layout.addWidget(action_btn_delete)

                # Set layout for the action widget
                action_widget.setLayout(action_layout)

                # Add the action widget to the table cell in the last column (index 10)
                self.orders_table_widget.setCellWidget(index, 10, action_widget)

        except Exception as e:
            print(f"Error loading orders: {e}")

    def printOrder(self, order_id):
        PrintService.generate_receipt(order_id)

    def viewOrder(self, order_id):
        print(order_id)

    def deleteOrder(self, order_id):
        try:
            reply = QMessageBox.question(
                None,
                "Delete Item",
                "Are you sure you want to delete this order?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                print(f"Deleting order with ID: {order_id}")  # Debugging log
                if DBService.delete_order(order_id):
                    self.loadOrdersFromDatabase()
                else:
                    QMessageBox.information(None, "Deleted", "Order Deleted" )
            else:
                print("Order deletion canceled.")  # If user clicks No

        except Exception as e:
            LogService.log_error(f"Error in deleteOrder method: {e}", exc=True)

    def searchOrders(self):
        """Search orders based on order_id, name, mobile, or address."""
        search_text = self.order_search_input.text().strip()  # Get the input from the search field
        if not search_text:
            self.loadOrdersFromDatabase()
            return

        try:
            # Fetch orders from DBService
            orders = DBService.search_orders(search_text)

            # Clear the table and populate with search results
            self.orders_table_widget.setRowCount(0)
            # De-structure and populate the table
            for index, (order_id, shop_table, name, mobile, address, amount, discount, status, created_at, item_count) in enumerate(
                    orders):
                # Insert a new row for each order
                self.orders_table_widget.insertRow(index)

                # Column 0: Order ID
                item_order_id = QTableWidgetItem(str(order_id))
                self.orders_table_widget.setItem(index, 0, item_order_id)

                # Column 1: Table
                item_shop_table = QTableWidgetItem(shop_table)
                self.orders_table_widget.setItem(index, 1, item_shop_table)

                # Column 2: Customer Name
                item_name = QTableWidgetItem(name)
                self.orders_table_widget.setItem(index, 2, item_name)

                # Column 3: Mobile
                item_mobile = QTableWidgetItem(mobile)
                self.orders_table_widget.setItem(index, 3, item_mobile)

                # Column 4: Address
                item_address = QTableWidgetItem(address)
                self.orders_table_widget.setItem(index, 4, item_address)

                # Column 5: Total Amount
                item_amount = QTableWidgetItem(f"{CURRENCY}{float(amount):.2f}")
                self.orders_table_widget.setItem(index, 5, item_amount)

                # Column 6: Discount
                item_discount = QTableWidgetItem(f"{CURRENCY}{float(discount):.2f}")
                self.orders_table_widget.setItem(index, 6, item_discount)

                # Column 7: Status
                item_status = QTableWidgetItem(status)
                self.orders_table_widget.setItem(index, 7, item_status)

                # Convert created_at (assumed to be in string format like '2024-12-08 15:30:00')
                created_datetime = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                formatted_date = created_datetime.strftime("%d-%m-%Y %I:%M %p")

                # Column 8: Items
                item_count_widget = QTableWidgetItem(str(item_count))
                self.orders_table_widget.setItem(index, 8, item_count_widget)

                # Column 8: Created At
                item_created_at = QTableWidgetItem(formatted_date)
                self.orders_table_widget.setItem(index, 9, item_created_at)

                # Column 10: Actions (Edit, View, Print, Delete - All in one column)
                action_widget = QWidget()  # Create a widget to hold the buttons
                action_layout = QHBoxLayout(action_widget)  # Use a horizontal layout to arrange buttons side by side

                # Print Button
                action_btn_print = QPushButton()
                action_btn_print.setIcon(QIcon('icon/print.png'))  # Replace with your icon path
                action_btn_print.setToolTip("Print Order")
                action_btn_print.setFixedSize(15, 15)
                action_btn_print.setStyleSheet("background: transparent; border: none;")
                action_btn_print.clicked.connect(lambda _, order_id=order_id: self.printOrder(order_id))
                # Delete Button
                action_btn_delete = QPushButton()
                action_btn_delete.setIcon(QIcon('icon/delete.png'))  # Replace with your icon path
                action_btn_delete.setToolTip("Delete Order")
                action_btn_delete.setFixedSize(15, 15)
                action_btn_delete.setStyleSheet("background: transparent; border: none;")
                action_btn_delete.clicked.connect(lambda _, order_id=order_id: self.deleteOrder(order_id))

                action_layout.addWidget(action_btn_print)
                action_layout.addWidget(action_btn_delete)

                # Set layout for the action widget
                action_widget.setLayout(action_layout)

                # Add the action widget to the table cell in the last column (index 10)
                self.orders_table_widget.setCellWidget(index, 10, action_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def filter_orders_by_date(self):
        selected_date = self.datepicker.date().toString("yyyy-MM-dd")

        if not selected_date:
            self.loadOrdersFromDatabase()
            return

        try:
            # Fetch orders from DBService
            orders = DBService.fetch_all_orders(selected_date)

            # Clear the table and populate with search results
            self.orders_table_widget.setRowCount(0)
            # De-structure and populate the table
            for index, (order_id, shop_table, name, mobile, address, amount, discount, status, created_at, item_count) in enumerate(orders):
                # Insert a new row for each order
                self.orders_table_widget.insertRow(index)

                # Column 0: Order ID
                item_order_id = QTableWidgetItem(str(order_id))
                self.orders_table_widget.setItem(index, 0, item_order_id)

                # Column 1: Table
                item_shop_table = QTableWidgetItem(shop_table)
                self.orders_table_widget.setItem(index, 1, item_shop_table)

                # Column 2: Customer Name
                item_name = QTableWidgetItem(name)
                self.orders_table_widget.setItem(index, 2, item_name)

                # Column 3: Mobile
                item_mobile = QTableWidgetItem(mobile)
                self.orders_table_widget.setItem(index, 3, item_mobile)

                # Column 4: Address
                item_address = QTableWidgetItem(address)
                self.orders_table_widget.setItem(index, 4, item_address)

                # Column 5: Total Amount
                item_amount = QTableWidgetItem(f"{CURRENCY}{float(amount):.2f}")
                self.orders_table_widget.setItem(index, 5, item_amount)

                # Column 6: Discount
                item_discount = QTableWidgetItem(f"{CURRENCY}{float(discount):.2f}")
                self.orders_table_widget.setItem(index, 6, item_discount)

                # Column 7: Status
                item_status = QTableWidgetItem(status)
                self.orders_table_widget.setItem(index, 7, item_status)

                # Convert created_at (assumed to be in string format like '2024-12-08 15:30:00')
                created_datetime = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                formatted_date = created_datetime.strftime("%d-%m-%Y %I:%M %p")

                # Column 8: Items
                item_count_widget = QTableWidgetItem(str(item_count))
                self.orders_table_widget.setItem(index, 8, item_count_widget)

                # Column 8: Created At
                item_created_at = QTableWidgetItem(formatted_date)
                self.orders_table_widget.setItem(index, 9, item_created_at)

                # Column 10: Actions (Edit, View, Print, Delete - All in one column)
                action_widget = QWidget()  # Create a widget to hold the buttons
                action_layout = QHBoxLayout(action_widget)  # Use a horizontal layout to arrange buttons side by side

                # Print Button
                action_btn_print = QPushButton()
                action_btn_print.setIcon(QIcon('icon/print.png'))  # Replace with your icon path
                action_btn_print.setToolTip("Print Order")
                action_btn_print.setFixedSize(15, 15)
                action_btn_print.setStyleSheet("background: transparent; border: none;")
                action_btn_print.clicked.connect(lambda _, order_id=order_id: self.printOrder(order_id))
                # Delete Button
                action_btn_delete = QPushButton()
                action_btn_delete.setIcon(QIcon('icon/delete.png'))  # Replace with your icon path
                action_btn_delete.setToolTip("Delete Order")
                action_btn_delete.setFixedSize(15, 15)
                action_btn_delete.setStyleSheet("background: transparent; border: none;")
                action_btn_delete.clicked.connect(lambda _, order_id=order_id: self.deleteOrder(order_id))

                action_layout.addWidget(action_btn_print)
                action_layout.addWidget(action_btn_delete)

                # Set layout for the action widget
                action_widget.setLayout(action_layout)

                # Add the action widget to the table cell in the last column (index 10)
                self.orders_table_widget.setCellWidget(index, 10, action_widget)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"An unexpected error occurred: {e}")






