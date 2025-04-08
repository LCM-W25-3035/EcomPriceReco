const puppeteer = require("puppeteer");
const fs = require("fs");
const csv = require("csv-parser");
const fastcsv = require("fast-csv");

// Function to clean the URL
function cleanUrl(url) {
  const urlObj = new URL(url);
  const path = urlObj.pathname.split("/ref")[0];
  urlObj.pathname = path;
  return urlObj.toString();
}

// Function to extract the price from an Amazon product page using Puppeteer
async function extractPriceWithPuppeteer(url) {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/Applications/Chromium.app/Contents/MacOS/Chromium' // Adjust path if needed
  });
  const page = await browser.newPage();
  let price = "Error: Price not found";
  
  try {
    await page.goto(url, { waitUntil: "domcontentloaded" });
    const priceElement = await page.$(".a-price-whole");
    if (priceElement) {
      price = await page.evaluate(el => el.textContent.trim(), priceElement);
    }
  } catch (err) {
    price = `Error: ${err.message}`;
  }
  
  await browser.close();
  return price;
}

// Function to process CSV, extract price, and write results to an output CSV
async function processCsv(inputFile, outputFile) {
  const inputStream = fs.createReadStream(inputFile);
  const outputStream = fs.createWriteStream(outputFile);
  const results = [];
  
  inputStream
    .pipe(csv())
    .on("data", async (row) => {
      const url = row["link"];
      if (!url) {
        row["Price"] = "No link provided";
      } else {
        const cleanedUrl = cleanUrl(url);
        row["Price"] = await extractPriceWithPuppeteer(cleanedUrl);
      }
      results.push(row);
    })
    .on("end", () => {
      fastcsv
        .write(results, { headers: true })
        .pipe(outputStream)
        .on("finish", () => {
          console.log(`Processing complete. Results written to ${outputFile}`);
        });
    });
}

const inputCsv = "../data/All-Electronics.csv"; // Replace with your input CSV file name
const outputCsv = "output_data.csv"; // Replace with your desired output CSV file name

console.log("Processing started. This may take a while for large datasets...");
processCsv(inputCsv, outputCsv);
