// Import necessary modules
import { chromium } from "playwright";
import fs from "fs";
import csvParser from "csv-parser";
import fastcsv from "fast-csv";
import pLimit from "p-limit";

// Normalize Best Buy URLs for consistent processing
const normalizeUrl = (url) => {
  try {
    const parsedUrl = new URL(url);
    return `${parsedUrl.origin}${parsedUrl.pathname}`;
  } catch (error) {
    console.error(`Invalid URL: ${url}`);
    return null;
  }
};

// Fetch product price from a Best Buy page
const getPriceFromPage = async (browser, url) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  let price = "Price not found";

  try {
    console.log(`Opening page: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded" });

    // Use Best Buy's price selector
    const priceLocator = page.locator(".priceView-hero-price span");
    if (await priceLocator.count() > 0) {
      price = (await priceLocator.textContent()).trim();
    }
  } catch (error) {
    console.error(`Error fetching price for ${url}: ${error.message}`);
    price = `Error: ${error.message}`;
  } finally {
    await context.close();
  }

  return price;
};

// Process input CSV and write output with extracted prices
const processProductData = async (inputFile, outputFile) => {
  const browser = await chromium.launch({ headless: true });
  const limit = pLimit(3); // Allow 3 concurrent tasks
  const results = [];

  console.log("Starting CSV processing...");

  fs.createReadStream(inputFile)
    .pipe(csvParser())
    .on("data", (row) => {
      const task = limit(async () => {
        const url = row["link"];
        if (!url) {
          console.warn("No URL found in row:", row);
          row["Price"] = "No link provided";
        } else {
          const cleanedUrl = normalizeUrl(url);
          if (cleanedUrl) {
            row["Price"] = await getPriceFromPage(browser, cleanedUrl);
          } else {
            row["Price"] = "Invalid URL";
          }
        }
        results.push(row);
      });

      task.catch((err) => console.error("Error in task:", err));
    })
    .on("end", async () => {
      await Promise.all(limit.activeTasks); // Ensure all tasks are complete
      await browser.close();

      // Write output to CSV
      fastcsv
        .write(results, { headers: true })
        .pipe(fs.createWriteStream(outputFile))
        .on("finish", () => console.log(`Results saved to ${outputFile}`));
    });
};

// Paths for input and output files
const INPUT_FILE = "../data/bestbuy_links.csv";
const OUTPUT_FILE = "bestbuy_price_results.csv";

console.log("Starting Best Buy price extraction...");
processProductData(INPUT_FILE, OUTPUT_FILE);
