import { chromium } from "playwright";
import fs from "fs";
import csvParser from "csv-parser";
import fastcsv from "fast-csv";
import pLimit from "p-limit";

// Standardize Best Buy URLs
const normalizeUrl = (url) => {
  try {
    const { origin, pathname } = new URL(url);
    return `${origin}${pathname}`;
  } catch (err) {
    console.error(`Invalid URL encountered: ${url}`);
    return null;
  }
};

// Retrieve product price from a Best Buy product page
const fetchPrice = async (browser, url) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  let price = "Price not found";

  try {
    console.log(`Navigating to: ${url}`);
    await page.goto(url, { waitUntil: "domcontentloaded" });

    const priceElement = page.locator(".priceView-hero-price span");
    if (await priceElement.count()) {
      price = (await priceElement.textContent()).trim();
    }
  } catch (err) {
    console.error(`Failed to fetch price for ${url}: ${err.message}`);
    price = `Error: ${err.message}`;
  } finally {
    await context.close();
  }

  return price;
};

// Read input CSV, extract prices, and write to output CSV
const extractPricesFromCsv = async (inputPath, outputPath) => {
  const browser = await chromium.launch({ headless: true });
  const concurrencyLimit = pLimit(3);
  const productData = [];

  console.log("Beginning CSV read and processing...");

  fs.createReadStream(inputPath)
    .pipe(csvParser())
    .on("data", (row) => {
      const task = concurrencyLimit(async () => {
        const url = row["link"];

        if (!url) {
          console.warn("Missing URL in row:", row);
          row["Price"] = "No link provided";
        } else {
          const standardizedUrl = normalizeUrl(url);
          row["Price"] = standardizedUrl
            ? await fetchPrice(browser, standardizedUrl)
            : "Invalid URL";
        }

        productData.push(row);
      });

      task.catch((err) => console.error("Task error:", err));
    })
    .on("end", async () => {
      await Promise.all(concurrencyLimit.activeTasks);
      await browser.close();

      fastcsv
        .write(productData, { headers: true })
        .pipe(fs.createWriteStream(outputPath))
        .on("finish", () => console.log(`Prices saved to ${outputPath}`));
    });
};

// Set file paths
const INPUT_FILE = "../data/bestbuy_links.csv";
const OUTPUT_FILE = "bestbuy_price_results.csv";

console.log("Launching Best Buy price extractor...");
extractPricesFromCsv(INPUT_FILE, OUTPUT_FILE);
