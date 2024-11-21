import sqlite3
from datetime import datetime

from config import DB_PATH
from service.log_service import LogService


class DBService:
    @staticmethod
    def get_connection():
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def fetch_all_orders():
        query = "SELECT o.order_id, o.shop_table, o.name, o.amount, o.status, o.created_at, (SELECT COUNT(*) FROM orders_items WHERE orders_items.order_id = o.order_id) AS item_count FROM orders o"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                orders = cursor.fetchall()
                LogService.log_info(f"Fetched {len(orders)} orders successfully.")
                return orders
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching all orders: {e}", exc=True)
            return []
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching all orders: {e}", exc=True)
            return []


    @staticmethod
    def fetch_categories():
        query = "SELECT * FROM category"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                categories = cursor.fetchall()
                LogService.log_info(f"Fetched {len(categories)} categories successfully.")
                return categories
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching categories: {e}", exc=True)
            return []
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching categories: {e}", exc=True)
            return []

    @staticmethod
    def save_category(category_name):
        query = "INSERT INTO category (category_name) VALUES (?)"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (category_name,))
                conn.commit()
                LogService.log_info(f"Category '{category_name}' saved successfully.")
                return True
        except sqlite3.IntegrityError:
            LogService.log_error(f"Category '{category_name}' already exists.", exc=True)
            return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while saving category: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while saving category: {e}", exc=True)
            return False

    @staticmethod
    def update_category(category_id, new_name):
        query = "UPDATE category SET category_name = ? WHERE category_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (new_name, category_id))
                conn.commit()
                LogService.log_info(f"Category ID {category_id} updated to '{new_name}' successfully.")
                return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while updating category {category_id}: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while updating category {category_id}: {e}", exc=True)
            return False

    @staticmethod
    def delete_category(category_id):
        query = "DELETE FROM category WHERE category_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (category_id,))
                conn.commit()
                LogService.log_info(f"Category with ID {category_id} deleted successfully.")
                return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while deleting category {category_id}: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while deleting category {category_id}: {e}", exc=True)
            return False



    ##SHOP TABLE



    @staticmethod
    def save_table(table_name):
        """Save the table to the database."""
        query = "INSERT INTO shop_tables (table_name) VALUES (?)"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (table_name,))
                conn.commit()
            LogService.log_info(f"Table '{table_name}' saved successfully.")
            return True
        except sqlite3.IntegrityError:
            LogService.log_error(f"Table '{table_name}' already exists.", exc=True)
            return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while saving table: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while saving table: {e}", exc=True)
            return False

    @staticmethod
    def fetch_tables():
        """Fetch all tables from the database."""
        query = "SELECT * FROM shop_tables"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                tables = cursor.fetchall()
            LogService.log_info(f"Fetched {len(tables)} tables successfully.")
            return tables
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching tables: {e}", exc=True)
            return []
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching tables: {e}", exc=True)
            return []

    @staticmethod
    def get_table_name(table_id):
        """Fetch the table name by its ID."""
        query = "SELECT table_name FROM shop_tables WHERE table_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (table_id,))
                table_name = cursor.fetchone()
            if table_name:
                return table_name[0]
            return None
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching table name: {e}", exc=True)
            return None
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching table name: {e}", exc=True)
            return None

    @staticmethod
    def update_table(table_id, new_name):
        """Update the table name in the database."""
        query = "UPDATE shop_tables SET table_name = ? WHERE table_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (new_name, table_id))
                conn.commit()
            LogService.log_info(f"Table ID {table_id} updated to {new_name}.")
            return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while updating table: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while updating table: {e}", exc=True)
            return False

    @staticmethod
    def delete_table(table_id):

        """Delete a table from the database by its ID."""
        query = "DELETE FROM shop_tables WHERE table_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (table_id,))
                conn.commit()
            LogService.log_info(f"Table with ID {table_id} deleted.")
            return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while deleting table: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while deleting table: {e}", exc=True)
            return False


    #items

    def save_item(item_name, category, item_description, item_price, mtype):
        """Save the item to the database."""
        query = "INSERT INTO items (item_name, category, item_description, item_price, mtype) VALUES (?, ?, ?, ?, ?)"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (item_name, category, item_description, item_price, mtype))
                conn.commit()
            LogService.log_info(f"Item '{item_name}' saved successfully.")
            return True
        except sqlite3.IntegrityError:
            LogService.log_error(f"Item '{item_name}' already exists.", exc=True)
            return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while saving item: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while saving item: {e}", exc=True)
            return False

    @staticmethod
    def fetch_items(category_filter=None, search_term=None):
        """Fetch items from the database with filters."""
        if category_filter and search_term:
            query = "SELECT * FROM items WHERE category = ? AND item_name LIKE ?"
            params = [category_filter, f"%{search_term}%"]
        elif category_filter:
            query = "SELECT * FROM items WHERE category = ?"
            params = [category_filter]
        elif search_term:
            query = "SELECT * FROM items WHERE item_name LIKE ?"
            params = [f"%{search_term}%"]
        else:
            query = "SELECT * FROM items"
            params = []

        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                items = cursor.fetchall()
            LogService.log_info(f"Fetched {len(items)} items successfully.")
            return items
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching items: {e}", exc=True)
            return []
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching items: {e}", exc=True)
            return []

    @staticmethod
    def get_item_details(item_id):
        """Fetch item details by ID."""
        query = "SELECT * FROM items WHERE item_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (item_id,))
                item = cursor.fetchone()
            if item:
                return item
            return None
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching item details: {e}", exc=True)
            return None
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching item details: {e}", exc=True)
            return None

    @staticmethod
    def update_item(item_id, item_name, category, item_description, item_price, mtype):
        """Update item details in the database."""
        query = "UPDATE items SET item_name = ?, category = ?, item_description = ?, item_price = ?, mtype = ? WHERE item_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (item_name, category, item_description, item_price, mtype, item_id))
                conn.commit()
            LogService.log_info(f"Item ID {item_id} updated to '{item_name}'.")
            return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while updating item: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while updating item: {e}", exc=True)
            return False

    @staticmethod
    def delete_item(item_id):
        """Delete an item from the database by its ID."""
        query = "DELETE FROM items WHERE item_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (item_id,))
                conn.commit()
            LogService.log_info(f"Item with ID {item_id} deleted.")
            return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while deleting item: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while deleting item: {e}", exc=True)
            return False


    # CREATE ORDER

    @staticmethod
    def add_item_to_order(item_name, item_price, item_qty=1):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO cart (item_name, item_price, item_qty) VALUES (?, ?, ?)",(item_name, item_price, item_qty))
                connection.commit()
                LogService.log_info(f"Item '{item_name}' added to cart.")
            return True
        except sqlite3.IntegrityError:
            LogService.log_error("Database Integrity Error while adding item to cart.")
            return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while adding item to cart: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while adding item to cart: {e}", exc=True)
            return False

    @staticmethod
    def update_quantity(cart_id, change):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("SELECT item_qty FROM cart WHERE cart_id = ?", (cart_id,))
                result = cursor.fetchone()

                if result:
                    current_qty = int(result[0])
                    new_qty = current_qty + change

                    if new_qty > 0:
                        cursor.execute("UPDATE cart SET item_qty = ? WHERE cart_id = ?", (new_qty, cart_id))
                        connection.commit()
                        return True
                    else:
                        cursor.execute("DELETE FROM cart WHERE cart_id = ?", (cart_id,))
                        connection.commit()
                        return True
                else:
                    return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while updating quantity: {e}", exc=True)
            return "Database error"
        except Exception as e:
            LogService.log_error(f"Unexpected error while updating quantity: {e}", exc=True)
            return "Unexpected error"

    @staticmethod
    def create_order(shop_table, name, mobile, address, discount):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()

                # Fetch all items from the cart
                cursor.execute("SELECT item_name, item_price, item_qty FROM cart")
                cart_items = cursor.fetchall()

                if not cart_items:
                    return "Cart Empty"

                total_amount = sum(float(item[1]) * int(item[2]) for item in cart_items)
                final_amount = total_amount - discount

                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""INSERT INTO orders (shop_table, name, mobile, address, amount, discount, created_at) VALUES (?, ?, ?, ?, ?, ?, ?) """, (shop_table, name, mobile, address, f"{final_amount:.2f}", f"{discount:.2f}", created_at))
                order_id = cursor.lastrowid

                for item_name, item_price, item_qty in cart_items:
                    cursor.execute("""INSERT INTO orders_items (order_id, item_name, item_price, item_qty) VALUES (?, ?, ?, ?)""", (order_id, item_name, item_price, item_qty))

                cursor.execute("DELETE FROM cart")
                connection.commit()

                return "Order placed successfully"
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while creating order: {e}", exc=True)
            return "Database error"
        except Exception as e:
            LogService.log_error(f"Unexpected error while creating order: {e}", exc=True)
            return "Unexpected error"