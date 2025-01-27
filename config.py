import os
from dotenv import load_dotenv

load_dotenv()

SHOP_NAME = os.getenv("SHOP_NAME", "Scurite Restaurant POS")
SHOP_MOBILE = os.getenv("SHOP_MOBILE", "0000000000")
CURRENCY = os.getenv("CURRENCY", "₹")
DB_PATH = os.getenv("DB_PATH", "db/database.db")
