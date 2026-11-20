# Truck & Bakkie Fleet Manager

A local desktop fleet management application built with Python, Flet, and SQLite.
It stores data in `storage/fleet.db`; database initialization is safe to rerun and
does not replace existing records.

## Features

- Register, search, update, and remove vehicles.
- Manage drivers and archive drivers with trip history.
- Start and complete trips, with vehicle availability and mileage updated
  transactionally.
- Record fuel purchases and maintenance costs.
- View fleet, trip, and operating-cost summaries and export vehicle costs to CSV.

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

## Setup on Windows

From the project directory, create and activate a virtual environment, then
install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Initialize the database and launch the app:

```powershell
python database\database.py
python main.py
```

The database schema is in `database/schema.sql`. The application creates the
`storage` directory and database file when needed. Keep a backup of
`storage/fleet.db` before manually changing database files or schema.

## Tests

Run the service and database tests with the project environment:

```powershell
python -m unittest discover -s tests -v
```

Tests create an isolated temporary database and do not modify the fleet database.