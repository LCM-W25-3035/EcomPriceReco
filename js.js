const { chromium } = require('playwright'); // Import Playwright
const fs = require('fs');

const newTxtFile = "C:/Users/vishn/Downloads/30_lines.txt"; // File with product URLs
const MAX_CONCURRENT_TABS = 5; // Adjust for speed vs. system load

const productUrls = fs.readFileSync(newTxtFile, 'utf-8')
    .split("\n")
    .map(url => url.trim())
    .filter(url => url.length > 0 && url.startsWith("http"));

// Function to validate a URL
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch (err) {
        return false;
    }
}

// Function to extract text safely
async function getTextContent(page, selector) {
    try {
        const element = await page.$(selector);
        return element ? (await element.textContent()).trim() : null;
    } catch (e) {
        return null;
    }
}

// Function to clean availability text
async function cleanAvailabilityText(text) {
    if (!text) return "Unavailable";
    text = text.trim();
    const unavailablePatterns = [
        "Currently unavailable",
        "We don't know when or if this item will be back in stock",
        "Temporarily out of stock",
        "Out of stock",
    ];
    for (const pattern of unavailablePatterns) {
        if (text.toLowerCase().includes(pattern.toLowerCase())) return "Currently unavailable";
    }
    return text || "Unavailable";
}

// Scrape product details
async function scrapeAmazonProduct(context, url) {
    if (!isValidUrl(url)) return null;

    console.log(`Scraping: ${url}`);
    const page = await context.newPage(); // Open a new page within the browser context

    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });

        const productName = await getTextContent(page, "#productTitle");
        const brand = await getTextContent(page, "#bylineInfo");
        const seller = await getTextContent(page, "#sellerProfileTriggerId");
        let inStockText = await getTextContent(page, "#availability");
        inStockText = await cleanAvailabilityText(inStockText);
        const reviewCount = await getTextContent(page, "#acrCustomerReviewText");
        const ratings = await getTextContent(page, ".a-icon-alt");

        let actualPrice = await getTextContent(page, ".a-price.a-text-price .a-offscreen");
        let discountedPrice = await getTextContent(page, ".a-price-whole");
        const discountedPriceFraction = await getTextContent(page, ".a-price-fraction");

        if (discountedPrice && discountedPriceFraction) {
            discountedPrice = `${discountedPrice}.${discountedPriceFraction}`;
        }

        let category = await getTextContent(page, "option[selected]");
        if (category) category = category.trim();

        await page.close(); // Close the page to free up resources

        return {
            "Product Name": productName,
            "Brand": brand,
            "Seller": seller,
            "Actual Price": actualPrice,
            "Discounted Price": discountedPrice,
            "In Stock": inStockText,
            "Review Count": reviewCount,
            "Ratings": ratings,
            "Category": category,
            "URL": url
        };
    } catch (error) {
        console.error(`Error fetching ${url}: ${error.message}`);
        await page.close();
        return null;
    }
}

// Scrape all products using parallel processing
async function scrapeAllProducts() {
    const browser = await chromium.launch({
        headless: true,
        args: ["--disable-images", "--no-sandbox"], // Speed optimization
    });

    const context = await browser.newContext({
        userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        viewport: { width: 1280, height: 800 }
    });

    const allProducts = [];
    const tasks = [];

    for (let i = 0; i < Math.min(MAX_CONCURRENT_TABS, productUrls.length); i++) {
        tasks.push(context.newPage());
    }

    let index = 0;
    while (index < productUrls.length) {
        const pagePromises = tasks.map(async (page, tabIndex) => {
            if (index < productUrls.length) {
                const url = productUrls[index++];
                const productData = await scrapeAmazonProduct(context, url);
                if (productData) allProducts.push(productData);
            }
        });

        await Promise.all(pagePromises);
    }

    await browser.close();
    return allProducts;
}

// Save data to CSV
function saveToCsv(data, filePath) {
    const header = Object.keys(data[0]).join(',') + '\n';
    const rows = data.map(product => Object.values(product).map(value => `"${value}"`).join(',')).join('\n');
    fs.writeFileSync(filePath, header + rows, 'utf-8');
    console.log(`Scraped data saved as ${filePath}`);
}

// Run the scraper
(async () => {
    console.time("Scraping Time");
    const allProducts = await scrapeAllProducts();
    console.timeEnd("Scraping Time");

    if (allProducts.length > 0) {
        const csvPath = "C:/Users/vishn/Downloads/testing.txt.csv";
        saveToCsv(allProducts, csvPath);
    }
})();
