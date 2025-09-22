from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QWidget, QMessageBox

from service.db_service import DBService


class PrintService:

    @staticmethod
    def generate_receipt(order_id):
        try:
            # Fetch order information
            order = DBService.fetch_order_info(order_id)
            if not order:
                print(f"Error: No order found with ID {order_id}")
                return None

            # Fetch order items
            items = DBService.get_order_items(order_id)
            if not items:
                print(f"Error: No items found for order ID {order_id}")
                return None

            order_id, shop_table, name, mobile, address, amount, discount, status, created_at = order

            receipt = []
            receipt.append("******** MAMA LIAM FRIES ********")
            receipt.append("--------- RECEIPT -----------")
            receipt.append(f"Order No: {order_id}")
            receipt.append(f"Table/Delivery: {shop_table}")
            receipt.append(f"Customer: {name}")
            receipt.append(f"Date: {created_at}")
            receipt.append("-" * 30)
            total = 0
            for item_id, item_name, item_qty, item_price in items:
                line_total = int(item_qty) * float(item_price)  # Calculate line total
                total += line_total
                receipt.append(f"{item_name:20} x{item_qty}  Kshs.{line_total:.2f}")  # Format receipt line

            receipt.append("-" * 30)
            receipt.append(f"Total: Kshs.{total:.2f}")
            receipt.append("****** Hot, Fast and Friendly *****")

            receipt_text = "\n".join(receipt)
            PrintService.print_receipt(receipt_text)

        except Exception as e:
            print(f"Error generating receipt: {e}")
            return None

    @staticmethod
    def print_receipt(receipt_text):
        if not receipt_text or not receipt_text.strip():
            print("Error: Receipt text is empty.")
            return

        # Create a QPrinter object
        printer = QPrinter(QPrinter.HighResolution)

        # Open the print dialog
        dialog = QPrintDialog(printer)
        if dialog.exec_() == QPrintDialog.Accepted:
            try:
                # Create a QTextDocument and set the receipt text
                document = QTextDocument()
                document.setPlainText(receipt_text)

                # Print the document using the selected printer
                document.print_(printer)
                print("Receipt printed successfully.")
            except Exception as e:
                print(f"Error during printing: {e}")
        else:
            print("Printing canceled by the user.")
