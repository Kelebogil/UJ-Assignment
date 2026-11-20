import csv
from datetime import datetime

from database.database import PROJECT_ROOT, connection_scope

REPORTS_DIRECTORY = PROJECT_ROOT / "storage" / "reports"


def get_report_summary():
    with connection_scope() as connection:
        return {
            "vehicles": connection.execute(
                "SELECT COUNT(*) FROM vehicles"
            ).fetchone()[0],
            "available_vehicles": connection.execute(
                "SELECT COUNT(*) FROM vehicles WHERE status = 'Available'"
            ).fetchone()[0],
            "maintenance_vehicles": connection.execute(
                "SELECT COUNT(*) FROM vehicles WHERE status = 'Maintenance'"
            ).fetchone()[0],
            "drivers": connection.execute(
                "SELECT COUNT(*) FROM drivers"
            ).fetchone()[0],
            "active_trips": connection.execute(
                "SELECT COUNT(*) FROM trips WHERE status = 'In Progress'"
            ).fetchone()[0],
            "completed_trips": connection.execute(
                "SELECT COUNT(*) FROM trips WHERE status = 'Completed'"
            ).fetchone()[0],
            "fuel_cost": connection.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM fuel_records"
            ).fetchone()[0],
            "maintenance_cost": connection.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM maintenance_records"
            ).fetchone()[0],
        }


def get_vehicle_costs():
    with connection_scope() as connection:
        return connection.execute(
            """
            SELECT
                vehicles.registration,
                vehicles.make,
                vehicles.model,
                COALESCE(fuel.total, 0) AS fuel_cost,
                COALESCE(maintenance.total, 0) AS maintenance_cost
            FROM vehicles
            LEFT JOIN (
                SELECT vehicle_id, SUM(cost) AS total
                FROM fuel_records GROUP BY vehicle_id
            ) AS fuel USING (vehicle_id)
            LEFT JOIN (
                SELECT vehicle_id, SUM(cost) AS total
                FROM maintenance_records GROUP BY vehicle_id
            ) AS maintenance USING (vehicle_id)
            ORDER BY vehicles.registration
            """
        ).fetchall()


def export_vehicle_costs():
    REPORTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIRECTORY / (
        f"fleet_costs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    rows = get_vehicle_costs()
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(
            ("Registration", "Make", "Model", "Fuel cost", "Maintenance cost")
        )
        writer.writerows(
            (
                row["registration"],
                row["make"],
                row["model"],
                f'{row["fuel_cost"]:.2f}',
                f'{row["maintenance_cost"]:.2f}'
            )
            for row in rows
        )
    return path
