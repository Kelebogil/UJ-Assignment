
from database.database import connection_scope


def add_vehicle(vehicle):

    data = vehicle.to_dict()
    if data["status"] == "On Trip":
        raise ValueError("Start a trip to set a vehicle as On Trip.")

    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO vehicles (
                registration,
                vehicle_type,
                make,
                model,
                year,
                current_mileage,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["registration"],
                data["vehicle_type"],
                data["make"],
                data["model"],
                data["year"],
                data["current_mileage"],
                data["status"]
            )
        )


def get_all_vehicles():

    with connection_scope() as connection:

        return connection.execute(
            """
            SELECT * FROM vehicles
            ORDER BY vehicle_id DESC
            """
        ).fetchall()


def update_vehicle(vehicle_id, vehicle):

    data = vehicle.to_dict()

    with connection_scope() as connection:
        connection.execute("BEGIN IMMEDIATE")
        current = connection.execute(
            """
            SELECT status, current_mileage
            FROM vehicles
            WHERE vehicle_id = ?
            """,
            (vehicle_id,)
        ).fetchone()
        if current is None:
            raise ValueError("Vehicle was not found.")
        if data["status"] == "On Trip" and current["status"] != "On Trip":
            raise ValueError("Start a trip to set a vehicle as On Trip.")
        if current["status"] == "On Trip" and (
            data["status"] != "On Trip"
            or data["current_mileage"] != current["current_mileage"]
        ):
            raise ValueError(
                "Vehicle status and mileage cannot be edited during an active trip."
            )

        connection.execute(
            """
            UPDATE vehicles
            SET registration = ?,
                vehicle_type = ?,
                make = ?,
                model = ?,
                year = ?,
                current_mileage = ?,
                status = ?
            WHERE vehicle_id = ?
            """,
            (
                data["registration"],
                data["vehicle_type"],
                data["make"],
                data["model"],
                data["year"],
                data["current_mileage"],
                data["status"],
                vehicle_id
            )
        )


def delete_vehicle(vehicle_id):

    with connection_scope() as connection:

        connection.execute(
            "DELETE FROM vehicles WHERE vehicle_id = ?",
            (vehicle_id,)
        )


def search_vehicles(keyword):

    with connection_scope() as connection:

        return connection.execute(
            """
            SELECT * FROM vehicles
            WHERE registration LIKE ?
               OR make LIKE ?
               OR model LIKE ?
            ORDER BY registration
            """,
            (
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            )
        ).fetchall()
