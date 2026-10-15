
import csv
import re
from pathlib import Path
from difflib import SequenceMatcher
from rapidfuzz.distance import Levenshtein

# Folders
ground_truth_dir = Path("data/ground_truth")
extracted_dir = Path("data/extracted")
results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

methods = [
    "beautifulsoup",
    "newspaper",
    "newsplease",
    "scrapy",
    "selenium",
]


def normalize(text):
    # Remove differences in whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


results = []

for article_id in range(1, 11):
    # Ground truth files: article_1.txt, article_2.txt, etc.
    truth_file = ground_truth_dir / f"article_{article_id}.txt"

    if not truth_file.exists():
        print(f"Missing ground truth: {truth_file}")
        continue

    truth = normalize(truth_file.read_text(encoding="utf-8"))

    for method in methods:
        # Extracted files: newspaper_01.txt, newspaper_02.txt, etc.
        extracted_file = extracted_dir / f"{method}_{article_id:02d}.txt"

        if not extracted_file.exists():
            results.append({
                "article_id": article_id,
                "method": method,
                "status": "failed",
                "levenshtein": "",
                "sequence_matcher": "",
                "ground_truth_words": len(truth.split()),
                "extracted_words": 0,
            })
            continue

        extracted = normalize(
            extracted_file.read_text(encoding="utf-8")
        )

        if not extracted:
            status = "failed"
            levenshtein_score = ""
            sequence_score = ""
        else:
            status = "extracted"
            levenshtein_score = round(
                Levenshtein.normalized_similarity(truth, extracted), 4
            )
            sequence_score = round(
                SequenceMatcher(None, truth, extracted, autojunk=False).ratio(),
                4
            )

        results.append({
            "article_id": article_id,
            "method": method,
            "status": status,
            "levenshtein": levenshtein_score,
            "sequence_matcher": sequence_score,
            "ground_truth_words": len(truth.split()),
            "extracted_words": len(extracted.split()),
        })

# Save detailed results
output_file = results_dir / "evaluation.csv"

with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"Saved results to {output_file}")

# Print summary
print("\nEVALUATION SUMMARY")
print("-" * 95)

for method in methods:
    method_results = [r for r in results if r["method"] == method]
    successful = [r for r in method_results if r["status"] == "extracted"]

    success_rate = len(successful) / len(method_results)

    avg_lev = (
        sum(r["levenshtein"] for r in successful) / len(successful)
        if successful else 0
    )

    avg_seq = (
        sum(r["sequence_matcher"] for r in successful) / len(successful)
        if successful else 0
    )

    # Failed extractions count as zero
    overall_lev = (
        sum(r["levenshtein"] for r in successful) / len(method_results)
    )

    print(
        f"{method:15} "
        f"Success: {success_rate:.0%}  "
        f"Avg similarity: {avg_lev:.3f}  "
        f"Overall score: {overall_lev:.3f}"
    )
