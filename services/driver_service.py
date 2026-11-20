import sqlite3

from database.database import connection_scope


def get_drivers(search=""):
    with connection_scope() as connection:
        return connection.execute(
            """
            SELECT * FROM drivers
            WHERE full_name LIKE ? OR licence_number LIKE ?
            ORDER BY full_name COLLATE NOCASE
            """,
            (f"%{search}%", f"%{search}%")
        ).fetchall()


def save_driver(full_name, licence_number, phone, status, driver_id=None):
    full_name = full_name.strip()
    licence_number = licence_number.strip().upper()
    phone = phone.strip() or None

    if not full_name or not licence_number:
        raise ValueError("Name and licence number are required.")
    if status not in ("Active", "Inactive"):
        raise ValueError("Choose a valid driver status.")

    with connection_scope() as connection:
        if driver_id is None:
            cursor = connection.execute(
                """
                INSERT INTO drivers (full_name, licence_number, phone, status)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, licence_number, phone, status)
            )
            return cursor.lastrowid

        if status != "Active":
            active_trip = connection.execute(
                """
                SELECT 1 FROM trips
                WHERE driver_id = ? AND status = 'In Progress'
                LIMIT 1
                """,
                (driver_id,)
            ).fetchone()
            if active_trip:
                raise ValueError("A driver with an active trip cannot be deactivated.")

        connection.execute(
            """
            UPDATE drivers
            SET full_name = ?, licence_number = ?, phone = ?, status = ?
            WHERE driver_id = ?
            """,
            (full_name, licence_number, phone, status, driver_id)
        )


def delete_driver(driver_id):
    try:
        with connection_scope() as connection:
            connection.execute(
                "DELETE FROM drivers WHERE driver_id = ?",
                (driver_id,)
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(
            "This driver has trip history and cannot be deleted. "
            "Set the driver to Inactive instead."
        ) from error
