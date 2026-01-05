# System Architecture — ID-Card-OCR

## 1. Purpose

This document describes the architecture of **ID-Card-OCR**, a local-first system designed to ingest Google Form responses, extract structured information from uploaded student ID cards using OCR, and manage volunteer allocation through a desktop dashboard.

The architecture prioritizes:
- explicit data flow
- modular components
- fail-soft ingestion
- local persistence
- ease of adaptation to other institutions or forms

---

## 2. High-Level Overview

The system follows a **pipeline-based architecture**, where each stage performs a single, well-defined responsibility.

Google Form  
↓  
Google Sheet (responses)  
↓  
Ingestion Pipeline (Python)  
↓  
OCR + Parsing  
↓  
SQLite Database (local)  
↓  
Dashboard (Flet UI)

There is **no direct coupling** between the dashboard and external services (Google Sheets, Google Drive, OCR engines).

---

## 3. Core Components

### 3.1 Ingestion Layer (`src/ingest.py`)

**Responsibilities:**
- Read responses from a Google Sheet
- Download uploaded ID card images
- Invoke OCR and parsing logic
- Compute derived metadata (e.g., year of study)
- Persist records into a local SQLite database

**Design Notes:**
- Ingestion is **idempotent**
- Email address acts as the primary key
- Failures in OCR do not block data ingestion
- Errors are logged per row, not globally

---

### 3.2 Sheet Reader (`src/sheet_reader.py`)

**Responsibilities:**
- Fetch Google Form responses using a public Sheet export URL
- Load data into a Pandas DataFrame

**Assumptions:**
- The Google Sheet is publicly accessible
- Column names match expected form fields

---

### 3.3 OCR Layer (`src/ocr.py`)

**Responsibilities:**
- Load ID card images from disk
- Extract raw text using Tesseract OCR

**Design Notes:**
- OCR is treated as a *best-effort* process
- Failures result in null OCR fields, not dropped records
- System-level dependency on Tesseract OCR

---

### 3.4 Parsing Layer (`src/parse.py`)

**Responsibilities:**
- Extract structured fields from OCR text:
  - student name
  - admission number
  - phone number
- Derive batch and admission years from admission number formats

**Design Notes:**
- Rule-based parsing using regex and heuristics
- Parsing failures are non-fatal
- Regex definitions are isolated for easy modification

---

### 3.5 Persistence Layer (`src/database.py`)

**Responsibilities:**
- Initialize database schema
- Insert or update student records
- Maintain allocation state

**Key Characteristics:**
- SQLite used as a local, human-auditable datastore
- Single table (`students`) with clear column grouping:
  - typed (form) data
  - OCR-extracted data
  - derived metadata
  - allocation state

**Design Principle:**
> SQLite is the **single source of truth** for the entire system.

---

### 3.6 Query Layer (`src/query.py`)

**Responsibilities:**
- Provide read-only accessors for dashboard filters
- Perform allocation and unallocation updates

**Design Notes:**
- Keeps SQL logic out of the UI
- Enables reuse across interfaces

---

### 3.7 Presentation Layer (`app.py`)

**Responsibilities:**
- Display volunteer data
- Provide filtering by:
  - category
  - allocation status
- Enable allocation and unallocation actions

**Design Notes:**
- Built using **Flet**
- Explicit user-triggered actions (no implicit UI state)
- Reads exclusively from SQLite
- No direct interaction with Google services

---

## 4. Data Flow Characteristics

- Data flows **unidirectionally** during ingestion
- Dashboard interactions only mutate allocation state
- OCR and parsing never modify typed form data
- External services are accessed only during ingestion

---

## 5. Failure Handling Strategy

| Component | Failure Handling |
|---------|------------------|
| Sheet fetch | Raises error, ingestion stops |
| Image download | Row skipped with logged error |
| OCR failure | OCR fields set to `NULL` |
| Parsing failure | Derived fields omitted |
| DB conflict | Row updated via UPSERT |

This ensures maximum data retention with minimal operator intervention.

---

## 6. Assumptions & Constraints

- ID card layouts follow a broadly consistent structure
- Admission numbers encode batch years
- Google Form responses are not maliciously crafted
- System is intended for **small to medium datasets** (tens to hundreds of rows)

---

## 7. Extensibility

The system can be adapted by modifying:
- Form column mappings (`src/ingest.py`)
- OCR parsing rules (`src/parse.py`)
- Admission number formats (regex config)
- Dashboard filters and layout (`app.py`)

Core architecture does **not** require modification for these changes.

---

## 8. Design Principles Summary

- Explicit over implicit
- Local-first persistence
- Fail-soft ingestion
- Clear separation of concerns
- Minimal framework coupling

---

## 9. Status

The system is **feature-complete and stable** as of v1.  
Future work should focus on usability improvements or reporting, not core ingestion logic.
