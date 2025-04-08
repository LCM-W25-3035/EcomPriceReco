const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

async function scrapeAmazonLinks(url) {
    try {
        // Fetch the HTML from the URL
        const { data } = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            },
        });

        // Load the HTML into Cheerio
        const $ = cheerio.load(data);

        // Initialize an array to hold product links
        let links = [];

        // Select each product entry
        $('[data-component-type="s-search-result"]').each((index, element) => {
            let link = $(element).find('a.a-link-normal').attr('href');
            if (link) {
                links.push(`https://www.amazon.in${link}`);
            }
        });

        // Define the file path
        const filePath = "C:/Users/vishn/Downloads/new10000.csv";

        // Ensure links were found before writing
        if (links.length > 0) {
            fs.appendFileSync(filePath, links.join('\n') + '\n', 'utf8');
            console.log(`Links from page saved to '${filePath}'`);
        } else {
            console.log('No product links found on this page.');
        }
    } catch (error) {
        console.error("Error fetching the page:", error);
    }
}

// Loop through multiple pages
const BASE_URL = "https://www.amazon.in/s?i=electronics&ref=nb_sb_noss&page=";
const totalPages =5  // You can change this to loop through more pages

for (let page = 1; page <= totalPages; page++) {
    const url = `${BASE_URL}${page}`;
    scrapeAmazonLinks(url);
}
