import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright

# List of ASINs to track
ASINS = ["B0B5NG67VH", "B081QMHRC9"]  # Replace with your ASINs
CSV_FILE = "C:\\Users\\vishn\\Downloads\\amazon_price_tracking.csv"

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

    return discounted_price.strip()

# Function to scrape price for a given ASIN
async def scrape_price(asin):
    url = f"https://www.amazon.in/dp/{asin}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=10000)
            price = await get_price_details(page)
            await browser.close()
            
            # If price not found, return None
            if price == "Not found":
                return None

            return f"₹{price}"  # Ensure proper formatting

        except Exception as e:
            await browser.close()
            print(f"⚠️ Error fetching price for {asin}: {e}")
            return None

# Function to track and store prices
async def track_prices():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")  # Current timestamp
    new_data = {"ASIN": []}  # Dictionary to store new price data

    for asin in ASINS:
        price = await scrape_price(asin)
        if price:
            new_data["ASIN"].append(asin)
            new_data[f"Price_{timestamp}"] = new_data.get(f"Price_{timestamp}", []) + [price]
            new_data[f"Timestamp_{timestamp}"] = new_data.get(f"Timestamp_{timestamp}", []) + [timestamp]
        else:
            print(f"⚠️ Price not found for {asin}, skipping...")

    # Convert new data into a DataFrame
    df_new = pd.DataFrame(new_data)

    # If file exists, merge with existing data
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

        # Merge existing data with new data by ASIN
        df_merged = pd.merge(df_existing, df_new, on="ASIN", how="outer")
    else:
        df_merged = df_new

    # Save updated data to CSV
    df_merged.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    print("✅ Data saved successfully!")

# Run the script
asyncio.run(track_prices())
