from selenium import webdriver
from bs4 import BeautifulSoup
from db.database import create_products_table, insert_product
from image_processing import run_image_processing
import requests
import time
import re

def get_page_content(url):
    """
    Fetches the HTML content of a web page specified by the URL using Selenium WebDriver.
    
    Args:
    - url (str): The URL of the web page to fetch.
    
    Returns:
    - str: The HTML content of the fetched web page.
    
    This function initializes a headless Chrome WebDriver, navigates to the given URL,
    waits for product images to load, and then retrieves the page source.
    """
    
    # Imitate a chrome web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # So we do not open the GUI
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    # Nike websites loads images then replaces placeholders using javascript
    # We wait for a short time so the actual images get loaded in their place
    # Specifically we wait for the product images to load
    # Moreover we scroll and wait for products to load
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Wait for the page to load
        time.sleep(3)
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait for new products to load
        time.sleep(3)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # If heights are the same, break the loop
        last_height = new_height
    
    # Fetch the content then close the web driver
    content = driver.page_source
    driver.quit()
    
    # Return the content
    return content


def parse_product_card(product_card):
    """
    Parses the product card to extract various details including product name, promotion status, price, image source,
    and details of other color variants if available.
    
    Adds the product and all of its different colors into the DB.

    Args:
    - product_card (BeautifulSoup Tag): The BeautifulSoup Tag object representing the product card.

    Returns:
    Tuple: A tuple containing the following elements in order:
        - product_id (str): The unique identifier of the product.
        - name (str): The name of the product.
        - promotion_status (str or None): The promotional status message (e.g., "On Sale", "Just New").
        - price (str): The price of the product.
        - colors (str): The primary color(s) of the product.
        - url (str): The URL of the product listing.
        - image_src (str): The URL of the main product image.
        - Description (str): Description of the product

    Notes:
    - This function uses BeautifulSoup and Selenium WebDriver to navigate and extract data from web pages.
    - It assumes specific HTML structure and class names for locating elements.
    - Uses Chrome WebDriver in headless mode (--headless) to avoid opening a GUI.
    - Waits for the page to load to ensure correct extraction of data.
    """
    # Extract product name and URL
    link = product_card.find('a', class_='product-card__link-overlay')
    name = link.text.strip()
    url = link['href']
    
    # Extract messaging if exists
    # Messaging can be something like "Just coming in" or "On Sale"
    message_tag = product_card.find('div', {'data-testid': 'product-card__messaging'})
    promotion_status = message_tag.text.strip() if message_tag else None
    
    # Extract price if exists
    price_tag = product_card.find('div', {'data-testid': 'product-card__price'})
    price = price_tag.text.strip() if price_tag else None
    
    # Extract the image of product
    image_tag = product_card.find('img', class_=re.compile(r'^product-card__hero-image'))
    image_url = image_tag['src'] if image_tag else None
    
    # Now we will use the web driver again to enter the product page and fetch more details
    # We will fetch the color of the shoe, its id and any other colors that shoe has
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # So we do not open the GUI
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    time.sleep(1)  # Wait for the page to load so images are not placeholders
        
    # Parse product details
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Extract Product description
    description_element = soup.find('div',class_=re.compile(r'^description-preview'))
    if description_element:   
        p_tag = description_element.find('p')
        description = p_tag.text.strip() if p_tag else None
    else:
        description = None
    
    # Extract "Shown:" details
    shown_element = soup.find('li', class_='description-preview__color-description')
    colors = shown_element.text.split('Shown:')[1].strip() if shown_element else None
    
    # Extract "Style:" details
    style_element = soup.find('li', class_='description-preview__style-color')
    product_id = style_element.text.split('Style:')[1].strip() if style_element else None
    
    # For other colors of the shoe extract their URLs, image url, and id
    colorway_div = soup.find('div', id='ColorwayDiv')
    if colorway_div:
        colorway_containers = colorway_div.find_all('div', class_=re.compile(r'^css-7aigzk colorway-container'))
        # Go over each color of the same product
        for container in colorway_containers:
            # Find the product id of the color
            input_tag = container.find('input', {'name': 'pdp-colorpicker'})
            product_id = input_tag['data-style-color'] if input_tag else None
            
            # Find the image url of the color
            img_tag = container.find('img')
            image_url = img_tag['src'] if img_tag else None
            
            # Construct the url of the product color using the parent url
            parent_url = url.split('/')
            parent_url[-1] = product_id
            cur_url = '/'.join(parent_url)
            
            # Parse the child product details
            # Can use this later to parse sizes as well
            cur_request = requests.get(cur_url)
            soup = BeautifulSoup(cur_request.text, 'html.parser')
            
            # Extract "Shown:" details
            shown_element = soup.find('li', class_='description-preview__color-description')
            colors = shown_element.text.split('Shown:')[1].strip() if shown_element else None
            
            # Enter child product into the db
            try:
                insert_product(
                    id=product_id,
                    name=name,
                    promotion_status=promotion_status,
                    price=price,
                    colors=colors,
                    url=cur_url,
                    image_src=image_url,
                    description=description
                )
            except Exception as e:
                print(f'Error inserting product: {name} - Error: {str(e)}')
    else:
        # Just add the product to the db
        try:
            insert_product(
                id=product_id,
                name=name,
                promotion_status=promotion_status,
                price=price,
                colors=colors,
                url=url,
                image_src=image_url,
                description=description
            )
        except Exception as e:
            print(f'Error inserting product: {name} - Error: {str(e)}')
             
    # Close the web browser after the use
    driver.quit()
    
    # Returns tuple, used this mainly to print information to make sure everything ran smoothly
    return (product_id, name, promotion_status, price, colors, url, image_url, description)


def scrape_main_page(base_url):
    """
    Scrapes the main page of a website to extract product information from product cards.

    Args:
    - base_url (str): The base URL of the main page to scrape.
    """
    content = get_page_content(base_url)
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all product card elements
    product_cards = soup.find_all('div', class_='product-card__body')
    for product_card in product_cards:
        parse_product_card(product_card)

# Main function to run the scraper
def main():
    # Define the base url to scrape from
    base_url = 'https://www.nike.com/w/mens-jordan-shoes-37eefznik1zy7ok'
    
    # Create the DB table if it does not exist
    create_products_table()
    
    # Parse and save products
    scrape_main_page(base_url=base_url)
    
    # Run image processing to filter the shoes into types
    run_image_processing()

if __name__ == '__main__':
    main()
