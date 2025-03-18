## Ecommerce Product Analysis, Trends, Price Tracking and Recommendations
Project Overview
This project aims to collect and analyze product data from Amazon, track prices, and provide product recommendations based on trends. The scraping pipeline is built using Playwright for efficient web scraping, and the data is processed and saved into structured CSV files using fast-csv and p-limit libraries. The project is now in the UI stage, with feature engineering and model building incorporated to enhance the recommendation system and predict price trends using Random Forest (RF) and XGBoost models.

Project Board Link: https://github.com/users/DikshaGori/projects/1

Current Progress

Data Collection
URL Cleaning: Ensures all input URLs are correctly formatted before scraping to avoid errors during the extraction process.
Price Extraction: Scrapes product details such as prices, titles, and other attributes from Amazon product pages.
CSV Handling: Data is processed and saved into CSV files in real-time for easy analysis.

Feature Engineering
To build a recommendation system and track price trends, several key features have been engineered:

Price History: Track the price of each product over time to identify pricing trends.
Product Attributes: Extracted features like product category, title, and ratings, which will be used to recommend similar products.
Time-based Features: Including the time of the last price update to help identify seasonal trends or promotions.
Price vs. Rating Correlation: A feature to evaluate the relationship between product pricing and its user rating for better recommendations.

Model Building
Using the engineered features, two key machine learning models have been developed to enhance the recommendation system and predict price trends:

1. Random Forest (RF) Model
The Random Forest model is used for predicting product prices based on the historical data and features such as ratings, price history, and product attributes. This model is based on an ensemble learning technique that uses multiple decision trees to improve prediction accuracy and robustness. It helps in:

Price Prediction: Predicting the potential price of a product based on trends and attributes.
Feature Importance: Identifying the most influential features that impact product pricing.
2. XGBoost Model
The XGBoost model is implemented for price prediction and product recommendation tasks. XGBoost is a powerful gradient boosting algorithm that has proven effective in handling large datasets with complex relationships. It enhances the performance of price tracking and recommendations by:

Improved Accuracy: Offering better prediction accuracy for price trends and future product prices.
Efficiency: Handling large datasets and providing faster model training with optimized performance.
Recommendation System: Predicting prices and recommending similar products based on user preferences and historical trends.
These models are implemented alongside basic algorithms such as K-Nearest Neighbors (KNN) for similarity-based recommendations and Linear Regression to predict price changes over time. The next step is to enhance these models with more advanced techniques and fine-tune their performance for better results.

Key Features
Automated Data Collection: Playwright automates the process of scraping product details from Amazon.
Scalable URL Handling: URLs are efficiently cleaned and processed to ensure smooth scraping.
Concurrent Processing: The p-limit library ensures that CSV files are processed concurrently, improving performance.
Clean and Structured Output: The scraped data is saved in a clean CSV format for further analysis.
Feature Engineering: Additional features have been engineered to improve recommendations, such as price trends, product attributes, and price vs. rating correlations.
Model Building: The Random Forest (RF) and XGBoost models have been implemented to predict price trends and recommend similar products based on historical data and features.
Recommendation System: A hybrid approach using KNN, Random Forest, and XGBoost for better product recommendations.
UI Development (Current Stage)
In this phase, the project is focused on building a user interface (UI) to display product details, pricing trends, and recommendations. The goal is to allow users to:

View the scraped product data in an easy-to-read format.

Track price changes over time.

Get product recommendations based on historical data.

Next Steps
Frontend Development: Designing and implementing the UI to display scraped data and recommendations.
User Interaction: Allowing users to search, filter, and view product details.
Price Tracking: Adding features to monitor price trends and notify users about price changes.
Recommendations: Implementing more advanced recommendation algorithms using Random Forest and XGBoost models.
Technology Stack
Playwright: For scraping product details from Amazon.
fast-csv: For efficient CSV file handling.
p-limit: To manage concurrency during data processing.
Node.js: For orchestrating the entire scraping and UI process.
Machine Learning Models:
Random Forest (RF): For predicting prices and analyzing feature importance.
XGBoost: For accurate price prediction and efficient product recommendations.
Frontend Technologies (In Progress): To be updated as development progresses.
Project Documentation
You can view the full project documentation here:
Project Documentation -  https://docs.google.com/document/d/1brUlfKF9rhHoDA6LP8EaX4IJyitOzlJrrohtfZekUQI/edit?usp=sharing

Getting Started
Prerequisites
Node.js installed on your machine.
Familiarity with web scraping, handling CSV data, and machine learning algorithms like Random Forest and XGBoost.
Access to Amazon product URLs for scraping.
Installation
Clone the repository:
git clone https://github.com/users/DikshaGori/projects/1
Install the necessary dependencies:

npm install
Run the scraping pipeline:

npm start
Contributing
Feel free to contribute to the project. Open an issue or submit a pull request with your improvements!
