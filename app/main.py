from pathlib import Path
import json
from typing import List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


app = FastAPI(
    title="Healthcare Data API",
    description="REST API for processed openFDA drug adverse event data",
    version="1.0.0",
)


DATA_FILE = Path(__file__).resolve().parent / "data" / "records.json"

class Record(BaseModel):
    id: int
    received_date: str | None = None
    patient_age: float | None = None
    patient_sex: str | None = None
    drugs: str
    reactions: str
    serious: int = Field(default=0, ge=1)
    country: str


class PaginatedRecords(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    records: List[Record]


class Stats(BaseModel):
    total_records: int
    average_patient_age: float | None
    serious_distribution: dict[str, int]
    top_countries: dict[str, int]
    top_reactions: dict[str, int]


def load_records() -> list[dict]:
    """Load processed records from the JSON file."""

    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Processed data file not found. Run the ingestion script first.",
        )

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Expected JSON data to be a list.")

        return data

    except (json.JSONDecodeError, OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load processed data: {error}",
        )


@app.get("/")
def root():
    """Health check endpoint."""

    return {
        "message": "Healthcare Data API is running",
        "docs": "/docs",
    }


@app.get(
    "/records",
    response_model=PaginatedRecords,
)
def get_records(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page",
    ),
):
    """Return paginated healthcare records."""

    records = load_records()

    total = len(records)

    start = (page - 1) * page_size
    end = start + page_size

    if start >= total and total > 0:
        raise HTTPException(
            status_code=404,
            detail=f"Page {page} does not exist.",
        )

    paginated_records = records[start:end]

    total_pages = (total + page_size - 1) // page_size

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "records": paginated_records,
    }


@app.get(
    "/records/{record_id}",
    response_model=Record,
)
def get_record(record_id: int):
    """Return a single healthcare record by ID."""

    records = load_records()

    for record in records:
        if record.get("id") == record_id:
            return record

    raise HTTPException(
        status_code=404,
        detail=f"Record with ID {record_id} not found.",
    )


@app.get(
    "/stats",
    response_model=Stats,
)
def get_stats():
    """Return aggregate statistics for the healthcare records."""

    records = load_records()

    total_records = len(records)

    serious_distribution: dict[str, int] = {}

    for record in records:
        serious = str(record.get("serious", "Unknown"))

        serious_distribution[serious] = (
            serious_distribution.get(serious, 0) + 1
        )

    ages = []

    for record in records:
        age = record.get("patient_age")

        if age is not None:
            try:
                ages.append(float(age))
            except (TypeError, ValueError):
                continue

    average_age = (
        round(sum(ages) / len(ages), 2)
        if ages
        else None
    )

    country_counts: dict[str, int] = {}

    for record in records:
        country = record.get("country") or "Unknown"

        country_counts[country] = (
            country_counts.get(country, 0) + 1
        )

    top_countries = dict(
        sorted(
            country_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]
    )

    reaction_counts: dict[str, int] = {}

    for record in records:
        reactions = record.get("reactions", "Unknown")

        for reaction in reactions.split(","):
            reaction = reaction.strip()

            if not reaction:
                continue

            reaction_counts[reaction] = (
                reaction_counts.get(reaction, 0) + 1
            )

    top_reactions = dict(
        sorted(
            reaction_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]
    )

    return {
        "total_records": total_records,
        "average_patient_age": average_age,
        "serious_distribution": serious_distribution,
        "top_countries": top_countries,
        "top_reactions": top_reactions,
    }