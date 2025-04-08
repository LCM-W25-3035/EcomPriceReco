import asyncio
import csv
import os
import random
import time
from playwright.async_api import async_playwright

# Function to extract text safely with a timeout
async def get_text(page, selector, default="Not found"):
    try:
        element = await page.wait_for_selector(selector, timeout=5000)
        return await element.text_content() if element else default
    except:
        return default

# Function to get the price details with fallbacks
async def get_price_details(page):
    discounted_price = await get_text(page, ".apexPriceToPay span.a-offscreen")
    if discounted_price == "Not found":
        discounted_price = await get_text(page, ".a-price .a-offscreen")  # Fallback

    price = await get_text(page, ".a-text-price span.a-offscreen")
    if price == "Not found":
        price = await get_text(page, ".a-price .a-offscreen")  # Fallback

    return discounted_price.strip(), price.strip()

# Function to scrape individual product data
async def scrape_amazon_product(asin):
    url = f"https://www.amazon.in/dp/{asin}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=15000)

            # Extract product details
            title = await get_text(page, "#productTitle")
            brand = await get_text(page, "#bylineInfo")
            stock_status = await get_text(page, "#availability span")

            # **Skip extracting if stock status is "Not found"**
            if stock_status == "Not found":
                print(f"⚠️ Skipping {asin}: Stock status could not be determined.")
                await browser.close()
                return None

            # Check if the product is out of stock
            if "out of stock" in stock_status.lower():
                print(f"⚠️ Skipping {asin}: Out of stock")
                await browser.close()
                return None

            review_count = await get_text(page, "#acrCustomerReviewText", "No reviews")
            rating = await get_text(page, ".a-icon-alt", "No ratings")

            # Extract price details
            discounted_price, price = await get_price_details(page)

            # Format the data
            product_data = [
                asin, title.strip(), brand.strip(), discounted_price, price,
                stock_status.strip(), rating.strip(), review_count.strip(), url
            ]

            await browser.close()
            return product_data

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

# Function to append data to CSV file
def append_to_csv(data, filename="20kamazon_data.csv"):
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["ASIN", "Title", "Brand", "Discounted Price", "Actual Price",
                             "Stock Status", "Rating", "Review Count", "URL"])
        writer.writerow(data)

# Function to introduce a random delay between 15-30 minutes
def random_delay(min_time=15, max_time=30):
    delay = random.randint(min_time * 60, max_time * 60)
    print(f"⏳ Waiting for {delay / 60:.2f} minutes...")
    time.sleep(delay)

# Main function to scrape all products from the list of ASINs
async def scrape_amazon_products():
    filename = "20000asins.txt"
    asin_list = get_asins_from_file(filename)

    if not asin_list:
        print("❌ No ASINs found. Exiting...")
        return

    count = 0
    for asin in asin_list:
        product_data = await scrape_amazon_product(asin)
        if product_data:
            append_to_csv(product_data)
            print(f"✅ Data saved for {asin}")
        count += 1

        # After every 100 products, introduce a random delay
        if count % 100 == 0:
            random_delay()  # Adds a delay between 15-30 minutes

        print("-" * 80)

# Execute script
if __name__ == "__main__":
    asyncio.run(scrape_amazon_products())
