import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import csv from "csv-parser";
import fastcsv from "fast-csv";
import { cleanUrl } from "./utils/helpers.js";
import { extractAmazonProductInfo } from "./utils/helpers.js";

// Generate human-readable output file name with timestamp
const getTimestamp = () => {
  const now = new Date();
  const date = now.toISOString().split('T')[0];
  const time = now.toISOString().split('T')[1].split('.')[0];
  return `${date}_${time.replace(/:/g, '-')}`;
};

// Function to add random delay between requests
const randomDelay = (min, max) => {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise(resolve => setTimeout(resolve, delay));
};

// Function to process a single CSV file
async function processCsv(inputFile, outputCsv) {
  return new Promise(async (resolve, reject) => {
    try {
      console.log(`\n📢 Processing started for ${inputFile} at ${new Date().toLocaleString()}...`);
      console.log(`📄 Output file: ${outputCsv}`);

      const browser = await chromium.launch({
        headless: false,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--disable-software-rasterizer',
          '--disable-extensions'
        ]
      });

      console.log("🚀 Browser Launched!");

      let processedCount = 0;
      const rows = [];

      // First, read all rows into memory
      await new Promise((resolveRead, rejectRead) => {
        fs.createReadStream(inputFile)
          .pipe(csv())
          .on('data', (row) => rows.push(row))
          .on('end', resolveRead)
          .on('error', rejectRead);
      });

      console.log(`📊 Total rows to process: ${rows.length}`);

      // Open the CSV stream once before processing all rows
      const csvStream = fs.createWriteStream(outputCsv, { flags: 'a' });
      const writer = fastcsv.format({ headers: processedCount === 0 });

      writer.pipe(csvStream);

      // Process rows one at a time with delay
      for (const row of rows) {
        try {
          const url = row["link"];
          if (!url) {
            console.warn("⚠️ No URL found for a row.");
            row["Title"] = "No link provided";
            row["Price"] = "N/A";
            row["Availability"] = "N/A";
            row["Rating"] = "N/A";
            row["Total Reviews"] = "N/A";
            row["Description"] = "N/A";
            row["DiscountPrice"] = "N/A";
            row["ActualPriceCategory"] = "N/A";
          } else {
            const cleanedUrl = cleanUrl(url);
            console.log(`🔍 Fetching details for: ${cleanedUrl}`);

            const productInfo = await extractAmazonProductInfo(cleanedUrl, browser);

            row["Title"] = productInfo.title || "N/A";  // Title will be fetched and assigned
            row["Price"] = productInfo.price || "N/A";
            row["Availability"] = productInfo.availability || "N/A";
            row["Rating"] = productInfo.rating || "N/A";
            row["Total Reviews"] = productInfo.totalReviews || "N/A";
            row["Description"] = productInfo.description || "N/A";
            row["DiscountPrice"] = productInfo.discountPrice || "N/A";  // New field for discount price
            row["ActualPriceCategory"] = productInfo.actualPriceCategory || "N/A";  // New field for actual price category
          }

          // Write row to the CSV stream
          writer.write({
            Title: row["Title"],   // Ensure you're using row["Title"] for the output
            Link: row["link"],
            Category: row["sub_category"],
            Price: row["Price"],
            Availability: row["Availability"],
            Rating: row["Rating"],
            TotalReviews: row["Total Reviews"],
            Description: row["Description"],
            DiscountPrice: row["DiscountPrice"],  // Writing discount price to CSV
            ActualPriceCategory: row["ActualPriceCategory"],  // Writing actual price category to CSV
          });

          processedCount++;
          console.log(`✅ Processed ${processedCount}/${rows.length} rows...`);

            // Add random delay between requests
            console.log('⏳ Adding delay before next request...');
            await randomDelay(2000, 5000);
        } catch (error) {
          console.error(`❌ Error processing row: ${error.message}`);
        }
      }

      // Close the writer once all rows are processed
      writer.end();
      await new Promise(resolve => csvStream.on('finish', resolve));

      await browser.close();
      console.log(`🎉 Processing complete! ✅ Total records processed: ${processedCount}`);
      console.log(`📄 Output saved at: ${outputCsv}`);
      resolve();
    } catch (error) {
      reject(error);
    }
  });
}

// Function to process all CSV files in the "data" folder
async function processAllCsvFiles() {
  try {
    const outputCsv = `./output/product_data_${getTimestamp()}.csv`;
    const __dirname = path.dirname(new URL(import.meta.url).pathname);
    const dataFolder = path.join(__dirname, "data");

    if (!fs.existsSync(dataFolder)) {
      throw new Error(`Data folder not found: ${dataFolder}`);
    }

    const files = fs.readdirSync(dataFolder);
    const csvFiles = files.filter(file => file.endsWith(".csv"));

    if (csvFiles.length === 0) {
      console.log("No CSV files found in the data folder");
      return;
    }

    console.log(`Found ${csvFiles.length} CSV files to process`);

    for (const csvFile of csvFiles) {
      try {
        const inputFile = path.join(dataFolder, csvFile);
        console.log(`Processing: ${csvFile}`);
        await processCsv(inputFile, outputCsv);
        console.log(`✅ Completed processing: ${csvFile}`);
      } catch (csvError) {
        console.error(`❌ Error processing ${csvFile}:`, csvError);
      }
    }

    console.log(`✅ All CSV files processed. Output saved to: ${outputCsv}`);
  } catch (error) {
    console.error("❌ Error in processAllCsvFiles:", error);
    throw error;
  }
}

async function processSpecificCsvFiles() {
  const outputCsv = `./output/product_data_${getTimestamp()}.csv`;
  const inputFile = './newurls.csv';
  await processCsv(inputFile, outputCsv);
}

// Start processing Specific CSV files
processSpecificCsvFiles().catch(err => console.error(`❌ Error processing files: ${err.message}`));

// Start processing all CSV files in the "data" folder
//Uncomment the below line to process all CSV files and comment the above line 174
// processAllCsvFiles().catch(err => console.error(`❌ Error processing files: ${err.message}`));
