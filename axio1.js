const axios = require("axios");
const fakeUserAgent = require("fake-useragent");

const scrapeAmazonProduct = async (asin) => {
  const url = `https://www.amazon.in/dp/${asin}`;
  
  const headers = {
    "User-Agent": fakeUserAgent(),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.amazon.in/"
  };
  
  try {
    const response = await axios.get(url, { headers });

    if (response.status === 200) {
      console.log("Page fetched successfully!");
      // Process the response here, e.g., extract product info
    } else {
      console.log(`❌ Failed to fetch product: HTTP ${response.status}`);
    }
  } catch (error) {
    console.error(`⚠️ Error fetching product: ${error.response ? error.response.status : error.message}`);
  }
};

// Example usage
scrapeAmazonProduct("B096MSW6CT");  // Replace with your ASIN
