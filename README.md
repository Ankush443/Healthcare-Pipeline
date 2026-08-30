# Healthcare Data API

A small end-to-end healthcare data pipeline built with Python, FastAPI, Bash, and Git. The project fetches public drug adverse-event data from the FDA OpenFDA API, cleans and transforms the data, stores it as CSV and JSON, and exposes it through a REST API.

## Features

* Fetches healthcare data from the public OpenFDA API
* Cleans and transforms raw API responses
* Handles missing values
* Exports processed data to CSV and JSON
* REST API built with FastAPI
* Pagination for healthcare records
* Record lookup by ID
* Statistical aggregation
* Input validation using Pydantic
* Proper HTTP error handling
* Automated API tests with Pytest
* Bash script for one-command setup and execution
* Git feature-branch workflow

## Project Architecture

```text
OpenFDA API
     │
     ▼
scripts/ingest.py
     │
     ├── Clean data
     ├── Transform fields
     └── Handle missing values
     │
     ▼
app/data/
 ├── records.csv
 └── records.json
     │
     ▼
FastAPI
     │
     ├── GET /records
     ├── GET /records/{id}
     └── GET /stats
     │
     ▼
Client
```

## Project Structure

```text
Healthcare-Pipeline/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── data/
│       ├── records.csv
│       └── records.json
├── scripts/
│   └── ingest.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .gitignore
├── requirements.txt
├── run.sh
└── README.md
```

## Technologies

* Python
* FastAPI
* Pydantic
* Pandas
* Requests
* Uvicorn
* Pytest
* Bash
* Git & GitHub

## Data Source

The project uses the public **OpenFDA Drug Adverse Event API**.

The ingestion script retrieves adverse drug event records and extracts relevant fields such as:

* Record ID
* Received date
* Patient age
* Patient sex
* Drugs
* Reactions
* Seriousness code
* Country

## Data Processing

The ingestion pipeline:

1. Sends a request to the OpenFDA API.
2. Retrieves healthcare records.
3. Extracts only the required fields.
4. Handles missing values using default values such as `Unknown`.
5. Converts numeric fields to appropriate types.
6. Combines multiple drugs and reactions into readable strings.
7. Saves the processed data as both CSV and JSON.

## API Documentation

Start the API with:

```bash
uvicorn app.main:app --reload
```

The interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### GET `/records`

Returns healthcare records with pagination.

Example:

```text
GET /records?page=1&page_size=10
```

Parameters:

| Parameter   | Type    | Default | Description                |
| ----------- | ------- | ------: | -------------------------- |
| `page`      | integer |       1 | Page number                |
| `page_size` | integer |      10 | Number of records per page |

`page` must be at least 1, and `page_size` must be between 1 and 100.

Example response:

```json
{
  "page": 1,
  "page_size": 10,
  "total": 100,
  "total_pages": 10,
  "records": []
}
```

### GET `/records/{id}`

Returns a single healthcare record by ID.

Example:

```text
GET /records/1
```

If the record does not exist, the API returns:

```json
{
  "detail": "Record with ID 999999 not found."
}
```

with HTTP status `404`.

### GET `/stats`

Returns aggregate statistics for the processed dataset.

Example:

```json
{
  "total_records": 100,
  "average_patient_age": 58.78,
  "serious_distribution": {
    "1": 34,
    "2": 66
  },
  "top_countries": {
    "US": 80,
    "GB": 5,
    "CN": 4
  },
  "top_reactions": {
    "Dyspnoea": 11,
    "Headache": 8
  }
}
```

The actual values depend on the data returned by OpenFDA at ingestion time.

## Error Handling

The API handles common invalid requests, including:

* Invalid pagination values → `422 Unprocessable Entity`
* Non-existent record IDs → `404 Not Found`
* Missing processed data → `500 Internal Server Error`
* Invalid or corrupted JSON data → `500 Internal Server Error`

## Testing

The project includes automated API tests using Pytest.

Run:

```bash
pytest -v
```

The tests cover:

* Root endpoint
* Record listing
* Pagination
* Invalid pagination parameters
* Single-record retrieval
* Missing record handling
* Statistics endpoint

## Automated Setup

The `run.sh` script automates the main workflow:

```text
Create virtual environment
        ↓
Activate environment
        ↓
Install dependencies
        ↓
Run data ingestion
        ↓
Start FastAPI server
```

On Bash-compatible environments:

```bash
./run.sh
```

For WSL:

```bash
bash run.sh
```

## Design Decisions

### JSON as the API data source

Processed JSON is used by the API because it is simple to load and maps naturally to REST responses. CSV is also generated to provide a convenient tabular representation for analysis.

### FastAPI

FastAPI was selected because it provides automatic request validation, OpenAPI documentation, type-based response validation, and a lightweight REST API structure.

### Pydantic

Pydantic models define the expected API response schema and provide automatic validation.

### Local file storage

A database was intentionally avoided because the assignment focuses on demonstrating data ingestion, transformation, API development, Bash automation, and Git rather than database architecture.

### Pagination

Pagination prevents the API from returning the entire dataset in a single response and demonstrates basic API scalability considerations.

## Running the Project

### Manual setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run ingestion:

```bash
python scripts/ingest.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

### Run tests

```bash
pytest -v
```

### One-command setup

```bash
./run.sh
```

## Git Workflow

The project was developed using a feature-branch workflow.

Example:

```text
main
  │
  └── feature/fastapi-endpoints
          │
          ├── FastAPI endpoints
          └── API tests
                  │
                  ▼
             Pull Request
                  │
                  ▼
                main
```

Meaningful commits were used to separate project initialization, API implementation, testing, and automation work.
