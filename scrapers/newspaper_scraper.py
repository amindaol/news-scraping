import csv
from pathlib import Path
from newspaper import Article

# Paths
input_file = Path("data/test_articles.csv")
output_dir = Path("data/extracted")
output_dir.mkdir(parents=True, exist_ok=True)

# Read articles from CSV
with open(input_file, newline="", encoding="utf-8") as file:
    articles = list(csv.DictReader(file))

# Scrape each article
for article_info in articles:
    article_id = int(article_info["id"])
    source = article_info["source"]
    url = article_info["url"]

    output_file = output_dir / f"newspaper_{article_id:02d}.txt"

    # Remove old result to avoid outdated extractions
    output_file.unlink(missing_ok=True)

    print(f"Scraping article {article_id}: {source}")

    try:
        # Download and parse article
        article = Article(url)
        article.download()
        article.parse()

        # Extract article text
        text = article.text.strip()

        if not text:
            print("  No article text extracted!")
            continue

        # Save extracted text
        output_file.write_text(text, encoding="utf-8")

        print(f"  Saved {len(text.split())} words")

    except Exception as error:
        print(f"  Error: {error}")

print("Finished scraping!")