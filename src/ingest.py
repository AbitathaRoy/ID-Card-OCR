# src/ingest.py

import os
import uuid
import requests

from src.sheet_reader import read_responses
from src.ocr import extract_text
from src.parse import (
    parse_admission_number,
    parse_phone_number,
    parse_name
)
from src.database import init_db, insert_or_update_student

from datetime import date

import re

def extract_drive_file_id(url: str) -> str | None:
    patterns = [
        r"id=([a-zA-Z0-9_-]+)",
        r"/d/([a-zA-Z0-9_-]+)"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def download_id_card(url: str) -> str:
    file_id = extract_drive_file_id(url)
    if not file_id:
        raise ValueError("Could not extract Drive file ID")

    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    os.makedirs("data/raw_images", exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    path = os.path.join("data/raw_images", filename)

    r = requests.get(download_url, timeout=15)
    r.raise_for_status()

    with open(path, "wb") as f:
        f.write(r.content)

    return path


def compute_year_of_study(admission_year: int) -> int:
    """
    Computes year of study using Aug 1 cutoff.
    """
    today = date.today()
    cutoff = date(admission_year, 8, 1)

    delta_years = (today - cutoff).days / 365.25

    year = int(delta_years) + 1
    return min(max(year, 1), 6)

def process_single_submission(row):
    """
    Processes one Google Form response row.
    """

    # -------- Typed (authoritative) data --------
    form_data = {
        "email": row["Email address"],
        "name": row["Name"],
        "course_code": row["Course"],
        "year_of_study": int(row["Year of Study"]),
        "phone": str(row["WhatsApp Number"]),
        "categories_csv": row["What categories would you like to volunteer for"]
    }

    # -------- ID card OCR --------
    image_url = row["ID Card"]
    image_path = download_id_card(image_url)

    try:
        raw_text = extract_text(image_path)
    except Exception as e:
        print(f"OCR failed for {form_data['email']}: {e}")
        raw_text = ""


    admission_info = parse_admission_number(raw_text) or {}
    ocr_data = {
        "name": parse_name(raw_text),
        "admission_no": admission_info.get("admission_no"),
        "phone": parse_phone_number(raw_text)
    }

    # -------- Derived --------
    derived_data = {}
    if admission_info:
        derived_data = {
            "admission_year": admission_info["admission_year"],
            "batch_end_year": admission_info["batch_end_year"],
            "computed_year": compute_year_of_study(
                admission_info["admission_year"]
            )
        }

    # -------- Persist --------
    insert_or_update_student(form_data, ocr_data, derived_data)

def run_pipeline():
    init_db()

    df = read_responses()

    for _, row in df.iterrows():
        try:
            process_single_submission(row)
        except Exception as e:
            print(f"Failed for {row.get('Email address')}: {e}")


if __name__ == "__main__":
    run_pipeline()
