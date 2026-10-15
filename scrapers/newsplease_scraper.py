import csv
from pathlib import Path
from newsplease import NewsPlease

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

    output_file = output_dir / f"newsplease_{article_id:02d}.txt"

    # Remove old result to avoid outdated extractions
    output_file.unlink(missing_ok=True)

    print(f"Scraping article {article_id}: {source}")

    try:
        # Download and extract article automatically
        article = NewsPlease.from_url(url)

        # Check if extraction failed
        if article is None or isinstance(article, dict):
            print("  Article extraction failed!")
            continue

        # Extract main article text
        text = (article.maintext or "").strip()

        if not text:
            print("  No article text extracted!")
            continue

        # Save extracted text
        output_file.write_text(text, encoding="utf-8")

        print(f"  Saved {len(text.split())} words")

    except Exception as error:
        print(f"  Error: {error}")

print("Finished scraping!")