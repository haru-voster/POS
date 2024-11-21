import sqlite3
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QHBoxLayout, QPushButton, QTableWidgetItem, QHeaderView, \
    QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic

from service.db_service import DBService

class Tables:
    def __init__(self):
        self.table_name_input = None
        self.table_list_widget = None
        self.table_table_widget = None
        self.update_dialog = None
        self.table_id_to_update = None

    def set_ui_elements(self, table_name_input, table_list_widget, table_table_widget):
        self.table_name_input = table_name_input
        self.table_list_widget = table_list_widget
        self.table_table_widget = table_table_widget

    def saveTable(self):
        table_name = self.table_name_input.text() if self.table_name_input else ""

        if table_name:
            if DBService.save_table(table_name):  # Using the DBService save_table method
                self.loadTableTable()
                self.loadTableList()
                print("Table saved:", table_name)
            else:
                print("Table already exists.")
        else:
            print("Table name is empty.")

    def loadTableList(self):
        tables = DBService.fetch_tables()  # Using DBService to fetch tables
        self.table_list_widget.clear()

        for table_name in tables:
            item_text = f"{table_name[1]}"
            item = QListWidgetItem()
            icon = QIcon("icon/table.png")
            item.setIcon(icon)
            item.setText(item_text)
            self.table_list_widget.setIconSize(QSize(64, 64))
            self.table_list_widget.addItem(item)

    def loadTableTable(self):
        tables = DBService.fetch_tables()  # Using DBService to fetch tables
        self.table_table_widget.clearContents()
        self.table_table_widget.setAlternatingRowColors(True)
        self.table_table_widget.setColumnCount(3)
        self.table_table_widget.setHorizontalHeaderLabels(("#", "Name", "Action"))

        self.table_table_widget.setColumnWidth(0, 5)
        self.table_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_table_widget.verticalHeader().setVisible(False)
        self.table_table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table_table_widget.setRowCount(0)

        for inx, table in enumerate(tables):
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)

            editBtn = QPushButton(self.table_table_widget)
            editBtn.setIcon(QIcon("icon/edit.png"))
            editBtn.setFixedWidth(30)

            deleteBtn = QPushButton(self.table_table_widget)
            deleteBtn.setIcon(QIcon("icon/delete.png"))
            deleteBtn.setFixedWidth(30)

            editBtn.clicked.connect(lambda checked, table_id=table[0]: self.showUpdateDialog(table_id))
            deleteBtn.clicked.connect(lambda checked, table_id=table[0]: self.handleDelete(table_id))

            layout.addWidget(editBtn)
            layout.addWidget(deleteBtn)
            layout.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(layout)

            self.table_table_widget.insertRow(inx)
            self.table_table_widget.setItem(inx, 0, QTableWidgetItem(str(table[0])))
            self.table_table_widget.setItem(inx, 1, QTableWidgetItem(str(table[1])))
            self.table_table_widget.setCellWidget(inx, 2, cell_widget)

    def showUpdateDialog(self, table_id):
        self.table_id_to_update = table_id
        self.update_dialog = QDialog()
        uic.loadUi('ui/table_update.ui', self.update_dialog)

        table_name = DBService.get_table_name(table_id)  # Using DBService to get table name
        self.update_dialog.table_update_input.setText(table_name)

        self.update_dialog.table_update_btn.clicked.connect(self.updateTable)
        self.update_dialog.exec_()

    def updateTable(self):
        new_name = self.update_dialog.table_update_input.text()
        if new_name:
            if DBService.update_table(self.table_id_to_update, new_name):  # Using DBService update_table
                self.update_dialog.accept()
                self.loadTableList()
                self.loadTableTable()
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
                self.loadTableTable()

