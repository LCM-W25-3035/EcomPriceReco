import { chromium } from 'playwright';
import fs from 'fs';

const newTxtFile = "C:/Users/My/Downloads/Python project 2/Python project/js-script/First-1.txt";
const MAX_CONCURRENT_TABS = 5;

const productUrls = fs.readFileSync(newTxtFile, 'utf-8')
    .split("\n")
    .map(url => url.trim())
    .filter(url => url.length > 0 && url.startsWith("http"));

async function getTextContent(page, selector) {
    try {
        const element = await page.$(selector);
        return element ? (await element.textContent()).trim() : null;
    } catch (e) {
        console.error(`Error with selector ${selector}: ${e.message}`);
        return null;
    }
}

async function cleanAvailabilityText(text) {
    if (!text) return "Unavailable";
    const patterns = [
        "Currently unavailable",
        "We don't know when or if this item will be back in stock",
        "Temporarily out of stock",
        "Out of stock",
    ];
    for (const pattern of patterns) {
        if (text.toLowerCase().includes(pattern.toLowerCase())) return "Currently unavailable";
    }
    return text || "Unavailable";
}

async function scrapeAmazonProduct(context, url) {
    console.log(`Scraping: ${url}`);
    const page = await context.newPage();

    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });

        const productName = await getTextContent(page, "#productTitle");
        const brand = await getTextContent(page, "#bylineInfo");
        const seller = await getTextContent(page, "#sellerProfileTriggerId");
        let inStockText = await getTextContent(page, "#availability");
        inStockText = await cleanAvailabilityText(inStockText);
        const reviewCount = await getTextContent(page, "#acrCustomerReviewText");
        const ratings = await getTextContent(page, ".a-icon-alt");

        const actualPrice = await getTextContent(page, ".a-price.a-text-price[data-a-strike='true'] .a-offscreen");
        let discountedPrice = await getTextContent(page, ".a-price.priceToPay .a-offscreen");

        if (!discountedPrice) {
            const discountedWhole = await getTextContent(page, ".a-price-whole");
            const discountedFraction = await getTextContent(page, ".a-price-fraction");
            discountedPrice = discountedWhole && discountedFraction
                ? `${discountedWhole}.${discountedFraction}`
                : discountedWhole;
        }

        let category = await getTextContent(page, "option[selected]");
        if (category) category = category.trim();

        const purchaseCount = await page.$eval('#social-proofing-faceout-title-tk_bought', el => el.textContent.trim()).catch(() => 'Unavailable');

        await page.close();

        return {
            "Product Name": productName || "N/A",
            "Brand": brand || "N/A",
            "Seller": seller || "N/A",
            "Actual Price": actualPrice || "N/A",
            "Discounted Price": discountedPrice || "N/A",
            "In Stock": inStockText || "N/A",
            "Review Count": reviewCount || "N/A",
            "Ratings": ratings || "N/A",
            "Category": category || "N/A",
            "Purchase Count": purchaseCount || "N/A",
            "URL": url
        };
    } catch (error) {
        console.error(`Error fetching ${url}: ${error.message}`);
        await page.close();
        return null;
    }
}

async function scrapeAllProducts() {
    const browser = await chromium.launch({
        headless: false,
        args: ["--disable-images", "--no-sandbox"],
    });

    const userAgents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        // Add more user agents here if needed
    ];
    const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];

    const context = await browser.newContext({
        userAgent: randomUserAgent,
        viewport: { width: 1280, height: 800 }
    });

    const allProducts = [];
    for (const url of productUrls) {
        const productData = await scrapeAmazonProduct(context, url);
        if (productData) allProducts.push(productData);
    }

    await browser.close();
    return allProducts;
}

function saveToCsv(data, filePath) {
    const header = Object.keys(data[0]).join(',') + '\n';
    const rows = data.map(product =>
        Object.values(product).map(value =>
            `"${value.replace(/"/g, '""')}"`
        ).join(',')
    ).join('\n');
    fs.writeFileSync(filePath, header + rows, 'utf-8');
    console.log(`Scraped data saved to ${filePath}`);
}

(async () => {
    console.time("Scraping Time");
    const allProducts = await scrapeAllProducts();
    console.timeEnd("Scraping Time");

    if (allProducts.length > 0) {
        const csvPath = "C:/Users/My/Downloads/Python project 2/Python project/js-script/Firstone.csv";
        saveToCsv(allProducts, csvPath);
    }
})();
