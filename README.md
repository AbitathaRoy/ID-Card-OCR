# ID-Card-OCR

A lightweight, modular system for ingesting Google Form responses, extracting structured data from uploaded student ID cards using OCR, and managing volunteer allocation through a local dashboard.

Originally designed for **Convoke (TechFest), Cluster Innovation Centre (CIC), University of Delhi**, but intentionally written to be adaptable to other institutions and forms.

---

## 🧭 What This System Does

1. Reads **Google Form responses** from a linked Google Sheet
2. Downloads **uploaded ID card images** (Google Drive links)
3. Extracts key fields via **OCR (Tesseract)**
4. Stores structured data in a **local SQLite database**
5. Provides a **desktop dashboard (Flet)** to:
   - Filter volunteers
   - Allocate / unallocate students
   - Track allocation categories

---

## 🗂️ Project Structure

```
ID-Card-OCR/
│
├── app.py # Flet-based dashboard
├── requirements.txt
├── README.md
├── architecture.pdf # High-level system architecture
│
├── src/
│ ├── ingest.py # Ingestion pipeline (Sheet → DB)
│ ├── sheet_reader.py # Google Sheet reader
│ ├── sheet_config.py # Sheet export URL (user-provided)
│ ├── ocr.py # OCR wrapper (Tesseract)
│ ├── parse.py # Text parsing logic
│ ├── database.py # SQLite schema + persistence
│ ├── query.py # Read-only DB queries
│ └── __init__.py
│
├── data/
│ ├── volunteer.db # SQLite database (generated)
│ └── raw_images/ # Downloaded ID card images
│
└── .gitignore
```

---

## 🚫 Files Ignored by Git (Must Be Created by User)

These files/directories are **intentionally not tracked** and must be created at runtime:

`src/sheet_config.py`
You must create this file manually:

```python
# src/sheet_config.py
SHEET_EXPORT_URL = "https://docs.google.com/spreadsheets/d/<ID>/export?format=xlsx"
```

## 📦 Prerequisites

This project requires a small set of **system-level** and **Python-level** dependencies.

---

### 1. System Dependency: Tesseract OCR

OCR functionality depends on **Tesseract OCR**, which must be installed separately at the system level.

#### Windows (Recommended)

Use the **UB Mannheim build** of Tesseract OCR:

👉 https://github.com/UB-Mannheim/tesseract/wiki

During installation, ensure that you:
- ✔ Add Tesseract to your **PATH**
- ✔ Install **English language data** (`eng`)
- (Optional) Install additional languages if needed

Verify installation by running:

```bash
tesseract --version
```

If this command succeeds, Tesseract is correctly installed.

### 2. Python Dependencies

Python ≥ 3.10 recommended.

Install dependencies:

```bash
pip install -r requirements.txt
```

The app also performs a runtime dependency check on startup.

## How to Run

### Step 1: Ingest Google Form Data

From the project root:

```bash
python -m src.ingest
```

⚠️ Do not run src/ingest.py directly.

### Step 2: Launch Dashboard

```bash
python app.py
```

## 🧠 Assumptions & Expected Input Structure

This system currently assumes:

### Google Form Columns

* Email address
* Name
* Course
* Year of Study
* WhatsApp Number
* ID Card (file upload)
* Volunteer category selection

If your form differs, update:
* ```process_single_submission()``` in ```src/ingest.py```.

### ID Card Layout Assumptions

The OCR parsing logic expects:
* Admission number containing batch years (e.g. BTH23-27@XXXX)
* Phone number present somewhere on the card
* Student name labeled near “Student Name”

These assumptions are encoded in:
* ```src/parse.py```
* regex definitions in ```src/config.py```

## 🔧 Safe Customization Points

Users are encouraged to tweak:
* Form column mappings → ```src/ingest.py```
* OCR parsing rules → ```src/parse.py```
* Admission number format → regex in ```src/config.py```
* Dashboard filters & layout → ```app.py```
* Allocation logic → ```src/query.py```

Core architecture does **not** need modification.

## 📄 Architecture Overview

See:
👉 [architecture.md](architecture.md)

## 📝 Notes

* SQLite is the single source of truth
* OCR is best-effort, not blocking ingestion
* Dashboard reads only from local DB
* No cloud deployment assumed