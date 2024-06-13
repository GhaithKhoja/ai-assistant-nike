import os
import sqlite3
import math

def get_connection():
    # Get the current directory of this script
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Construct the path to the database file
    db_path = os.path.join(current_dir, 'database.db')
    
    # Connect to the SQLite database
    return sqlite3.connect(db_path)

def create_products_table():
    # Get connection to the table and create the table if it does not exist
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            promotion_status TEXT,
            price TEXT,
            discount TEXT,
            colors TEXT,
            url TEXT,
            image_src TEXT,
            description TEXT
        )
        ''')
        conn.commit()

def insert_product(id, name, promotion_status, price, colors, url, image_src, description, type=None):
    # Check if there is a discount for the price
    price_parts = price.split('$')[1:]  # Split and remove the empty string before the first '$'
    
    # If there are two elements in the array it means that there is a a discount
    if len(price_parts) == 2:
        # There is a discount
        current_price = float(price_parts[0])
        original_price = float(price_parts[1])
        discount = math.floor(((original_price - current_price) / original_price) * 100)
        discount = f"%{discount}"
    else:
        # No discount
        current_price = float(price_parts[0])
        discount = None
    
    # Get connection to the DB and insert the information
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO products (id, name, type, promotion_status, price, discount, colors, url, image_src, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', 
        (id,
         name.lower(),
         type.lower() if type else None,
         promotion_status,
         f"${current_price}",
         discount,
         colors.lower() if colors else None,
         url,
         image_src,
         description.lower() if description else None
        ))
        conn.commit()
