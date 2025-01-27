import sqlite3
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QHBoxLayout, QPushButton, QTableWidgetItem, QHeaderView, \
    QMessageBox, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import uic

from service.db_service import DBService

class Tables:
    def __init__(self):
        self.table_name_input = None
        self.table_list_widget = None
        self.table_table_widget = None
        self.update_dialog = None
        self.table_id_to_update = None

    def set_ui_elements(self, table_name_input, table_list_widget):
        self.table_name_input = table_name_input
        self.table_list_widget = table_list_widget

    def saveTable(self):
        table_name = self.table_name_input.text().title() if self.table_name_input else ""

        if table_name:
            if DBService.save_table(table_name):  # Using the DBService save_table method
                self.loadTableList()
                print("Table saved:", table_name)
            else:
                print("Table already exists.")
        else:
            print("Table name is empty.")

    def loadTableList(self):
        tables = DBService.fetch_tables()  # Using DBService to fetch tables
        self.table_list_widget.clear()

        for table_id, table_name in tables:
            # Create a widget to hold table icon, name, and buttons
            table_widget = QWidget()
            table_layout = QVBoxLayout()

            # Create a horizontal layout for the buttons
            button_layout = QHBoxLayout()

            # Table icon
            table_icon_label = QLabel()
            table_icon_label.setPixmap(QPixmap("icon/table.png"))
            table_icon_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
            table_icon_label.setStyleSheet("margin-right: 15px")
            table_icon_label.setMinimumWidth(100)
            table_icon_label.setMinimumHeight(40)

            # Table name label
            table_name_label = QLabel(table_name)
            table_name_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold; margin-top: 8px")
            table_name_label.setAlignment(Qt.AlignCenter)

            # Edit button
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("icon/edit.png"))  # Replace with path to edit icon
            edit_button.setToolTip("Edit Table")
            edit_button.setFixedSize(30, 30)
            edit_button.setStyleSheet("border: none; background: transparent;")
            edit_button.clicked.connect(lambda checked, tbl_id=table_id: self.handleEdit(tbl_id))

            # Delete button
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("icon/delete.png"))  # Replace with path to delete icon
            delete_button.setToolTip("Delete Table")
            delete_button.setFixedSize(30, 30)
            delete_button.setStyleSheet("border: none; background: transparent;")
            delete_button.clicked.connect(lambda checked, tbl_id=table_id: self.handleDelete(tbl_id))

            # Add spacer between buttons
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)

            # Add components to the vertical layout
            table_layout.addWidget(table_icon_label)
            table_layout.addWidget(table_name_label)
            table_layout.addLayout(button_layout)
            table_layout.setAlignment(Qt.AlignCenter)
            table_layout.setContentsMargins(5,5,5,5)

            # Set layout to widget
            table_widget.setLayout(table_layout)

            # Add widget to list
            list_item = QListWidgetItem()
            list_item.setSizeHint(table_widget.sizeHint())
            self.table_list_widget.addItem(list_item)
            self.table_list_widget.setItemWidget(list_item, table_widget)


    def handleEdit(self, table_id):
        self.table_id_to_update = table_id
        self.update_dialog = QDialog()
        uic.loadUi('ui/table_update.ui', self.update_dialog)

        table_name = DBService.get_table_name(table_id)  # Using DBService to get table name
        self.update_dialog.table_update_input.setText(table_name)

        self.update_dialog.table_update_btn.clicked.connect(self.updateTable)
        self.update_dialog.exec_()

    def updateTable(self):
        new_name = self.update_dialog.table_update_input.text().title()
        if new_name:
            if DBService.update_table(self.table_id_to_update, new_name):  # Using DBService update_table
                self.update_dialog.accept()
                self.loadTableList()
        else:
            print("New table name is empty.")

    def handleDelete(self, table_id):
        reply = QMessageBox.question(
            None,
            "Delete Table",
            "Are you sure you want to delete this table?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if DBService.delete_table(table_id):  # Using DBService delete_table
                self.loadTableList()

