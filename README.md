# EcomPriceReco
Ecommerce Product Analysis, Trends, Price Tracking and Recommendations

Project Board Link: https://github.com/users/DikshaGori/projects/1

Project Documentation: https://docs.google.com/document/d/1brUlfKF9rhHoDA6LP8EaX4IJyitOzlJrrohtfZekUQI/edit?usp=sharing

Current Progress
Data Collection
URL Cleaning: Ensures input URLs are correctly formatted for scraping.
Price Extraction: Extracts price data from Amazon product pages.
CSV Handling: Processes and saves data to CSV files in real-time.

Key Features
Automated Data Collection: Playwright is used to scrape product details such as prices, titles, and other attributes.
Scalable URL Handling: URLs are cleaned and processed to ensure efficient and error-free scraping.
Concurrent Processing: CSV files are processed concurrently using the p-limit library to enhance performance.
Clean and Structured Output: Scraped data is saved in CSV format for further analysis.

Technology Stack
Playwright: For web scraping and automating browser interactions.
fast-csv: For handling CSV output efficiently.
p-limit: To control concurrency during processing.
Node.js: To power the entire scraping pipeline.
