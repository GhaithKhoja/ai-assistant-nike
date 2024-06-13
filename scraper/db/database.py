import os
import sqlite3
import math
import json
from typing import List, Optional, Tuple

def get_connection():
    """
    Establishes a connection to the Database
    """
    # Get the current directory of this script
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Construct the path to the database file
    db_path = os.path.join(current_dir, 'database.db')
    
    # Connect to the SQLite database
    return sqlite3.connect(db_path)

def create_products_table():
    """
    Creates the products table if it doesnt exist
    """
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
    """
    Inserts a product into the products table in the database.

    Args:
    - id (str): Unique identifier for the product.
    - name (str): Name of the product.
    - promotion_status (str): Promotion status of the product.
    - price (str): Price of the product. Can contain discount information (e.g., "$95$138").
    - colors (str): Colors available for the product.
    - url (str): URL to the product's page.
    - image_src (str): Source URL for the product's image.
    - description (str): Description of the product.
    - type (str, optional): Type/category of the product. Default is None.
    """
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
    
def search_products(
        name: Optional[str] = None, 
        max_price: Optional[float] = None, 
        colors: Optional[List[str]] = None, 
        description: Optional[str] = None
    ) -> List[Tuple]:
    """
    Searches for products in the database based on the given criteria.

    Args:
    - name (str, optional): Name of the product to search for.
    - max_price (float, optional): Maximum price of the product.
    - colors (list of str, optional): List of colors to search for.
    - description (str, optional): Description text to search for.

    Returns:
    - list of tuples: A list of tuples representing the products that match the search criteria.
    """
    query = "SELECT name, price, colors, discount, description FROM products WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name.lower()}%")

    if max_price is not None:
        query += " AND CAST(price AS FLOAT) <= ?"
        params.append(max_price)

    if colors:
        query += " AND (" + " OR ".join(["colors LIKE ?" for _ in colors]) + ")"
        params.extend([f"%{color.lower()}%" for color in colors])

    if description:
        query += " AND description LIKE ?"
        params.append(f"%{description.lower()}%")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()

    products_list = []
    for result in results:
        name, price, colors, discount, description = result
        product_dict = {
            "name": name,
            "price": price,
            "colors": colors,
            "discount": discount,
            "description": description
        }
        products_list.append(product_dict)

    return json.dumps({"products": products_list}, indent=2)

def search_products_with_discounts(
        name: Optional[str] = None,
        max_price: Optional[float] = None,
        colors: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> str:
    """
    Searches for products in the database that have discounts, optionally filtering by additional criteria.

    Args:
    - name (str, optional): Name of the product to search for.
    - max_price (float, optional): Maximum price of the product.
    - colors (list of str, optional): List of colors to search for.
    - description (str, optional): Description text to search for.

    Returns:
    - str: JSON string representing the products with discounts matching the criteria.
    """
    query = "SELECT name, price, colors, discount, description FROM products WHERE discount IS NOT NULL"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name.lower()}%")

    if max_price is not None:
        query += " AND CAST(price AS FLOAT) <= ?"
        params.append(max_price)

    if colors:
        query += " AND (" + " OR ".join(["colors LIKE ?" for _ in colors]) + ")"
        params.extend([f"%{color.lower()}%" for color in colors])

    if description:
        query += " AND description LIKE ?"
        params.append(f"%{description.lower()}%")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()

    products_list = []
    for result in results:
        name, price, colors, discount, description = result
        product_dict = {
            "name": name,
            "price": price,
            "colors": colors,
            "discount": discount,
            "description": description
        }
        products_list.append(product_dict)

    return json.dumps({"products": products_list}, indent=2)

def search_new_releases(
        name: Optional[str] = None,
        max_price: Optional[float] = None,
        colors: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> str:
    """
    Searches for new releases in the database based on the given criteria.

    Args:
    - name (str, optional): Name of the product to search for.
    - max_price (float, optional): Maximum price of the product.
    - colors (list of str, optional): List of colors to search for.
    - description (str, optional): Description text to search for.

    Returns:
    - str: JSON string representing the upcoming new releases matching the criteria.
    """
    query = "SELECT name, price, colors, discount, description FROM products WHERE promotion_status IN ('Just In', 'Coming Soon')"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name.lower()}%")

    if max_price is not None:
        query += " AND CAST(price AS FLOAT) <= ?"
        params.append(max_price)

    if colors:
        query += " AND (" + " OR ".join(["colors LIKE ?" for _ in colors]) + ")"
        params.extend([f"%{color.lower()}%" for color in colors])

    if description:
        query += " AND description LIKE ?"
        params.append(f"%{description.lower()}%")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()

    products_list = []
    for result in results:
        name, price, colors, discount, description = result
        product_dict = {
            "name": name,
            "price": price,
            "colors": colors,
            "discount": discount,
            "description": description
        }
        products_list.append(product_dict)

    return json.dumps({"products": products_list}, indent=2)