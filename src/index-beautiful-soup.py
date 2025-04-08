import csv
import requests
from bs4 import BeautifulSoup
from time import sleep
from random import uniform
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# Function to clean the URL
def clean_url(url):
    parsed_url = urlparse(url)
    # Remove the 'ref' parameter and anything after it
    path = parsed_url.path.split("/ref")[0]
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, path, "", "", ""))
    return cleaned_url

# Function to extract the price from an Amazon product page
def extract_price(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, "html.parser")

        print(url)

        # Write the soup to a file for debugging
        with open("debug_soup.html", "w", encoding="utf-8") as debug_file:
            debug_file.write(soup.prettify())

        # Look for the price using common Amazon price selectors
        price_tag = soup.find("span", {"class": "a-price-whole"})
        print(price_tag)
        print(price_tag)
        if price_tag:
            return price_tag.text.strip()
        else:
            return "Price not found"

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

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
                row["Price"] = extract_price(cleaned_url)

            writer.writerow(row)

            # Sleep to avoid getting blocked by Amazon
            sleep(uniform(1, 3))

if __name__ == "__main__":
    input_csv = "All-Electronics.csv"  # Replace with your input CSV file name
    output_csv = "output_data.csv"  # Replace with your desired output CSV file name

    print("Processing started. This may take a while for large datasets...")
    process_csv(input_csv, output_csv)
    print(f"Processing complete. Results written to {output_csv}")
