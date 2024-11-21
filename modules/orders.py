import sqlite3
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QListWidgetItem, QWidget,  QVBoxLayout, QLabel

from service.db_service import DBService
from config import CURRENCY



from modules.update_order import UpdateOrder


class Orders:
    def __init__(self):
        # Placeholder for UI elements
        self.orders_dine_list_widget = None
        self.orders_delivery_list_widget = None
        self.update_order_window = None

    def set_ui_elements(self, orders_dine_list_widget, orders_delivery_list_widget):
        self.orders_dine_list_widget = orders_dine_list_widget
        self.orders_delivery_list_widget = orders_delivery_list_widget

    def loadordersList(self):
        self.orders_dine_list_widget.clear()
        self.orders_dine_list_widget.setSpacing(10)

        orders = DBService.fetch_all_orders()

        try:
            for index, (order_id, shop_table, name, amount, status, created_at, item_count) in enumerate(orders):
                if shop_table != 'Delivery':
                    created_datetime = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")

                    item_widget = QWidget()
                    item_layout = QVBoxLayout(item_widget)

                    item_widget.setStyleSheet("background-color: #D4F7C5; border-radius: 10px;")
                    item_widget.setFixedSize(150, 150)

                    item_layout.setContentsMargins(10, 10, 10, 10)

                    order_id_label = QLabel(f"ORDER NO")
                    order_id_label.setStyleSheet(
                        "font-size: 10px; color: #000000; letter-spacing: 1px; margin-top: 5px")
                    order_id_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

                    order_no_label = QLabel(str(order_id))
                    order_no_label.setStyleSheet("font-size: 20px; color: #000000; font-weight: bold; ")
                    order_no_label.setAlignment(Qt.AlignHCenter)
                    order_no_label.setWordWrap(True)

                    amount_label = QLabel(str(f"{CURRENCY}{float(amount):.2f} ({item_count})"))
                    amount_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
                    amount_label.setAlignment(Qt.AlignHCenter)

                    status_label = QLabel(str(status))
                    status_label.setStyleSheet("font-size: 12px; color: #666;")
                    status_label.setAlignment(Qt.AlignHCenter)

                    shop_table_label = QLabel(shop_table)
                    shop_table_label.setStyleSheet(
                        "font-size: 14px; color: #1FD655; font-weight: bold; border:1px solid #888; border-radius: 5px")
                    shop_table_label.setAlignment(Qt.AlignHCenter)

                    timer_label = QLabel()
                    timer_label.setStyleSheet("font-size: 11px; color: #F94449;")
                    timer_label.setAlignment(Qt.AlignHCenter)

                    # Start QTimer for updating every minute
                    timer = QTimer(self.orders_dine_list_widget)  # Use a valid QObject as parent
                    timer.timeout.connect(lambda lbl=timer_label, dt=created_datetime: self.update_timer(lbl, dt))
                    timer.start(60000)  # Update every 60 seconds

                    # Initialize timer immediately
                    self.update_timer(timer_label, created_datetime)

                    # Add labels to layout
                    item_layout.addWidget(order_id_label)
                    item_layout.addWidget(order_no_label)
                    item_layout.addWidget(amount_label)
                    item_layout.addWidget(status_label)
                    item_layout.addWidget(shop_table_label)
                    item_layout.addWidget(timer_label)

                    # Create QListWidgetItem and set custom widget
                    list_item = QListWidgetItem()
                    list_item.setSizeHint(item_widget.size())
                    list_item.setData(Qt.UserRole, order_id)

                    self.orders_dine_list_widget.addItem(list_item)
                    self.orders_dine_list_widget.setItemWidget(list_item, item_widget)
                    self.orders_dine_list_widget.itemDoubleClicked.connect(self.handleItemDoubleClick)

        except Exception as e:
            print(f"Error loading orders: {e}")

        except ValueError as e:
            print("Data unpacking error:", e)
            print("Orders data:", orders)

    def handleItemDoubleClick(self, list_item):
        # Retrieve order_id from list_item
        order_id = list_item.data(Qt.UserRole)
        print(order_id)
        if order_id:
            if self.update_order_window is None or not self.update_order_window.update_order_window.isVisible():
                self.update_order_window = UpdateOrder(order_id)
                self.update_order_window.showDialog()
            else:
                print("Update order window is already open.")

    def update_timer(self, timer_label, created_datetime):
        elapsed = datetime.now() - created_datetime
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes = remainder // 60

        if hours > 0:
            timer_label.setText(f"{hours}h:{minutes}m")
        else:
            timer_label.setText(f"{minutes}m")



