import { chromium } from 'playwright'; // Import Playwright
import fs from 'fs';

const newTxtFile = "C:/Users/My/Downloads/Python project 2/Python project/js-script/newurls.txt"; // File with product URLs
const outputCsvFile = "C:/Users/My/Downloads/Python project 2/Python project/js-script/newurls12.csv"; // Output CSV file
const MAX_CONCURRENT_TABS = 5; // Adjust for speed vs. system load

const productUrls = fs.readFileSync(newTxtFile, 'utf-8')
    .split("\n")
    .map(url => url.trim())
    .filter(url => url.length > 0 && url.startsWith("http"));

// Initialize CSV with headers if file doesn't exist
if (!fs.existsSync(outputCsvFile)) {
    fs.writeFileSync(outputCsvFile, 'Product Name,Brand,Seller,Actual Price,Discounted Price,In Stock,Review Count,Ratings,Category,Purchase Count,Product Details,URL\n', 'utf-8');
}

async function scrapeAmazonProduct(context, url, index, total) {
    console.log(`📡 [${index + 1}/${total}] Scraping: ${url}`);
    const page = await context.newPage();
    
    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

        const productName = await page.textContent("#productTitle").catch(() => "N/A");
        const brand = await page.textContent("#bylineInfo").catch(() => "N/A");
        const seller = await page.textContent("#sellerProfileTriggerId").catch(() => "N/A");
        const inStockText = await page.textContent("#availability").catch(() => "Unavailable");
        const reviewCount = await page.textContent("#acrCustomerReviewText").catch(() => "N/A");
        const ratings = await page.textContent(".a-icon-alt").catch(() => "N/A");
        const purchaseCount = await page.textContent("#social-proofing-faceout-title-tk_bought").catch(() => "Unavailable");
        
        let actualPrice = await page.textContent(".a-price.a-text-price[data-a-strike='true'] .a-offscreen").catch(() => "N/A");
        let discountedPrice = await page.textContent(".a-price.priceToPay .a-offscreen").catch(() => "N/A");
        let category = await page.textContent("option[selected]").catch(() => "N/A");

        const productData = {
            "Product Name": productName.trim(),
            "Brand": brand.trim(),
            "Seller": seller.trim(),
            "Actual Price": actualPrice.trim(),
            "Discounted Price": discountedPrice.trim(),
            "In Stock": inStockText.trim(),
            "Review Count": reviewCount.trim(),
            "Ratings": ratings.trim(),
            "Category": category.trim(),
            "Purchase Count": purchaseCount.trim(),
            "Product Details": url
        };

        saveToCsv(productData);
        console.log(`✅ [${index + 1}/${total}] Saved: ${productName.trim()}`);

        await page.close();
        return productData;
    } catch (error) {
        console.error(`❌ [${index + 1}/${total}] Error fetching ${url}: ${error.message}`);
        await page.close();
        return null;
    }
}

function saveToCsv(productData) {
    const row = Object.values(productData).map(value => `"${(value ?? "").replace(/"/g, '""')}"`).join(',') + '\n';
    fs.appendFileSync(outputCsvFile, row, 'utf-8');
}

async function scrapeAllProducts() {
    console.log(`🚀 Starting scraping of ${productUrls.length} products...`);
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    
    let scrapedCount = 0;
    const tasks = productUrls.map((url, index) => 
        scrapeAmazonProduct(context, url, index, productUrls.length).then(result => {
            if (result) scrapedCount++;
        })
    );

    await Promise.all(tasks);
    await browser.close();

    console.log(`🎉 Scraping complete! Successfully scraped ${scrapedCount}/${productUrls.length} products.`);
}

(async () => {
    console.time("⏳ Scraping Time");
    await scrapeAllProducts();
    console.timeEnd("⏳ Scraping Time");
})();
