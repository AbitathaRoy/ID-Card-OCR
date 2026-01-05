# src/parse.py

import re
from src.config import ADMISSION_REGEX, PHONE_REGEX


def parse_admission_number(text: str) -> dict | None:
    match = re.search(ADMISSION_REGEX, text)
    if not match:
        return None

    admission_no = match.group()

    # Example: BTH23-27@152304
    course_code = admission_no[:3]
    years_part = admission_no[3:8]   # "23-27"

    start_year = 2000 + int(years_part[:2])
    end_year = 2000 + int(years_part[3:])

    return {
        "admission_no": admission_no,
        "course_code": course_code,
        "admission_year": start_year,
        "batch_end_year": end_year
    }


def parse_phone_number(text: str) -> str | None:
    match = re.search(PHONE_REGEX, text)
    if match:
        return match.group()
    return None


def parse_name(text: str) -> str | None:
    """
    Best-effort name extraction.
    Handles:
    - 'Student's Name: XYZ'
    - 'Student's Name XYZ'
    """
    lines = text.splitlines()

    for line in lines:
        if "Student" in line and "Name" in line:
            # Remove common label fragments
            cleaned = line
            cleaned = cleaned.replace("Student's Name", "")
            cleaned = cleaned.replace("Student Name", "")
            cleaned = cleaned.replace("Name", "")
            cleaned = cleaned.replace(":", "")
            cleaned = cleaned.strip()

            # Very small sanity check
            if len(cleaned.split()) >= 2:
                return cleaned

    return None

