import csv
from pathlib import Path

import scrapy
from scrapy.crawler import CrawlerProcess


INPUT_FILE = Path("data/test_articles.csv")
OUTPUT_DIR = Path("data/extracted")

ARTICLE_SELECTORS = {
    "The Guardian": "#maincontent .article-body-commercial-selector",
    "Euronews": ".c-article-content",
    "TechCrunch": ".entry-content",
    "Deutsche Welle": "article",
    "France 24": "article",
}


class NewsSpider(scrapy.Spider):
    name = "news_spider"

    custom_settings = {
        "LOG_LEVEL": "WARNING",
        "DOWNLOAD_TIMEOUT": 15,
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1,
        "HTTPERROR_ALLOWED_CODES": [403],
    }

    async def start(self):
        # Read test articles
        with open(INPUT_FILE, newline="", encoding="utf-8") as file:
            articles = list(csv.DictReader(file))

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        for article in articles:
            article_id = int(article["id"])
            source = article["source"]
            url = article["url"]

            # Remove previous result
            output_file = OUTPUT_DIR / f"scrapy_{article_id:02d}.txt"
            output_file.unlink(missing_ok=True)

            print(f"Scraping article {article_id}: {source}", flush=True)

            yield scrapy.Request(
                url=url,
                callback=self.parse_article,
                errback=self.handle_error,
                cb_kwargs={
                    "article_id": article_id,
                    "source": source,
                },
            )

    def parse_article(self, response, article_id, source):
        if response.status != 200:
            print(f"  Article {article_id}: HTTP {response.status}")
            return

        # Select article body based on website HTML structure
        selector = ARTICLE_SELECTORS.get(source, "article")
        article = response.css(selector)

        if not article:
            print(f"  Article {article_id}: Article body not found!")
            return

        # Extract all text inside each paragraph, including nested elements
        paragraphs = article.css("p")

        extracted_paragraphs = []

        for paragraph in paragraphs:
            parts = paragraph.xpath(".//text()").getall()
            text = " ".join(" ".join(parts).split())

            if text:
                extracted_paragraphs.append(text)

        if not extracted_paragraphs:
            print(f"  Article {article_id}: No text extracted!")
            return

        text = "\n\n".join(extracted_paragraphs)

        # Save extracted article
        output_file = OUTPUT_DIR / f"scrapy_{article_id:02d}.txt"
        output_file.write_text(text, encoding="utf-8")

        print(f"  Article {article_id}: Saved {len(text.split())} words")

    def handle_error(self, failure):
        print(f"  Request failed: {failure.value}")


if __name__ == "__main__":
    print("Starting Scrapy...", flush=True)

    process = CrawlerProcess(
        settings={
            "LOG_LEVEL": "WARNING",
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        }
    )

    process.crawl(NewsSpider)
    process.start()

    print("Scrapy finished!", flush=True)