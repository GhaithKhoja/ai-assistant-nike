import os
from openai import OpenAI
from dotenv import load_dotenv
from db.database import get_product_details, insert_product_type

# Load environment variables from .env file
load_dotenv()

# Load the OpenAI key
api_key = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=api_key)
    
def run_image_processing():
    """
    Uses shoes names to match them into types, if the name does not mention the shoe type we use gpt vision.
    """
    products = get_product_details()

    for product in products:
        # Get product details
        id, name, image_url = product
        
        # Check if the name contains any of the keywords
        shoe_type = None
        if any(keyword in name.lower() for keyword in ['low', 'mid', 'high', 'basketball', 'slides']):
            if 'low' in name.lower():
                shoe_type = 'low'
            elif 'mid' in name.lower():
                shoe_type = 'mid'
            elif 'high' in name.lower():
                shoe_type = 'high'
            elif 'basketball' in name.lower():
                shoe_type = 'basketball'
            elif 'slides' in name.lower():
                shoe_type = 'slides'
            else:
                shoe_type = None  # Default case if none of the keywords match
        
        # If no shoe type from name, use GPT-4 to extract
        if not shoe_type:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "The image you are seeing is an Air Jordans product. Categorize the product in the image into one of the following: low, mid, high, basketball, slides. Only output the category and nothing else"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                        ],
                    }
                ],
            )
            shoe_type = response.choices[0].message.content.strip().lower()
            print(f"For shoe with id {id} gpt vision categorized it into type {shoe_type}")

        # Ensure shoe_type is within specified categories or default to 'low'
        valid_shoe_types = ['low', 'mid', 'high', 'basketball', 'slides']
        if shoe_type not in valid_shoe_types:
            shoe_type = 'low'  # Default to 'low' if not recognized

        # Update the database with the shoe type
        insert_product_type(id, shoe_type)
        
# Main function to run the image processing
def main():
    run_image_processing()

if __name__ == '__main__':
    main()