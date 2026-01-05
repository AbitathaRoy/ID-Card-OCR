# app.py

import sys
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

import flet as ft

# --------------------------------------------------
# Dependency check
# --------------------------------------------------

def ensure_requirements():
    req_file = Path("requirements.txt")
    if not req_file.exists():
        return

    with req_file.open() as f:
        requirements = [
            l.strip() for l in f
            if l.strip() and not l.startswith("#")
        ]

    missing = []
    for req in requirements:
        pkg_name = req.split("==")[0].split(">=")[0].split("<=")[0]
        if importlib.util.find_spec(pkg_name) is None:
            missing.append(req)

    if missing:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing]
        )

ensure_requirements()

# --------------------------------------------------
# Imports from src
# --------------------------------------------------

from src.ingest import run_pipeline
from src.query import (
    get_all_students,
    get_students_by_category,
    allocate_student,
    unallocate_student,
)

# --------------------------------------------------
# Flet App
# --------------------------------------------------

def main(page: ft.Page):
    page.title = "Volunteer Management Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    status_text = ft.Text("Loaded from local database.")

    # ---------------- Categories ----------------

    categories = [
        "Hackathon",
        "Gaming",
        "Quiz",
        "Treasure Hunt",
        "Miscellaneous",
    ]

    category_checks = {
        cat: ft.Checkbox(label=cat, value=False)
        for cat in categories
    }

    def get_selected_categories():
        return [cat for cat, cb in category_checks.items() if cb.value]

    # ---------------- Allocation filters ----------------

    allocation_filter_allocated = ft.Checkbox(label="Allocated", value=True)
    allocation_filter_unallocated = ft.Checkbox(label="Unallocated", value=True)

    def allocation_filter(row):
        is_allocated = row["allocated"] == 1

        if allocation_filter_allocated.value and allocation_filter_unallocated.value:
            return True
        if allocation_filter_allocated.value:
            return is_allocated
        if allocation_filter_unallocated.value:
            return not is_allocated
        return True

    # ---------------- Allocation category selector ----------------

    allocation_category_dropdown = ft.Dropdown(
        label="Allocation Category",
        options=[ft.dropdown.Option(cat) for cat in categories],
        value=categories[0],
        width=250
    )

    # ---------------- Table container ----------------

    table_container = ft.Column()

    # ---------------- Core logic ----------------

    def load_local_data(e=None):
        selected = get_selected_categories()

        if not selected:
            data = get_all_students()
        else:
            seen = {}
            for cat in selected:
                for row in get_students_by_category(cat):
                    seen[row["email"]] = row
            data = list(seen.values())

        data = [row for row in data if allocation_filter(row)]
        build_table(data)

    def build_table(data):
        rows = []

        for row in data:
            is_allocated = row["allocated"] == 1
            allocated_event = row["allocated_event"] or "-"

            def make_toggle(email, allocated):
                return lambda e: toggle_allocation(email, allocated)

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row["ocr_name"] or "—")),
                        ft.DataCell(
                            ft.Text(
                                row["ocr_admission_no"][:3]
                                if row["ocr_admission_no"] else "—"
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                str(row["computed_year_of_study"])
                                if row["computed_year_of_study"] else "—"
                            )
                        ),
                        ft.DataCell(ft.Text(row["ocr_phone"] or "—")),
                        ft.DataCell(ft.Text("Yes" if is_allocated else "No")),
                        ft.DataCell(ft.Text(allocated_event)),
                        ft.DataCell(
                            ft.Button(
                                "Unallocate" if is_allocated else "Allocate",
                                on_click=make_toggle(row["email"], is_allocated),
                            )
                        ),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Course")),
                ft.DataColumn(ft.Text("Year")),
                ft.DataColumn(ft.Text("Phone")),
                ft.DataColumn(ft.Text("Allocated")),
                ft.DataColumn(ft.Text("Allocated Category")),
                ft.DataColumn(ft.Text("Action")),
            ],
            rows=rows,
        )

        table_container.controls = [table]
        table_container.update()

    def refresh_from_sheet(e):
        status_text.value = "Fetching data from Google Sheet..."
        page.update()

        try:
            run_pipeline()
            status_text.value = (
                f"Sheet refreshed at {datetime.now().strftime('%H:%M:%S')}"
            )
        except Exception as ex:
            status_text.value = f"Error: {ex}"

        load_local_data()
        page.update()

    def toggle_allocation(email, is_allocated):
        if is_allocated:
            unallocate_student(email)
        else:
            allocate_student(email, allocation_category_dropdown.value)
        load_local_data()

    # ---------------- UI Controls ----------------

    fetch_sheet_button = ft.Button(
        "Fetch from Google Sheet",
        on_click=refresh_from_sheet,
    )

    apply_filter_button = ft.Button(
        "Apply Filters",
        on_click=load_local_data,
    )

    # ---------------- Layout ----------------

    page.add(
        ft.Column(
            [
                ft.Row([fetch_sheet_button, status_text]),
                ft.Text("Filter by Category:"),
                ft.Row(list(category_checks.values())),
                ft.Text("Filter by Allocation Status:"),
                ft.Row([allocation_filter_allocated, allocation_filter_unallocated]),
                ft.Text("Allocation Category (used when allocating):"),
                allocation_category_dropdown,
                apply_filter_button,
                table_container,
            ]
        )
    )

    load_local_data()

# --------------------------------------------------
# Run
# --------------------------------------------------

ft.run(main)
