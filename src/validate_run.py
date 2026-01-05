from src.database import fetch_all_students_as_dict
from src.validate import validate_record


def run_validation():
    rows = fetch_all_students_as_dict()

    for row in rows:
        scores = validate_record(row)
        print(
            row["email"],
            "→",
            scores
        )


if __name__ == "__main__":
    run_validation()
