from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QWidget, QHBoxLayout, QPushButton, QTableWidgetItem, QHeaderView, \
QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from service.db_service import DBService

class Category:
    def __init__(self):
        self.category_name_input = None
        self.category_list_widget = None
        self.category_table_widget = None
        self.update_dialog = None
        self.category_id_to_update = None

    def set_ui_elements(self, category_name_input, category_list_widget, category_table_widget):
        self.category_name_input = category_name_input
        self.category_list_widget = category_list_widget
        self.category_table_widget = category_table_widget

    def saveCategory(self):
        category_name = self.category_name_input.text() if self.category_name_input else ""

        if category_name:
            if DBService.save_category(category_name):
                self.loadCategoryTable()
                self.loadCategoryList()
                print("Category saved:", category_name)
            else:
                print("Category already exists.")
        else:
            print("Category name is empty.")

    def loadCategoryList(self):
        categories = DBService.fetch_categories()
        self.category_list_widget.clear()
        for category in categories:
            item_text = f"{category[1]}"
            item = QListWidgetItem()
            item.setText(item_text)
            self.category_list_widget.addItem(item)

    def loadCategoryTable(self):
        categories = DBService.fetch_categories()
        self.category_table_widget.clearContents()
        self.category_table_widget.setAlternatingRowColors(True)
        self.category_table_widget.setColumnCount(3)
        self.category_table_widget.setHorizontalHeaderLabels(("#", "Name", "Action"))
        self.category_table_widget.setColumnWidth(0, 5)
        self.category_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.category_table_widget.verticalHeader().setVisible(False)
        self.category_table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.category_table_widget.setRowCount(0)

        for inx, category in enumerate(categories):
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            editBtn = QPushButton(self.category_table_widget)
            editBtn.setIcon(QIcon("icon/edit.png"))
            editBtn.setFixedWidth(30)
            deleteBtn = QPushButton(self.category_table_widget)
            deleteBtn.setIcon(QIcon("icon/delete.png"))
            deleteBtn.setFixedWidth(30)
            editBtn.clicked.connect(lambda checked, category_id=category[0]: self.showUpdateDialog(category_id))
            deleteBtn.clicked.connect(lambda checked, category_id=category[0]: self.handleDelete(category_id))
            layout.addWidget(editBtn)
            layout.addWidget(deleteBtn)
            layout.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(layout)
            self.category_table_widget.insertRow(inx)
            self.category_table_widget.setItem(inx, 0, QTableWidgetItem(str(category[0])))
            self.category_table_widget.setItem(inx, 1, QTableWidgetItem(str(category[1])))
            self.category_table_widget.setCellWidget(inx, 2, cell_widget)

    def showUpdateDialog(self, category_id):
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
        new_name = self.update_dialog.category_update_input.text()
        if new_name:
            DBService.update_category(self.category_id_to_update, new_name)
            print(f"Category ID {self.category_id_to_update} updated to {new_name}")
            self.update_dialog.accept()
            self.loadCategoryList()
            self.loadCategoryTable()
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
            self.loadCategoryTable()
