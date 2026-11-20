from datetime import date

from database.database import connection_scope


def get_vehicles():
    with connection_scope() as connection:
        return connection.execute(
            "SELECT vehicle_id, registration FROM vehicles ORDER BY registration"
        ).fetchall()


def get_fuel_records():
    with connection_scope() as connection:
        return connection.execute(
            """
            SELECT fuel_records.*, vehicles.registration
            FROM fuel_records
            JOIN vehicles USING (vehicle_id)
            ORDER BY purchase_date DESC, fuel_id DESC
            """
        ).fetchall()


def save_fuel_record(vehicle_id, litres, cost, purchase_date, fuel_id=None):
    if litres <= 0:
        raise ValueError("Fuel quantity must be greater than zero.")
    if cost < 0:
        raise ValueError("Fuel cost cannot be negative.")
    _validate_date(purchase_date, "Purchase date")

    with connection_scope() as connection:
        values = (vehicle_id, litres, cost, purchase_date)
        if fuel_id is None:
            connection.execute(
                """
                INSERT INTO fuel_records (vehicle_id, litres, cost, purchase_date)
                VALUES (?, ?, ?, ?)
                """,
                values
            )
        else:
            connection.execute(
                """
                UPDATE fuel_records
                SET vehicle_id = ?, litres = ?, cost = ?, purchase_date = ?
                WHERE fuel_id = ?
                """,
                (*values, fuel_id)
            )


def delete_fuel_record(fuel_id):
    with connection_scope() as connection:
        connection.execute("DELETE FROM fuel_records WHERE fuel_id = ?", (fuel_id,))


def get_maintenance_records():
    with connection_scope() as connection:
        return connection.execute(
            """
            SELECT maintenance_records.*, vehicles.registration
            FROM maintenance_records
            JOIN vehicles USING (vehicle_id)
            ORDER BY service_date DESC, maintenance_id DESC
            """
        ).fetchall()


def save_maintenance_record(
    vehicle_id, description, cost, service_date, next_service_date=None,
    maintenance_id=None
):
    description = description.strip()
    if not description:
        raise ValueError("Maintenance description is required.")
    if cost < 0:
        raise ValueError("Maintenance cost cannot be negative.")
    _validate_date(service_date, "Service date")
    if next_service_date:
        _validate_date(next_service_date, "Next service date")
        if next_service_date < service_date:
            raise ValueError("Next service date cannot be before service date.")
    else:
        next_service_date = None

    with connection_scope() as connection:
        values = (
            vehicle_id, description, cost, service_date, next_service_date
        )
        if maintenance_id is None:
            connection.execute(
                """
                INSERT INTO maintenance_records (
                    vehicle_id, description, cost, service_date, next_service_date
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                values
            )
        else:
            connection.execute(
                """
                UPDATE maintenance_records
                SET vehicle_id = ?, description = ?, cost = ?,
                    service_date = ?, next_service_date = ?
                WHERE maintenance_id = ?
                """,
                (*values, maintenance_id)
            )


def delete_maintenance_record(maintenance_id):
    with connection_scope() as connection:
        connection.execute(
            "DELETE FROM maintenance_records WHERE maintenance_id = ?",
            (maintenance_id,)
        )


def _validate_date(value, field_name):
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from error
