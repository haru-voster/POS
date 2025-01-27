from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QHBoxLayout, QPushButton, QTableWidgetItem, QHeaderView, \
    QMessageBox, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from service.db_service import DBService

class Category:
    def __init__(self):
        self.category_name_input = None
        self.category_list_widget = None
        self.update_dialog = None
        self.category_id_to_update = None

    def set_ui_elements(self, category_name_input, category_list_widget):
        self.category_name_input = category_name_input
        self.category_list_widget = category_list_widget

    def saveCategory(self):
        category_name = self.category_name_input.text().title() if self.category_name_input else ""

        if category_name:
            if DBService.save_category(category_name):
                self.loadCategoryList()
                self.category_name_input.clear()
            else:
                print("Category already exists.")
        else:
            print("Category name is empty.")

    def loadCategoryList(self):
        """Load categories into the category list widget with Edit and Delete buttons."""
        categories = DBService.fetch_categories()
        self.category_list_widget.clear()

        for category_id, category_name in categories:
            # Create a widget to hold category text and buttons
            category_widget = QWidget()
            outer_layout = QVBoxLayout()  # Outer vertical layout

            # Category name label
            category_label = QLabel(category_name)
            category_label.setStyleSheet("font-size: 14px; color: #111; margin-right : 5px")
            category_label.setFixedWidth(100)
            category_label.setFixedHeight(50)
            category_label.setWordWrap(True)
            category_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
            outer_layout.addWidget(category_label)

            # Inner horizontal layout for buttons
            button_layout = QHBoxLayout()
            # Edit button
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("icon/edit.png"))  # Replace with path to edit icon
            edit_button.setToolTip("Edit Category")
            edit_button.setStyleSheet("background: transparent; border: none;")
            edit_button.setFixedSize(30, 30)
            edit_button.clicked.connect(lambda checked, cat_id=category_id: self.handleEdit(cat_id))

            # Delete button
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("icon/delete.png"))  # Replace with path to delete icon
            delete_button.setToolTip("Delete Category")
            delete_button.setStyleSheet("background: transparent; border: none;")
            delete_button.setFixedSize(30, 30)
            delete_button.clicked.connect(lambda checked, cat_id=category_id: self.handleDelete(cat_id))

            # Add buttons to horizontal layout
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button) # Add spacing between buttons
            button_layout.setAlignment(Qt.AlignCenter)  # Align buttons to the right

            # Add the button layout to the outer vertical layout
            outer_layout.addLayout(button_layout) # Add margins around the widget
            # Set layout to widget
            category_widget.setLayout(outer_layout)

            # Add widget to list
            list_item = QListWidgetItem()
            list_item.setSizeHint(category_widget.sizeHint())
            self.category_list_widget.addItem(list_item)
            self.category_list_widget.setItemWidget(list_item, category_widget)


    def handleEdit(self, category_id):
        self.category_id_to_update = category_id
        self.update_dialog = QDialog()
        uic.loadUi('ui/category_update.ui', self.update_dialog)
        category_name = self.getCategoryName(category_id)
        self.update_dialog.category_update_input.setText(category_name)
        self.update_dialog.category_update_btn.clicked.connect(self.updateCategory)
        self.update_dialog.exec_()

    def getCategoryName(self, category_id):
        categories = DBService.fetch_categories()
        category_name = next((category[1] for category in categories if category[0] == category_id), None)
        return category_name

    def updateCategory(self):
        new_name = self.update_dialog.category_update_input.text().title()
        if new_name:
            DBService.update_category(self.category_id_to_update, new_name)
            print(f"Category ID {self.category_id_to_update} updated to {new_name}")
            self.update_dialog.accept()
            self.loadCategoryList()
        else:
            print("New category name is empty.")

    def handleDelete(self, category_id):
        reply = QMessageBox.question(
            None,
            "Delete Category",
            f"Are you sure you want to delete category",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            DBService.delete_category(category_id)
            self.loadCategoryList()
