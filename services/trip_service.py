from datetime import date

from database.database import connection_scope


def get_trips():
    with connection_scope() as connection:
        return connection.execute(
            """
            SELECT trips.*, vehicles.registration, drivers.full_name
            FROM trips
            JOIN vehicles USING (vehicle_id)
            JOIN drivers USING (driver_id)
            ORDER BY trips.trip_id DESC
            """
        ).fetchall()


def get_available_vehicles():
    with connection_scope() as connection:
        return connection.execute(
            """
            SELECT vehicle_id, registration, current_mileage
            FROM vehicles
            WHERE status = 'Available'
            ORDER BY registration
            """
        ).fetchall()


def get_active_drivers():
    with connection_scope() as connection:
        return connection.execute(
            """
            SELECT driver_id, full_name
            FROM drivers
            WHERE status = 'Active'
            ORDER BY full_name COLLATE NOCASE
            """
        ).fetchall()


def create_trip(vehicle_id, driver_id, destination, start_mileage, trip_date):
    destination = destination.strip()
    if not destination:
        raise ValueError("Destination is required.")
    if start_mileage < 0:
        raise ValueError("Starting mileage cannot be negative.")
    try:
        date.fromisoformat(trip_date)
    except (TypeError, ValueError) as error:
        raise ValueError("Enter the trip date as YYYY-MM-DD.") from error

    with connection_scope() as connection:
        connection.execute("BEGIN IMMEDIATE")
        vehicle = connection.execute(
            "SELECT status, current_mileage FROM vehicles WHERE vehicle_id = ?",
            (vehicle_id,)
        ).fetchone()
        if vehicle is None:
            raise ValueError("Select an existing vehicle.")
        if vehicle["status"] != "Available":
            raise ValueError("The selected vehicle is not available.")
        if start_mileage < vehicle["current_mileage"]:
            raise ValueError("Starting mileage cannot be below current mileage.")

        driver = connection.execute(
            "SELECT status FROM drivers WHERE driver_id = ?",
            (driver_id,)
        ).fetchone()
        if driver is None or driver["status"] != "Active":
            raise ValueError("Select an active driver.")
        active_driver_trip = connection.execute(
            """
            SELECT 1 FROM trips
            WHERE driver_id = ? AND status = 'In Progress'
            LIMIT 1
            """,
            (driver_id,)
        ).fetchone()
        if active_driver_trip:
            raise ValueError("The selected driver is already assigned to an active trip.")

        cursor = connection.execute(
            """
            INSERT INTO trips (
                vehicle_id, driver_id, destination, start_mileage, trip_date, status
            )
            VALUES (?, ?, ?, ?, ?, 'In Progress')
            """,
            (vehicle_id, driver_id, destination, start_mileage, trip_date)
        )
        connection.execute(
            "UPDATE vehicles SET status = 'On Trip' WHERE vehicle_id = ?",
            (vehicle_id,)
        )
        return cursor.lastrowid


def complete_trip(trip_id, end_mileage):
    if end_mileage < 0:
        raise ValueError("Ending mileage cannot be negative.")

    with connection_scope() as connection:
        connection.execute("BEGIN IMMEDIATE")
        trip = connection.execute(
            """
            SELECT vehicle_id, start_mileage, status
            FROM trips WHERE trip_id = ?
            """,
            (trip_id,)
        ).fetchone()
        if trip is None:
            raise ValueError("Trip was not found.")
        if trip["status"] != "In Progress":
            raise ValueError("Only an in-progress trip can be completed.")
        if end_mileage < trip["start_mileage"]:
            raise ValueError("Ending mileage cannot be below starting mileage.")

        connection.execute(
            """
            UPDATE trips
            SET end_mileage = ?, status = 'Completed'
            WHERE trip_id = ?
            """,
            (end_mileage, trip_id)
        )
        connection.execute(
            """
            UPDATE vehicles
            SET current_mileage = ?, status = 'Available'
            WHERE vehicle_id = ?
            """,
            (end_mileage, trip["vehicle_id"])
        )


def delete_trip(trip_id):
    with connection_scope() as connection:
        connection.execute("BEGIN IMMEDIATE")
        trip = connection.execute(
            "SELECT vehicle_id, status FROM trips WHERE trip_id = ?",
            (trip_id,)
        ).fetchone()
        if trip is None:
            return

        connection.execute("DELETE FROM trips WHERE trip_id = ?", (trip_id,))
        if trip["status"] == "In Progress":
            connection.execute(
                """
                UPDATE vehicles SET status = 'Available'
                WHERE vehicle_id = ? AND status = 'On Trip'
                """,
                (trip["vehicle_id"],)
            )
