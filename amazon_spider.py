import scrapy
from scrapy.http import Request
import random

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.in"]
    
    # Amazon Electronics category URL
    start_urls = [
        "https://www.amazon.in/s?k=electronics"
    ]

    # Function to generate random user-agent headers
    def get_headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36",
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "en-US,en;q=0.9",
        }

    # Start the scraping process
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=self.get_headers())

    def parse(self, response):
        products = response.xpath("//div[@data-component-type='s-search-result']")

        for product in products:
            yield {
                "name": product.xpath(".//span[@class='a-size-medium a-color-base a-text-normal']/text()").get(),
                "price": product.xpath(".//span[@class='a-price-whole']/text()").get(),
                "link": response.urljoin(product.xpath(".//a[@class='a-link-normal s-no-outline']/@href").get())
            }
        
        # Follow pagination if available
        next_page = response.xpath("//a[contains(@aria-label, 'Next')]/@href").get()
        if next_page:
            yield response.follow(next_page, headers=self.get_headers(), callback=self.parse)
