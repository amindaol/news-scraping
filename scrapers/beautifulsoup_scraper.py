import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# Paths
input_file = Path("data/test_articles.csv")
output_dir = Path("data/extracted")
output_dir.mkdir(parents=True, exist_ok=True)

# CSS selectors based on the HTML structure of each website
article_selectors = {
    "The Guardian": "#maincontent .article-body-commercial-selector",
    "Euronews": ".c-article-content",
    "TechCrunch": ".entry-content",
    "France 24": "article",
    "Deutsche Welle": "article",
}

# Possible newsletter and promotional elements
promotion_selectors = (
    '[data-component="newsletter-signup"], '
    '[data-gu-name="newsletter-signup"], '
    '.newsletter-signup'
)

# Read articles from CSV
with open(input_file, newline="", encoding="utf-8") as file:
    articles = list(csv.DictReader(file))

# Scrape each article
for article_info in articles:
    article_id = int(article_info["id"])
    source = article_info["source"]
    url = article_info["url"]

    output_file = output_dir / f"beautifulsoup_{article_id:02d}.txt"

    # Remove old result to avoid using outdated extractions
    output_file.unlink(missing_ok=True)

    print(f"Scraping article {article_id}: {source}")

    try:
        # Download HTML
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find article content using website-specific selectors
        selector = article_selectors.get(source, "article")
        article = soup.select_one(selector)

        if article is None:
            print("  Article body not found!")
            continue

        # Remove newsletter and promotional elements
        promotions = article.select(promotion_selectors)

        for element in promotions:
            element.decompose()

        print(f"  Removed {len(promotions)} promotional elements")

        # Extract paragraphs
        paragraphs = article.find_all("p")

        text = "\n\n".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
            if p.get_text(strip=True)
        )

        if not text.strip():
            print("  No article text extracted!")
            continue

        # Save extracted text
        output_file.write_text(text, encoding="utf-8")

        print(f"  Saved {len(paragraphs)} paragraphs")
        print(f"  Extracted {len(text.split())} words")

    except requests.RequestException as error:
        print(f"  Request error: {error}")

    except Exception as error:
        print(f"  Unexpected error: {error}")

print("Finished scraping!")