from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from modules.all_orders import AllOrders
from modules.category import Category
from modules.create_order import CreateOrder
from modules.items import Items
from modules.orders import Orders
from modules.tables import Tables


class Dashboard(QMainWindow):
    def __init__(self):
        super(Dashboard, self).__init__()
     
     
        self.showMaximized()
        # Initialize Category class instance
        self.category_manager = Category()
        self.items_manager = Items()
        self.table_manager = Tables()
        self.orders_manager = Orders()
        self.create_order = CreateOrder()
        self.all_orders_manager = AllOrders()

        # Set UI elements for the Category instance
        self.category_manager.set_ui_elements(self.category_name_input, self.category_list_widget)
        self.items_manager.set_ui_elements(self.items_name_input, self.items_category_combo, self.items_price_input, self.items_mtype_combo, self.items_list_widget, self.items_page_search_input, self.items_page_search_btn, self.items_page_category_combo_filter)
        self.table_manager.set_ui_elements(self.table_name_input, self.table_list_widget)
        self.orders_manager.set_ui_elements(self.orders_dine_list_widget)
        self.all_orders_manager.set_ui_elements(self.orders_page_table_widget, self.orders_page_search_input, self.orders_page_search_btn, self.datepicker)

        # Connect add_category_btn to the saveCategory method in Category
        self.add_category_btn.clicked.connect(self.category_manager.saveCategory)
        self.add_items_btn.clicked.connect(self.items_manager.createItem)
        self.add_table_btn.clicked.connect(self.table_manager.saveTable)

        self.actionCategory.triggered.connect(self.show_category_section)
        self.actionItems.triggered.connect(self.show_items_section)
        self.actionDashboard.triggered.connect(self.show_dashboard_section)
        self.actionTables.triggered.connect(self.show_tables_section)
        self.actionCreate_Order.triggered.connect(self.show_create_order)
        self.actionOrders.triggered.connect(self.show_orders_dialog)
        self.actionToolbar.triggered.connect(self.toggleToolbar)
        self.uimanager.setCurrentIndex(0)
        self.show_dashboard_section()


    def show_dashboard_section(self):
        self.uimanager.setCurrentIndex(0)
        self.orders_manager.loadordersList()

    def show_category_section(self):
        self.uimanager.setCurrentIndex(2)
        self.category_manager.loadCategoryList()

    def show_items_section(self):
        self.uimanager.setCurrentIndex(1)
        self.items_manager.load_categories_in_combo()
        self.items_manager.loadItemsList()

    def show_tables_section(self):
        self.uimanager.setCurrentIndex(3)
        self.table_manager.loadTableList()

    def toggleToolbar(self):
        self.toolbar.setVisible(not self.toolbar.isVisible())

    def show_create_order(self):
        self.create_order.create_order_dialog.finished.connect(self.orders_manager.loadordersList)
        self.create_order.showDialog()

    def show_orders_dialog(self):
        self.uimanager.setCurrentIndex(4)
        self.all_orders_manager.loadOrdersFromDatabase()
