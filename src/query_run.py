# src/query_run.py

from src.query import (
    get_unallocated,
    get_candidates,
    allocate_student
)


def demo():
    print("\n--- Unallocated volunteers ---")
    for row in get_unallocated():
        print(row["email"], row["typed_categories"])

    print("\n--- High-confidence Hackathon volunteers ---")
    candidates = get_candidates("Hackathon", min_confidence=0.85)

    for row, scores in candidates:
        print(
            row["email"],
            row["typed_year_of_study"],
            f"confidence={scores['overall_confidence']:.2f}"
        )

    if candidates:
        chosen = candidates[0][0]
        print(f"\nAllocating {chosen['email']} to Hackathon Core Team")
        allocate_student(chosen["email"], "Hackathon Core Team")


if __name__ == "__main__":
    demo()
