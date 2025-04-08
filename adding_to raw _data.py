import asyncio
import csv
import os
import re
import time
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# File paths - using your specific paths
INPUT_CSV = r"C:\Users\vishn\Downloads\primary1.csv"
OUTPUT_CSV = r"C:\Users\vishn\Downloads\outputlast.csv"

# Weekly schedule interval in seconds (7 days)
WEEKLY_INTERVAL = 7 * 24 * 60 * 60  # 7 days in seconds

async def get_text(page, selector):
    try:
        element = await page.query_selector(selector)
        if element:
            text = await element.inner_text()
            return text.strip()
        return "Not found"
    except Exception as e:
        print(f"Error getting text from selector {selector}: {e}")
        return "Not found"

async def get_discounted_price(page):
    discounted_price = await get_text(page, ".apexPriceToPay span.a-offscreen")
    if discounted_price == "Not found":
        discounted_price = await get_text(page, ".a-price .a-offscreen")
    
    # Extract numeric value from price text
    if discounted_price != "Not found":
        # Remove non-numeric characters (except decimal points)
        numeric_price = re.sub(r'[^\d.]', '', discounted_price)
        return float(numeric_price) if numeric_price else None
    return None

def extract_numeric_price(price_str):
    """Extract numeric value from price string"""
    if not price_str or price_str == "":
        return None
    numeric_price = re.sub(r'[^\d.]', '', price_str)
    return float(numeric_price) if numeric_price else None

