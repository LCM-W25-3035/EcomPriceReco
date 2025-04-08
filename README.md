###Ecommerce Product Analysis, Trends, Price Tracking, and Recommendations
Project Overview
This project focuses on collecting and analyzing product data from Amazon, tracking price
fluctuations, and offering product recommendations based on historical trends. The scraping
pipeline is built using Playwright for robust and efficient web scraping. Data is structured and saved
using fast-csv and managed concurrently using the p-limit library. Currently, the project is in the UI
development stage, with feature engineering and machine learning models incorporated to enhance
the recommendation engine and predict price trends using Random Forest (RF) and XGBoost.
Project Board: https://github.com/users/DikshaGori/projects/1
Current Progress
1. Data Collection
- URL Cleaning: Ensures all input URLs are properly formatted to avoid scraping errors.
- Price Extraction: Scrapes key product details such as price, title, category, and ratings from
Amazon product pages.
- CSV Handling: Data is processed and saved in real-time into structured CSV files for analysis.
2. Feature Engineering
- Price History: Tracks product prices over time to identify trends.
- Product Attributes: Includes features like category, title, and ratings for similarity-based
recommendations.
- Time-based Features: Incorporates time of last price update to capture seasonal trends or
promotions.
- Price vs. Rating Correlation: Evaluates the relationship between pricing and user ratings to
enhance recommendations.
3. Model Building
Random Forest (RF):
- Use Case: Price prediction using historical data, ratings, and product attributes.
- Benefits: High accuracy with ensemble learning. Insight into feature importance.
XGBoost:
- Use Case: Price prediction and product recommendation.
- Benefits: High efficiency and scalability. Excellent accuracy on large and complex datasets.
Supports user preference-based recommendations.
Other Algorithms:
- K-Nearest Neighbors (KNN): For similarity-based product recommendations.
- Linear Regression: To forecast price changes over time.
Key Features
- Automated Data Collection
- URL Sanitization
- Concurrent Processing
- Clean Output
- Feature Engineering
- Hybrid Recommendation System
UI Development 
The project is now focused on frontend development to allow users to:
- Visualize product pricing trends.
- Search and filter products.
- Receive product recommendations based on trends and user preferences.
- Frontend Development
- Enhance Recommendation Logic
- Price Tracking Features
- Advanced Search
Technology Stack
- Scraping: Playwright
- Data Handling: fast-csv, p-limit
- Backend: Node.js
- ML Models: Random Forest, XGBoost, KNN, Linear Regression
- Frontend: streamlit UI 
Project Documentation
https://docs.google.com/document/d/1brUlfKF9rhHoDA6LP8EaX4IJyitOzlJrrohtfZekUQI/edit?usp=s
haring
Getting Started
Prerequisites:
- Node.js installed.
- Familiarity with: Web scraping, CSV handling, Machine learning (RF, XGBoost)
Installation:
git clone https://github.com/users/DikshaGori/projects/1
npm install
npm start
Contributing
We welcome contributions! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
