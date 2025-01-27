import sqlite3
from datetime import datetime

from config import DB_PATH
from service.log_service import LogService


class DBService:
    @staticmethod
    def get_connection():
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def fetch_all_orders(date=None):
        """Fetch all orders from the database, optionally filtered by date."""
        if date:
            # Query for fetching orders by a specific date
            query = """SELECT o.order_id, o.shop_table, o.name, o.mobile, o.address, o.amount, o.discount, o.status, o.created_at, 
                                  (SELECT COUNT(*) FROM orders_items WHERE orders_items.order_id = o.order_id) AS item_count 
                           FROM orders o
                           WHERE o.created_at LIKE ?
                           ORDER BY o.order_id DESC"""
            params = (f"{date}%",)  # Filter by date using LIKE
        else:
            # Query for fetching all orders
            query = """SELECT o.order_id, o.shop_table, o.name, o.mobile, o.address, o.amount, o.discount, o.status, o.created_at, 
                                  (SELECT COUNT(*) FROM orders_items WHERE orders_items.order_id = o.order_id) AS item_count 
                           FROM orders o
                           ORDER BY o.order_id DESC"""
            params = ()  # No parameters needed for all orders query

        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
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
    def fetch_running_orders():
        query = """SELECT o.order_id, o.shop_table, o.name, o.mobile, o.address, ROUND((SELECT SUM(item_price * item_qty) FROM orders_items WHERE orders_items.order_id = o.order_id), 2) AS amount, o.discount, o.status, o.created_at, (SELECT COUNT(*) FROM orders_items WHERE orders_items.order_id = o.order_id) AS item_count FROM orders o WHERE o.status NOT IN ('Cancelled', 'Done', 'Delivered') ORDER BY o.order_id DESC"""
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
        query = "SELECT category_id, category_name FROM category"
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

    def save_item(item_name, category, item_price, mtype):
        """Save the item to the database."""
        query = "INSERT INTO items (item_name, category, item_price, mtype) VALUES (?, ?, ?, ?)"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (item_name, category, item_price, mtype))
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
        """Fetch items with variations as comma-separated values."""
        if category_filter and search_term:
            # Filter by category and search term
            query = """ SELECT items.item_id, items.item_name, items.category, items.item_price, items.mtype, GROUP_CONCAT(variations.v_name, ', ') AS variation_names, GROUP_CONCAT(variations.v_price, ', ') AS variation_prices FROM items LEFT JOIN variations ON items.item_id = variations.v_item WHERE items.category = ? AND items.item_name LIKE ? GROUP BY items.item_id ORDER BY items.item_id; """
            params = [category_filter, f"%{search_term}%"]
        elif category_filter:
            # Filter by category only
            query = """ SELECT items.item_id, items.item_name, items.category, items.item_price, items.mtype, GROUP_CONCAT(variations.v_name, ', ') AS variation_names, GROUP_CONCAT(variations.v_price, ', ') AS variation_prices FROM items LEFT JOIN variations ON items.item_id = variations.v_item WHERE items.category = ? GROUP BY items.item_id ORDER BY items.item_id; """
            params = [category_filter]
        elif search_term:
            # Search by item name only
            query = """ SELECT items.item_id, items.item_name, items.category, items.item_price, items.mtype, GROUP_CONCAT(variations.v_name, ', ') AS variation_names, GROUP_CONCAT(variations.v_price, ', ') AS variation_prices FROM items LEFT JOIN variations ON items.item_id = variations.v_item WHERE items.item_name LIKE ? GROUP BY items.item_id ORDER BY items.item_id; """
            params = [f"%{search_term}%"]
        else:
            # Fetch all items
            query = """ SELECT items.item_id, items.item_name, items.category, items.item_price, items.mtype, GROUP_CONCAT(variations.v_name, ', ') AS variation_names, GROUP_CONCAT(variations.v_price, ', ') AS variation_prices FROM items LEFT JOIN variations ON items.item_id = variations.v_item GROUP BY items.item_id ORDER BY items.item_id; """
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
    def update_item(item_id, item_name, category, item_price, mtype):
        """Update item details in the database."""
        query = "UPDATE items SET item_name = ?, category = ?, item_price = ?, mtype = ? WHERE item_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (item_name, category, item_price, mtype, item_id))
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

    def add_item_to_cart(item_id):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT item_name, item_price FROM items WHERE item_id = ?", (item_id,))
                item = cursor.fetchone()
                if not item:
                    LogService.log_error(f"Item with ID {item_id} not found.")
                    return False

                item_name, item_price = item
                item_qty = 1
                cursor.execute("INSERT INTO cart (item_name, item_price, item_qty) VALUES (?, ?, ?)",(item_name, item_price, item_qty))
                connection.commit()
                LogService.log_info(f"Item '{item_name}' with ID {item_id} added to cart (Qty: {item_qty}).")
                return True

        except sqlite3.IntegrityError:
            LogService.log_error(f"Database Integrity Error while adding item ID {item_id} to cart.")
            return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while adding item ID {item_id} to cart: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while adding item ID {item_id} to cart: {e}", exc=True)
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
    def create_order(shop_table, name, mobile, address):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()

                # Fetch all items from the cart
                cursor.execute("SELECT item_name, item_price, item_qty FROM cart")
                cart_items = cursor.fetchall()

                # Check if the cart is empty
                if not cart_items:
                    return "Cart Empty"

                # Calculate the total amount and final amount after discount
                total_amount = sum(float(item[1]) * int(item[2]) for item in cart_items)
                final_amount = total_amount

                # Get the current time for the created_at field
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""INSERT INTO orders (shop_table, name, mobile, address, amount, created_at) VALUES (?, ?, ?, ?, ?, ?)""", (shop_table, name, mobile, address, f"{final_amount:.2f}", created_at))
                order_id = cursor.lastrowid

                # Insert items from the cart into the orders_items table
                for item_name, item_price, item_qty in cart_items:
                    cursor.execute("""INSERT INTO orders_items (order_id, item_name, item_price, item_qty)VALUES (?, ?, ?, ?)""", (order_id, item_name, item_price, item_qty))

                cursor.execute("DELETE FROM cart")
                connection.commit()

                return "Order placed successfully"

        except sqlite3.Error as e:
            LogService.log_error(f"Database error while creating order: {e}", exc=True)
            return "Database error"

        except Exception as e:
            LogService.log_error(f"Unexpected error while creating order: {e}", exc=True)
            return "Unexpected error"


    @staticmethod
    def get_cart_items():
        """Fetch all items from the cart."""
        query = "SELECT cart_id, item_name, item_price, item_qty FROM cart"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                items = cursor.fetchall()  # List of tuples
            return items if items else []
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching cart items: {e}", exc=True)
            return []
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching cart items: {e}", exc=True)
            return []

    @staticmethod
    def calculate_cart_total():
        """Calculate the total price of all items in the cart."""
        query = "SELECT SUM(item_price * item_qty) FROM cart"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
            return result[0] if result[0] is not None else 0.0
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while calculating cart total: {e}", exc=True)
            return 0.0
        except Exception as e:
            LogService.log_error(f"Unexpected error while calculating cart total: {e}", exc=True)
            return 0.0


    #UPDATE ORDER

    @staticmethod
    def fetch_order_info(order_id):
        query = """SELECT order_id, shop_table, name, mobile, address, amount, discount, status, created_at FROM orders WHERE order_id = ?"""
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (order_id,))
                order_info = cursor.fetchone()
                if order_info:
                    LogService.log_info(f"Order info fetched successfully for order_id: {order_id}")
                    return order_info
                else:
                    LogService.log_warning(f"No order found with order_id: {order_id}")
                    return None
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching order info for order_id: {order_id}: {e}", exc=True)
            return None
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching order info for order_id: {order_id}: {e}", exc=True)
            return None

    @staticmethod
    def get_order_items(order_id):
        """Fetch all items for a specific order from the order_items table."""
        query = "SELECT item_id, item_name, item_qty, item_price FROM orders_items WHERE order_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (order_id,))
                items = cursor.fetchall()  # List of tuples
            return items if items else []
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching cart items: {e}", exc=True)
            return []
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching cart items: {e}", exc=True)
            return []

    @staticmethod
    def update_order_quantity(item_id, change):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("SELECT item_qty FROM orders_items WHERE item_id = ?", (item_id,))
                result = cursor.fetchone()

                if result:
                    current_qty = int(result[0])
                    new_qty = current_qty + change

                    if new_qty > 0:
                        cursor.execute("UPDATE orders_items SET item_qty = ? WHERE item_id = ?", (new_qty, item_id))
                        connection.commit()
                        return True
                    else:
                        cursor.execute("DELETE FROM orders_items WHERE item_id = ?", (item_id,))
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
    def add_item_to_order(item_id, order_id):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT item_name, item_price FROM items WHERE item_id = ?", (item_id,))
                item = cursor.fetchone()
                if not item:
                    LogService.log_error(f"Item with ID {item_id} not found.")
                    return False

                item_name, item_price = item
                item_qty = 1

                cursor = connection.cursor()
                cursor.execute("INSERT INTO orders_items (order_id, item_name, item_price, item_qty) VALUES (?, ?, ?, ?)",(order_id, item_name, item_price, item_qty),)
                connection.commit()
                LogService.log_info(f"Item '{item_name}' added to order {order_id}.")
            return True
        except sqlite3.IntegrityError:
            LogService.log_error("Database Integrity Error while adding item to order.")
            return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while adding item to order: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while adding item to order: {e}", exc=True)
            return False

    @staticmethod
    def calculate_order_total(order_id):
        """Calculate the total price of all items in an order."""
        query = "SELECT SUM(item_price * item_qty) FROM orders_items WHERE order_id = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (order_id,))
                result = cursor.fetchone()
            return result[0] if result[0] is not None else 0.0
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while calculating order total: {e}", exc=True)
            return 0.0
        except Exception as e:
            LogService.log_error(f"Unexpected error while calculating order total: {e}", exc=True)
            return 0.0

    #Variation

    @staticmethod
    def insert_variation(item_id, variation_name, variation_price):
        """Inserts a variation for a given item into the database."""
        try:
            with DBService.get_connection() as connection:  # Assuming `get_connection` handles the DB connection
                cursor = connection.cursor()
                cursor.execute("INSERT INTO variations (v_item, v_name, v_price) VALUES (?, ?, ?)",
                               (item_id, variation_name, variation_price))
                connection.commit()
                LogService.log_info(f"Variation '{variation_name}' for item ID {item_id} added successfully.")
            return True
        except sqlite3.IntegrityError:
            LogService.log_error("Database Integrity Error while inserting variation.")
            return False
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while inserting variation: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while inserting variation: {e}", exc=True)
            return False

    @staticmethod
    def fetch_variations(item_id):
        print(item_id)
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT vid, v_name, v_price FROM variations WHERE v_item = ? """, (item_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            LogService.log_error(f"Error fetching variations for item ID {item_id}: {e}", exc=True)
            return []

    @staticmethod
    def delete_variation(variation_id):
        """Delete a specific variation from the database."""
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""DELETE FROM variations WHERE vid = ?""", (variation_id,))
                connection.commit()
                LogService.log_info(f"Variation ID {variation_id} deleted.")
                return True
        except sqlite3.Error as e:
            LogService.log_error(f"Error deleting variation ID {variation_id}: {e}", exc=True)
            return False

    @staticmethod
    def update_variation(variation_id, variation_name, variation_price):
        """Update the variation in the database."""
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""UPDATE variations SET v_name = ?, v_price = ? WHERE vid = ? """, (variation_name, variation_price, variation_id))
                connection.commit()
                LogService.log_info(f"Variation ID {variation_id} updated.")
            return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while updating variation: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while updating variation: {e}", exc=True)
            return False

    @staticmethod
    def getVariationCount(item_id):
        query = "SELECT COUNT(*) FROM variations WHERE v_item = ?"
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (item_id,))
                result = cursor.fetchone()
            count = result[0] if result and result[0] is not None else 0
            LogService.log_info(f"Item ID {item_id} has {count} variations.")
            return count
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while fetching variation count for Item ID {item_id}: {e}", exc=True)
            return 0
        except Exception as e:
            LogService.log_error(f"Unexpected error while fetching variation count for Item ID {item_id}: {e}", exc=True)
            return 0

    @staticmethod
    def add_variation_to_cart(variation_id):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""SELECT i.item_name, v.v_name, v.v_price FROM variations v JOIN items i ON v.v_item = i.item_id WHERE v.vid = ?""", (variation_id,))
                result = cursor.fetchone()

                if not result:
                    LogService.log_error(f"Variation ID {variation_id} not found.")
                    return False

                item_name, variation_name, variation_price = result
                full_name = f"{item_name} - {variation_name}"
                variation_qty = 1
                cursor.execute("""INSERT INTO cart (item_name, item_price, item_qty) VALUES (?, ?, ?)""", (full_name, variation_price, variation_qty))
                connection.commit()
                LogService.log_info(f"Variation '{full_name}' with ID {variation_id} added to cart.")
                return True

        except sqlite3.Error as e:
            LogService.log_error(f"Database error while adding variation ID {variation_id} to cart: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while adding variation ID {variation_id} to cart: {e}", exc=True)
            return False

    @staticmethod
    def add_variation_to_order(variation_id, order_id):
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT i.item_name, v.v_name, v.v_price FROM variations v JOIN items i ON v.v_item = i.item_id WHERE v.vid = ?""", (variation_id,))
                result = cursor.fetchone()

                if not result:
                    LogService.log_error(f"Variation ID {variation_id} not found.")
                    return False

                item_name, variation_name, variation_price = result
                full_name = f"{item_name} - {variation_name}"
                variation_qty = 1

                cursor.execute("""INSERT INTO orders_items (order_id, item_name, item_price, item_qty) VALUES (?, ?, ?, ?)""", (order_id, full_name, variation_price, variation_qty))
                connection.commit()
                LogService.log_info(f"Variation '{full_name}' with ID {variation_id} added to order {order_id}.")
                return True

        except sqlite3.Error as e:
            LogService.log_error(f"Database error while adding variation ID {variation_id} to order {order_id}: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while adding variation ID {variation_id} to order {order_id}: {e}", exc=True)
            return False

    @staticmethod
    def update_order_status(order_id, status):
        query = "UPDATE orders SET status = ? WHERE order_id = ?"
        try:
            with DBService.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, (status, order_id))
                connection.commit()

                if cursor.rowcount > 0:
                    LogService.log_info(f"Order ID {order_id} updated to status '{status}'.")
                    return True
                else:
                    LogService.log_error(f"Order ID {order_id} not found for status update.")
                    return False

        except sqlite3.Error as e:
            LogService.log_error(f"Database error while updating order ID {order_id} status: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while updating order ID {order_id} status: {e}", exc=True)
            return False

    @staticmethod
    def update_order(order_id, name, mobile, address, discount, amount):
        query = """UPDATE orders SET name = ?, mobile = ?, address = ?, discount = ?, amount = ?, status = 'Done' WHERE order_id = ?"""
        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, mobile, address, discount, amount, order_id))
                conn.commit()
                LogService.log_info(f"Order with ID {order_id} updated successfully.")
                return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while updating order {order_id}: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while updating order {order_id}: {e}", exc=True)
            return False


    @staticmethod
    def delete_order(order_id):
        # Start a transaction to ensure both deletions are atomic
        try:
            # First, delete the items associated with the order from orders_items
            delete_items_query = "DELETE FROM orders_items WHERE order_id = ?"
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(delete_items_query, (order_id,))
                conn.commit()

            # Now, delete the order itself from the orders table
            delete_order_query = "DELETE FROM orders WHERE order_id = ?"
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(delete_order_query, (order_id,))
                conn.commit()

            LogService.log_info(f"Order with ID {order_id} and its items deleted successfully.")
            return True
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while deleting order {order_id}: {e}", exc=True)
            return False
        except Exception as e:
            LogService.log_error(f"Unexpected error while deleting order {order_id}: {e}", exc=True)
            return False

    @staticmethod
    def search_orders(search_text):
        query = """
            SELECT o.order_id, o.shop_table, o.name, o.mobile, o.address, 
                   o.amount, o.discount, o.status, o.created_at,
                   (SELECT COUNT(*) FROM orders_items WHERE orders_items.order_id = o.order_id) AS item_count
            FROM orders o
            WHERE o.order_id LIKE ?
               OR o.name LIKE ?
               OR o.mobile LIKE ?
               OR o.address LIKE ?
            ORDER BY o.order_id DESC
        """
        wildcard_search_text = f"%{search_text}%"
        params = (wildcard_search_text, wildcard_search_text, wildcard_search_text, wildcard_search_text)

        try:
            with DBService.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                orders = cursor.fetchall()
                LogService.log_info(f"Search for orders with text '{search_text}' completed successfully.")
                return orders
        except sqlite3.Error as e:
            LogService.log_error(f"Database error while searching for orders with text '{search_text}': {e}", exc=True)
            return []
        except Exception as e:
            LogService.log_error(f"Unexpected error while searching for orders with text '{search_text}': {e}",exc=True)
            return []
