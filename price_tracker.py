import asyncio
import csv
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Function to extract text safely with a timeout
async def get_text(page, selector, default="Not found"):
    try:
        element = await page.wait_for_selector(selector, timeout=5000)
        return await element.text_content() if element else default
    except:
        return default

# Function to get the discounted price with fallbacks
async def get_discounted_price(page):
    discounted_price = await get_text(page, ".apexPriceToPay span.a-offscreen")
    if discounted_price == "Not found":
        discounted_price = await get_text(page, ".a-price .a-offscreen")  # Fallback

    return discounted_price.strip()

# Function to scrape individual product data
async def scrape_amazon_product(asin):
    url = f"https://www.amazon.in/dp/{asin}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=15000)

            # Extract stock status
            stock_status = await get_text(page, "#availability span")

            # Skip extracting if stock status is "Not found"
            if stock_status == "Not found":
                print(f"⚠️ Skipping {asin}: Stock status could not be determined.")
                await browser.close()
                return None

            # Check if the product is out of stock
            if "out of stock" in stock_status.lower():
                print(f"⚠️ Skipping {asin}: Out of stock")
                await browser.close()
                return None

            # Extract discounted price
            discounted_price = await get_discounted_price(page)
            
            # Check if the price was found
            if discounted_price == "Not found":
                print(f"⚠️ Skipping {asin}: Discounted price could not be found.")
                await browser.close()
                return None

            await browser.close()
            return discounted_price

        except Exception as e:
            await browser.close()
            print(f"⚠️ Error fetching product {asin}: {e}")
            return None

# Read ASINs from a text file
def get_asins_from_file(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found.")
        return []

# Function to update CSV file with new prices and a timestamp header
def update_csv(prices, filename="amazon_price_tracking.csv"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(filename)

    if not file_exists:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            header = ["ASIN", timestamp]
            writer.writerow(header)
    else:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            data = list(reader)
        
        # Create a dictionary from existing CSV data
        data_dict = {row[0]: row for row in data}
        
        # Add new timestamp header if needed
        if len(data[0]) == len(data_dict[next(iter(data_dict))]):
            for row in data:
                row.append("")
        
        data[0].append(timestamp)

    # Update the dictionary with new prices
    for asin, price in prices.items():
        if asin in data_dict:
            data_dict[asin].append(price)
        else:
            data_dict[asin] = [asin] + [""] * (len(data[0]) - 2) + [price]

    # Write updated data back to CSV
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for row in data_dict.values():
            writer.writerow(row)

# Main function to scrape all products from the list of ASINs
async def scrape_amazon_products():
    filename = "C:/Users/project/Downloads/url500.txt"
    asin_list = get_asins_from_file(filename)

    if not asin_list:
        print("❌ No ASINs found. Exiting...")
        return

    prices = {}
    for asin in asin_list:
        discounted_price = await scrape_amazon_product(asin)
        if discounted_price:
            prices[asin] = discounted_price
            print(f"✅ Price fetched for {asin}")
        print("-" * 80)

    # Update the CSV file with the new prices
    update_csv(prices)

# Execute script
if __name__ == "__main__":
    asyncio.run(scrape_amazon_products())