async def track_prices():
    """Main price tracking function"""
    print(f"Starting price tracking at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if input file exists
    if not os.path.exists(INPUT_CSV):
        print(f"Input file {INPUT_CSV} not found.")
        return
    
    # Read the input data
    products = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)

    # Initialize output file if it doesn't exist
    output_exists = os.path.exists(OUTPUT_CSV)
    
    # Define base columns for the output file
    base_columns = ['Unnamed: 0', 'name', 'main_category', 'sub_category', 'image', 'link', 
                  'ratings', 'no_of_ratings', 'discount_price', 'actual_price']
    
    # Determine max price columns needed
    max_price_columns = 0  
    
    # If output file exists, read it to capture historical data and determine max columns
    tracked_data = []
    if output_exists:
        with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
            output_reader = csv.DictReader(f)
            headers = output_reader.fieldnames
            
            # Find the highest discounted_price_X column
            for header in headers:
                if header.startswith('discounted_price_'):
                    try:
                        column_num = int(header.split('_')[-1])
                        max_price_columns = max(max_price_columns, column_num)
                    except ValueError:
                        pass
            
            # Reset file pointer and read the data
            f.seek(0)
            next(f)  # Skip header row
            output_reader = csv.DictReader(f, fieldnames=headers)
            for row in output_reader:
                tracked_data.append(row)
    
    # Increment max_price_columns for the new extraction
    max_price_columns += 1
    
    # Complete output columns list with current extraction column
    output_columns = base_columns + [f'discounted_price_{i}' for i in range(1, max_price_columns + 1)]
    
    # Launch browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        )
        
        updated_data = []
        for idx, product in enumerate(products):
            product_url = product['link']
            print(f"Processing product {idx+1}/{len(products)}: {product['name']}")
            
            # Create a new page for each product to avoid issues
            page = await context.new_page()
            
            try:
                # Navigate to product page
                await page.goto(product_url, timeout=60000)
                # Wait for price element to load - wait for either of the two selectors
                try:
                    await page.wait_for_selector(".apexPriceToPay span.a-offscreen, .a-price .a-offscreen", timeout=30000)
                except:
                    print(f"Price selector not found for {product['name']}, continuing anyway")
                
                # Get the current price using the specified function
                current_price = await get_discounted_price(page)
                print(f"Current price: {current_price}")
                
                # Find if we already have this product in our tracking
                existing_record = None
                if tracked_data:
                    for record in tracked_data:
                        if record['link'] == product_url:
                            existing_record = record
                            break
                
                # Set up the new or updated record
                if existing_record:
                    # Get the last known discounted price if current_price is None
                    if current_price is None:
                        # Try to get the last discounted price
                        for i in range(1, max_price_columns):
                            col_name = f'discounted_price_{i}'
                            if col_name in existing_record and existing_record[col_name] and existing_record[col_name].strip():
                                current_price = extract_numeric_price(existing_record[col_name])
                                print(f"Using previous price: {current_price}")
                                break
                        
                        # If no discounted price found, use initial discount_price
                        if current_price is None:
                            current_price = extract_numeric_price(existing_record['discount_price'])
                            print(f"Using initial discount price: {current_price}")
                            
                        # If still no price, use actual_price
                        if current_price is None:
                            current_price = extract_numeric_price(existing_record['actual_price'])
                            print(f"Using actual price: {current_price}")
                    
                    # Shift previous prices to the right
                    for i in range(max_price_columns, 1, -1):
                        prev_column = f'discounted_price_{i-1}' 
                        curr_column = f'discounted_price_{i}'
                        
                        if prev_column in existing_record:
                            existing_record[curr_column] = existing_record[prev_column]
                    
                    # Add new price at position 1
                    if current_price:
                        existing_record['discounted_price_1'] = str(current_price)
                    else:
                        # Fallback to ensure something is in the column
                        existing_record['discounted_price_1'] = ""
                        
                    updated_data.append(existing_record)
                else:
                    # Create a new record
                    new_record = {
                        'Unnamed: 0': str(idx),
                        'name': product['name'],
                        'main_category': product['main_category'],
                        'sub_category': product['sub_category'],
                        'image': product['image'],
                        'link': product['link'],
                        'ratings': product['ratings'],
                        'no_of_ratings': product['no_of_ratings'],
                        'discount_price': product['discount_price'],
                        'actual_price': product['actual_price']
                    }
                    
                    # If no current price found, try to use discount_price from input
                    if current_price is None:
                        current_price = extract_numeric_price(product['discount_price'])
                        print(f"Using initial discount price: {current_price}")
                        
                        # If still no price, use actual_price
                        if current_price is None:
                            current_price = extract_numeric_price(product['actual_price'])
                            print(f"Using actual price: {current_price}")
                    
                    # Add the current price as the first historical price
                    if current_price:
                        new_record['discounted_price_1'] = str(current_price)
                    else:
                        new_record['discounted_price_1'] = ""
                    
                    # Initialize other price columns
                    for i in range(2, max_price_columns + 1):
                        new_record[f'discounted_price_{i}'] = ""
                    
                    updated_data.append(new_record)
            except Exception as e:
                print(f"Error processing {product_url}: {e}")
                
                # Still add the product to our tracking even if we couldn't get a price
                new_record = {
                    'Unnamed: 0': str(idx),
                    'name': product['name'],
                    'main_category': product['main_category'],
                    'sub_category': product['sub_category'],
                    'image': product['image'],
                    'link': product['link'],
                    'ratings': product['ratings'],
                    'no_of_ratings': product['no_of_ratings'],
                    'discount_price': product['discount_price'],
                    'actual_price': product['actual_price']
                }
                
                # Try to use discount_price if scraping failed
                current_price = extract_numeric_price(product['discount_price'])
                if current_price is None:
                    current_price = extract_numeric_price(product['actual_price'])
                
                if current_price:
                    new_record['discounted_price_1'] = str(current_price)
                else:
                    new_record['discounted_price_1'] = ""
                
                # Initialize other price columns
                for i in range(2, max_price_columns + 1):
                    new_record[f'discounted_price_{i}'] = ""
                
                updated_data.append(new_record)
            finally:
                await page.close()
        
        await context.close()
        await browser.close()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # Write the updated data to the output file
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(updated_data)
    
    print(f"Price tracking data saved to {OUTPUT_CSV} with {max_price_columns} historical price columns")
    print(f"Price tracking completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

async def run_weekly():
    """Run price tracking on a weekly schedule"""
    print("Starting weekly price tracking scheduler")
    print(f"Next run scheduled for: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
        try:
            # Run the price tracking
            success = await track_prices()
            
            # Calculate next run time (one week from now)
            next_run = datetime.now() + timedelta(days=7)
            print(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Sleep until next week
            await asyncio.sleep(WEEKLY_INTERVAL)
        except Exception as e:
            print(f"Error in weekly scheduler: {e}")
            # If there's an error, wait 1 hour and try again
            print("Will retry in 1 hour")
            await asyncio.sleep(3600)

def run_once():
    """Run the price tracking once"""
    asyncio.run(track_prices())
    print("One-time price tracking complete")

def start_weekly_schedule():
    """Start the weekly schedule"""
    asyncio.run(run_weekly())

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1].lower() == "weekly":
        print("Starting price tracker in weekly mode")
        start_weekly_schedule()
    else:
        print("Running price tracker once. Add 'weekly' parameter to run on a weekly schedule.")
        run_once()