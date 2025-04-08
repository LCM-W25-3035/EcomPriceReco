import csv
from time import sleep
from random import uniform
from urllib.parse import urlparse, urlunparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Function to clean the URL
def clean_url(url):
    parsed_url = urlparse(url)
    # Remove the 'ref' parameter and anything after it
    path = parsed_url.path.split("/ref")[0]
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, path, "", "", ""))
    return cleaned_url

# Function to extract the price from an Amazon product page using Selenium
def extract_price_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")

    service = Service("path/to/chromedriver")  # Replace with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        sleep(2)  # Wait for the page to load
        price_element = driver.find_element(By.CLASS_NAME, "a-price-whole")
        return price_element.text.strip()
    except Exception as e:
        return f"Error: {e}"
    finally:
        driver.quit()

# Read input CSV, process each URL, and write results to an output CSV
def process_csv(input_file, output_file):
    with open(input_file, "r", newline="", encoding="utf-8") as infile, \
         open(output_file, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Price"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            url = row.get("link")
            if not url:
                row["Price"] = "No link provided"
            else:
                cleaned_url = clean_url(url)
                row["Price"] = extract_price_with_selenium(cleaned_url)

            writer.writerow(row)

            # Sleep to avoid getting blocked by Amazon
            sleep(uniform(1, 3))

if __name__ == "__main__":
    input_csv = "../data/All-Electronics.csv"  # Replace with your input CSV file name
    output_csv = "output_data.csv"  # Replace with your desired output CSV file name

    print("Processing started. This may take a while for large datasets...")
    process_csv(input_csv, output_csv)
    print(f"Processing complete. Results written to {output_csv}")
