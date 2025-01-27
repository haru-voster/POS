from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidgetItem, \
    QMessageBox, QHBoxLayout, QTableWidget
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from service.db_service import DBService
from config import CURRENCY


class Items:
    def __init__(self):
        # Placeholder for UI elements
        self.items_name_input = None
        self.items_category_combo = None
        self.items_price_input = None
        self.items_description_input = None
        self.items_mtype_combo = None
        self.items_list_widget = None
        self.items_page_search_input = None
        self.items_page_search_btn = None
        self.items_page_category_combo_filter = None
        self.updateDialog = None
        self.item_id_to_update = None
        self.variation_dialog = None
        self.variation_table_widget = None

    def set_ui_elements(self, items_name_input, items_category_combo, items_price_input, items_mtype_combo, items_list_widget, items_page_search_input, items_page_search_btn, items_page_category_combo_filter):
        """Set UI elements so we can interact with them from this class."""
        self.items_name_input = items_name_input
        self.items_category_combo = items_category_combo
        self.items_price_input = items_price_input
        self.items_mtype_combo = items_mtype_combo
        self.items_list_widget = items_list_widget
        self.items_page_search_input = items_page_search_input
        self.items_page_search_btn = items_page_search_btn
        self.items_page_category_combo_filter = items_page_category_combo_filter

        self.items_page_category_combo_filter.currentTextChanged.connect(self.filter_items)
        self.items_page_search_btn.clicked.connect(self.performSearch)

        self.loadItemsList()

    def createItem(self):
        """Save the item to the database."""
        item_name = self.items_name_input.text().title() if self.items_name_input else ""
        category = self.items_category_combo.currentText() if self.items_category_combo else ""
        item_price = self.items_price_input.text() if self.items_price_input else ""
        mtype = self.items_mtype_combo.currentText() if self.items_mtype_combo.currentText() else "Veg"

        item_price = self.validate_price_input(item_price)

        if item_name:
            try:
                DBService.save_item(item_name, category, item_price, mtype)
                self.loadItemsList()
            except Exception as e:
                print(f"Error creating item: {e}")
        else:
            print("Item name is empty.")

    def loadItemsList(self, category_filter=None, search_term=None):
        """Load items into the list widget with optional category and search filtering."""
        self.items_list_widget.clear()
        items = DBService.fetch_items(category_filter=category_filter, search_term=search_term)

        for index, (item_id, item_name, item_category, item_price, mtype, variation_names, variation_prices) in enumerate(items):
            # Create item widget
            item_widget = QWidget()
            item_layout = QVBoxLayout()

            # Set background color
            background_color = "#D4F7C5" if mtype == "Veg" else "#FFD1D1"
            item_widget.setStyleSheet(f"background-color: {background_color}; border-radius: 10px;")

            # Set item name label
            text_up_label = QLabel(item_name)
            text_up_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
            text_up_label.setFixedWidth(130)
            text_up_label.setFixedHeight(60)
            text_up_label.setWordWrap(True)
            text_up_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            # Add variation names and prices if they exist, otherwise show item price
            if variation_names and variation_prices:
                variation_list = variation_names.split(",")
                price_list = variation_prices.split(",")
                variation_price_text = "\n".join(
                    [f"{name.strip()} - {CURRENCY}{price.strip()}" for name, price in zip(variation_list, price_list)]
                )
                variation_label = QLabel(variation_price_text)
                variation_label.setStyleSheet("font-size: 12px; color: #444; font-weight: bold; font-style: italic;")
            else:
                # If no variations exist, display the item price
                variation_label = QLabel(f"{CURRENCY}{item_price}")
                variation_label.setStyleSheet("font-size: 12px; color: #444; font-weight: bold; font-style: italic;")

            variation_label.setWordWrap(True)
            variation_label.setFixedWidth(130)
            variation_label.setFixedHeight(60)
            variation_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            # Set item category label
            text_down_label = QLabel(item_category)
            text_down_label.setStyleSheet("font-size: 12px; color: #666;")
            text_down_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            # Add labels to the layout
            item_layout.addWidget(text_up_label)
            item_layout.addWidget(variation_label)  # Show either variations or item price
            item_layout.addWidget(text_down_label)
            item_layout.setContentsMargins(10,10,10,10)

            # Create a layout for the buttons
            button_layout = QHBoxLayout()

            # Create edit button with icon
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("icon/edit.png"))  # Set path to your icon file
            edit_button.setToolTip("Edit Item")
            edit_button.setFixedSize(30, 30)
            edit_button.clicked.connect(lambda checked, item_id=item_id: self.handleEdit(item_id))

            # Create delete button with icon
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("icon/delete.png"))  # Set path to your icon file
            delete_button.setToolTip("Delete Item")
            delete_button.setFixedSize(30, 30)
            delete_button.clicked.connect(lambda checked, item_id=item_id: self.handleDelete(item_id))

            # Create view button with icon
            view_button = QPushButton()
            view_button.setIcon(QIcon("icon/add.png"))  # Set path to your icon file
            view_button.setToolTip("View Item")
            view_button.setFixedSize(30, 30)
            view_button.clicked.connect(lambda checked, item_id=item_id: self.handleVariation(item_id))

            # Add buttons to button layout
            button_layout.addWidget(view_button)
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)

            # Add button layout to item layout
            item_layout.addLayout(button_layout)
            item_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            item_widget.setLayout(item_layout)

            # Add widget to list
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())

            self.items_list_widget.addItem(list_item)
            self.items_list_widget.setItemWidget(list_item, item_widget)

    def handleVariation(self, item_id):
        if self.variation_dialog is None or not self.variation_dialog.isVisible():
            self.item_id_to_update = item_id
            self.variation_dialog = QDialog()
            uic.loadUi('ui/variation.ui', self.variation_dialog)
            self.variation_table_widget = self.variation_dialog.findChild(QTableWidget, 'variation_table_widget')
            item_details = DBService.get_item_details(item_id)
            if item_details:
                self.variation_dialog.variation_item_id.setText(str(item_id))
                self.variation_dialog.variation_item_name.setText(item_details[1])
                self.loadVariationTable(item_id)
            else:
                print(f"Item details for ID {item_id} not found.")

            self.variation_dialog.variation_add_btn.clicked.connect(self.addVariation)
            self.variation_dialog.exec_()
        else:
            print("Dialog is already open.")


    def handleEdit(self, item_id):
        self.item_id_to_update = item_id
        self.updateDialog = QDialog()
        uic.loadUi('ui/item_update.ui', self.updateDialog)  # Load the update UI
        self.variation_table_widget = QTableWidget()
        item = DBService.get_item_details(item_id)
        self.updateDialog.items_update_name_input.setText(item[1])
        self.updateDialog.items_update_price_input.setText(str(item[3]))
        self.updateDialog.items_update_mtype_combo.setCurrentText(item[4])
        self.updateDialog.item_update_btn.clicked.connect(self.updateItem)
        self.load_categories_in_item_update(item[2])
        self.updateDialog.exec_()

    def updateItem(self):
        """Update the item details in the database."""
        item_name = self.updateDialog.items_update_name_input.text().title()
        category = self.updateDialog.items_update_category_combo.currentText()
        item_price = self.updateDialog.items_update_price_input.text()
        mtype = self.updateDialog.items_update_mtype_combo.currentText()

        item_price = self.validate_price_input(item_price)

        if item_name:
            try:
                DBService.update_item(self.item_id_to_update, item_name, category, item_price, mtype)
                print(f"Item ID {self.item_id_to_update} updated.")
                self.updateDialog.accept()
                self.loadItemsList()
            except Exception as e:
                print(f"Error updating item: {e}")
        else:
            print("Item name is empty.")

    def deleteItem(self, item_id):
        try:
            DBService.delete_item(item_id)
            print(f"Item with ID {item_id} deleted.")
        except Exception as e:
            print(f"Error deleting item: {e}")

    def handleDelete(self, item_id):
        reply = QMessageBox.question(
            None,
            "Delete Item",
            "Are you sure you want to delete this item?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.deleteItem(item_id)
            self.loadItemsList()

    def load_categories_in_combo(self):
        categories = DBService.fetch_categories()
        self.items_category_combo.clear()
        self.items_page_category_combo_filter.addItem('All')

        for category_id, category_name in categories:
            self.items_category_combo.addItem(category_name, category_id)
            self.items_page_category_combo_filter.addItem(category_name, category_id)

    def load_categories_in_item_update(self, selected_category_name):
        categories = DBService.fetch_categories()
        self.updateDialog.items_update_category_combo.clear()

        for category_id, category_name in categories:
            self.updateDialog.items_update_category_combo.addItem(category_name, category_id)

        # Set the selected category
        index = self.updateDialog.items_update_category_combo.findText(selected_category_name)
        if index >= 0:
            self.updateDialog.items_update_category_combo.setCurrentIndex(index)

    def filter_items(self):
        category_filter = self.items_page_category_combo_filter.currentText()
        self.loadItemsList(category_filter)

    def performSearch(self):
        search_term = self.items_page_search_input.text()

        if not search_term.strip():  # If search term is empty or just whitespace
            self.loadItemsList()  # Load all items (without search filter)
        else:
            self.loadItemsList(search_term=search_term)


    def addVariation(self):
        item_id = self.variation_dialog.variation_item_id.text()
        variation_name = self.variation_dialog.variation_name_input.text().title()
        variation_price = self.variation_dialog.variation_price_input.text()

        variation_price = self.validate_price_input(variation_price)

        if variation_name and variation_price:
            try:
                # Call the DBService to insert the variation
                DBService.insert_variation(item_id, variation_name, variation_price)
                print(f"Variation '{variation_name}' added successfully!")
                self.loadVariationTable(item_id)
            except Exception as e:
                print(f"Error adding variation: {e}")
        else:
            print("Variation name or price is empty.")

    def loadVariationTable(self, item_id):
        """Load variations for a specific item into the variation table widget."""
        self.variation_table_widget.clearContents()
        self.variation_table_widget.setAlternatingRowColors(True)
        self.variation_table_widget.setColumnCount(3)  # Name, Price, Action
        self.variation_table_widget.setHorizontalHeaderLabels(("Size / Name", "Price", "Action"))

        self.variation_table_widget.setRowCount(0)

        # Fetch variations for the given item_id from the database
        variations = DBService.fetch_variations(item_id)

        print(variations)

        for index, (vid, v_name, v_price) in enumerate(variations):
            # Create table rows
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)

            # Create Edit Button
            editBtn = QPushButton(self.variation_table_widget)
            editBtn.setIcon(QIcon("icon/edit.png"))
            editBtn.setFixedWidth(30)

            # Create Delete Button
            deleteBtn = QPushButton(self.variation_table_widget)
            deleteBtn.setIcon(QIcon("icon/delete.png"))
            deleteBtn.setFixedWidth(30)

            # Connect actions to buttons
            editBtn.clicked.connect(lambda checked, variation_id=vid: self.showUpdateVariationDialog(vid, v_name, v_price))
            deleteBtn.clicked.connect(lambda checked, variation_id=vid: self.handleDeleteVariation(vid, item_id))

            # Add buttons to the layout
            layout.addWidget(editBtn)
            layout.addWidget(deleteBtn)
            layout.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(layout)

            # Insert row and set item data in the table
            self.variation_table_widget.insertRow(index)
            self.variation_table_widget.setItem(index, 0, QTableWidgetItem(v_name))
            self.variation_table_widget.setItem(index, 1, QTableWidgetItem(str(CURRENCY + v_price)))
            self.variation_table_widget.setCellWidget(index, 2, cell_widget)

    def showUpdateVariationDialog(self, variation_id, variation_name, variation_price):
        self.variation_update_dialog = QDialog()
        uic.loadUi('ui/variation_update.ui', self.variation_update_dialog)
        self.variation_update_dialog.variation_update_id_input.setText(str(variation_id))
        self.variation_update_dialog.variation_update_name_input.setText(str(variation_name))
        self.variation_update_dialog.variation_update_price_input.setText(str(variation_price))
        self.variation_update_dialog.variation_update_btn.clicked.connect(self.updateVariation)
        self.variation_update_dialog.exec_()

    def handleDeleteVariation(self, variation_id, item_id):
        print(item_id)
        """Delete a variation and refresh the table."""
        reply = QMessageBox.question(
            self.variation_dialog,
            "Delete Variation",
            "Are you sure you want to delete this variation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Call DBService to delete the variation from the database
            if DBService.delete_variation(variation_id):
                print(f"Variation ID {variation_id} deleted.")
                # Reload the variations to update the table
                self.loadVariationTable(item_id)

    def updateVariation(self):
        variation_id = self.variation_update_dialog.variation_update_id_input.text()
        variation_name = self.variation_update_dialog.variation_update_name_input.text().title()
        variation_price = self.variation_update_dialog.variation_update_price_input.text()

        variation_price = self.validate_price_input(variation_price)

        if not variation_id or not variation_name or not variation_price:
            print("Variation ID, name, and price must not be empty.")
            return

        try:
            if DBService.update_variation(variation_id, variation_name, variation_price):
                self.variation_update_dialog.close()
                print(f"Variation ID {variation_id} successfully updated.")
            else:
                print(f"Failed to update variation ID {variation_id}.")
        except Exception as e:
            print(f"Error while updating variation ID {variation_id}: {e}")


    def validate_price_input(self, price_text):
        if not price_text.strip():
            QMessageBox.warning(None, "Input Error", "Price cannot be empty.")
            return None
        try:
            item_price = float(price_text)
            if item_price < 0:
                QMessageBox.warning(None, "Input Error", "Price cannot be negative.")
                return None
        except ValueError:
            QMessageBox.warning(None, "Input Error", "Please enter a valid number for the price.")
            return None
        return item_price





