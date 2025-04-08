const fs = require('fs');
const puppeteer = require('puppeteer'); // Assuming you're using Puppeteer for scraping

async function getTextContent(page, selector) {
    const element = await page.$(selector);
    if (element) {
        return await page.evaluate(el => el.textContent.trim(), element);
    }
    return null; // Return null if the element is not found
}

async function getPrice(page, asin) {
    try {
        const url = `https://www.amazon.com/dp/${asin}`;
        await page.goto(url, { waitUntil: 'domcontentloaded' });

        // Check if the page title contains 'Amazon'
        const pageTitle = await page.title();
        if (!pageTitle.includes("Amazon")) {
            console.log(`Failed to load the product page for ASIN: ${asin}`);
            return 'Error loading page';
        }

        // Wait for the price element to appear
        await page.waitForSelector('.a-price-whole', { timeout: 5000 });

        // Fetch the price components from the page
        const discountedPrice = await getTextContent(page, ".a-price-whole");
        const discountedPriceFraction = await getTextContent(page, ".a-price-fraction");

        if (discountedPrice && discountedPriceFraction) {
            const fullPrice = `${discountedPrice}.${discountedPriceFraction}`;
            console.log(`Price for ASIN ${asin}: $${fullPrice}`);
            return fullPrice;
        } else {
            console.log(`Price not found for ASIN ${asin}`);
            return 'Price not available';
        }
    } catch (error) {
        console.error(`Error fetching price for ASIN ${asin}:`, error);
        return 'Error fetching price';
    }
}

async function updatePricesFromFile() {
    // Path to the .txt file containing ASINs
    const filePath = 'C:/Users/vishn/Documents/url500.txt';

    // Read ASINs from the .txt file
    const asins = fs.readFileSync(filePath, 'utf-8').split('\n').map(line => line.trim()).filter(line => line);

    // Launch Puppeteer browser instance
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Loop through each ASIN in the text file
    for (let asin of asins) {
        console.log(`Fetching price for ASIN: ${asin}...`);

        // Fetch the price using the getPrice function
        const price = await getPrice(page, asin);

        // Display the price in the console
        console.log(`Price for ASIN ${asin}: ${price}\n`);
    }

    // Close the Puppeteer browser
    await browser.close();
}

// Call the function to update the prices
updatePricesFromFile().catch(console.error);
