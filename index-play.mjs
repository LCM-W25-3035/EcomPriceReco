import { chromium } from "playwright";
import fs from "fs";
import csv from "csv-parser";
import fastcsv from "fast-csv";
import pLimit from "p-limit";

// Function to clean the URL
function cleanUrl(url) {
  const urlObj = new URL(url);
  const path = urlObj.pathname.split("/ref")[0];
  urlObj.pathname = path;
  return urlObj.toString();
}

// Function to extract the price from an Amazon product page using Playwright
async function extractPriceWithPlaywright(url, browser) {
  const context = await browser.newContext();
  const page = await context.newPage();
  let price = "Error: Price not found";

  try {
    await page.goto(url, { waitUntil: "domcontentloaded" });
    const priceElement = await page.locator(".a-price-whole").first();
    const priceElement2 = await page.locator(".a-offscreen").first();

    if (await priceElement.count() > 0) {
      console.log("Price Element found for ",url)
      price = await priceElement.textContent();
      price = price.trim();
      console.log(price)
    }
    if(await priceElement2.count() > 0){
        console.log("Price Element found for ",url)
      price = await priceElement2.textContent();
      price = price.trim();
      console.log(price)
    }
  } catch (err) {
    console.log("Error in price")
    price = `Error: ${err.message}`;
  }

  await context.close();
  return price;
}

// Function to process CSV, extract price, and write results to an output CSV
async function processCsv(inputFile, outputFile) {
  const inputStream = fs.createReadStream(inputFile);
  const outputStream = fs.createWriteStream(outputFile);
  const results = [];
  const limit = pLimit(5); // Limit concurrency to 5

  const browser = await chromium.launch({ headless: true });
  console.log("Browser Launched")

  const tasks = [];
  inputStream
    .pipe(csv())
    .on("data", (row) => {
      const task = limit(async () => {
        const url = row["link"];
        if (!url) {
            console.log("No URL");
            row["Price"] = "No link provided";
        } else {
          const cleanedUrl = cleanUrl(url);
        //   console.log(cleanedUrl);
          row["Price"] = await extractPriceWithPlaywright(cleanedUrl, browser);
        }
        results.push(row);
      });
      tasks.push(task);
    })
    .on("end", async () => {
      await Promise.all(tasks); // Wait for all tasks to complete
      await browser.close();

      fastcsv
        .write(results, { headers: true })
        .pipe(outputStream)
        .on("finish", () => {
          console.log(`Processing complete. Results written to ${outputFile}`);
        });
    });
}

const inputCsv = "../data/merge.csv"; // Replace with your input CSV file name
const outputCsv = "output_data2.csv"; // Replace with your desired output CSV file name

console.log("Processing started. This may take a while for large datasets...");
processCsv(inputCsv, outputCsv);
