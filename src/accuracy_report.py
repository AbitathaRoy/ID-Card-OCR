from src.database import fetch_all_students_as_dict
from src.validate import validate_record
import statistics


def generate_accuracy_report(threshold=0.8):
    rows = fetch_all_students_as_dict()

    if not rows:
        print("No data available.")
        return

    name_scores = []
    phone_scores = []
    year_scores = []
    overall_scores = []
    low_confidence = []

    for row in rows:
        scores = validate_record(row)

        name_scores.append(scores["name_score"])
        phone_scores.append(scores["phone_score"])
        year_scores.append(scores["year_score"])
        overall_scores.append(scores["overall_confidence"])

        if scores["overall_confidence"] < threshold:
            low_confidence.append(row["email"])

    print("\n===== OCR ACCURACY REPORT =====\n")

    print(f"Total records           : {len(rows)}\n")

    print("Name similarity:")
    print(f"  Mean                  : {statistics.mean(name_scores):.3f}")
    print(f"  Min / Max             : {min(name_scores):.3f} / {max(name_scores):.3f}\n")

    print("Phone exact match:")
    print(f"  Accuracy              : {sum(phone_scores)/len(phone_scores):.2%}\n")

    print("Year of study exact match:")
    print(f"  Accuracy              : {sum(year_scores)/len(year_scores):.2%}\n")

    print("Overall confidence:")
    print(f"  Mean                  : {statistics.mean(overall_scores):.3f}")
    print(f"  Min / Max             : {min(overall_scores):.3f} / {max(overall_scores):.3f}\n")

    print(f"Low-confidence (<{threshold}) records:")
    for email in low_confidence:
        print(f"  - {email}")

    print("\n===============================\n")


if __name__ == "__main__":
    generate_accuracy_report()
