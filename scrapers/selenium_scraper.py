import csv
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


# Paths
input_file = Path("data/test_articles.csv")
output_dir = Path("data/extracted")
output_dir.mkdir(parents=True, exist_ok=True)

# CSS selectors based on website HTML structure
selectors = {
    "The Guardian": "#maincontent .article-body-commercial-selector",
    "Euronews": ".c-article-content",
    "TechCrunch": ".entry-content",
    "Deutsche Welle": "article",
    "France 24": "article",
}

# Configure headless Chrome
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

# Read articles
with open(input_file, newline="", encoding="utf-8") as file:
    articles = list(csv.DictReader(file))

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(30)

try:
    for article in articles:
        article_id = int(article["id"])
        source = article["source"]
        url = article["url"]

        output_file = output_dir / f"selenium_{article_id:02d}.txt"

        # Remove old extraction result
        output_file.unlink(missing_ok=True)

        print(f"Scraping article {article_id}: {source}", flush=True)

        try:
            # Open website
            driver.get(url)

            if source == "Deutsche Welle":
                elements = driver.find_elements(By.CSS_SELECTOR, "article")

                print(f"Found {len(elements)} article elements")

                for i, element in enumerate(elements):
                    print(
                        f"Article element {i}: "
                        f"{len(element.text.split())} words"
                    )

            # Wait until article paragraphs contain text
            selector = selectors.get(source, "article")

            def article_has_text(driver):
                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector
                )

                for element in elements:
                    paragraphs = element.find_elements(
                        By.TAG_NAME,
                        "p"
                    )

                    if any(p.text.strip() for p in paragraphs):
                        return element

                return False

            article_element = WebDriverWait(
                driver, 15
            ).until(article_has_text)

            # Extract paragraphs
            paragraphs = article_element.find_elements(
                By.TAG_NAME,
                "p"
            )

            extracted_paragraphs = [
                p.text.strip()
                for p in paragraphs
                if p.text.strip()
            ]

            text = "\n\n".join(extracted_paragraphs)

            if not text:
                print("  No text extracted!")
                continue

            # Save extracted text
            output_file.write_text(
                text,
                encoding="utf-8"
            )

            print(f"  Saved {len(text.split())} words")

        except TimeoutException:
            print(
                f"  Article {article_id}: "
                "Timed out waiting for article content"
            )

        except Exception as error:
            print(
                f"  Article {article_id}: "
                f"{type(error).__name__}: {error}"
            )

finally:
    driver.quit()

print("Finished scraping!")