import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from database.database import connection_scope, initialise_database
from models.vehicle import Vehicle
from services.driver_service import delete_driver, save_driver
from services.record_service import (
    get_fuel_records,
    get_maintenance_records,
    save_fuel_record,
    save_maintenance_record
)
from services.report_service import (
    export_vehicle_costs,
    get_report_summary,
    get_vehicle_costs
)
from services.trip_service import complete_trip, create_trip
from services.vehicle_service import (
    add_vehicle,
    get_all_vehicles,
    update_vehicle
)


class FleetServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "fleet.db"
        self.database_patcher = patch(
            "database.database.DATABASE_PATH",
            self.database_path
        )
        self.database_patcher.start()
        initialise_database()

        add_vehicle(
            Vehicle(
                registration="TEST-001",
                vehicle_type="Truck",
                make="Test",
                model="Hauler",
                year=2024,
                current_mileage=100
            )
        )
        self.vehicle_id = get_all_vehicles()[0]["vehicle_id"]
        save_driver("Test Driver", "LIC-001", "0123456789", "Active")
        with connection_scope() as connection:
            self.driver_id = connection.execute(
                "SELECT driver_id FROM drivers WHERE licence_number = ?",
                ("LIC-001",)
            ).fetchone()["driver_id"]

    def tearDown(self):
        self.database_patcher.stop()
        self.temporary_directory.cleanup()

    def test_trip_start_and_completion_update_vehicle_state(self):
        trip_id = create_trip(
            self.vehicle_id,
            self.driver_id,
            "Johannesburg",
            100,
            date.today().isoformat()
        )
        with connection_scope() as connection:
            vehicle = connection.execute(
                "SELECT status, current_mileage FROM vehicles WHERE vehicle_id = ?",
                (self.vehicle_id,)
            ).fetchone()
        self.assertEqual(vehicle["status"], "On Trip")
        self.assertEqual(vehicle["current_mileage"], 100)

        with self.assertRaises(ValueError):
            complete_trip(trip_id, 99)
        with self.assertRaisesRegex(ValueError, "during an active trip"):
            update_vehicle(
                self.vehicle_id,
                Vehicle(
                    registration="TEST-001",
                    vehicle_type="Truck",
                    make="Test",
                    model="Hauler",
                    year=2024,
                    current_mileage=100,
                    status="Available"
                )
            )
        with connection_scope() as connection:
            trip = connection.execute(
                "SELECT status FROM trips WHERE trip_id = ?",
                (trip_id,)
            ).fetchone()
        self.assertEqual(trip["status"], "In Progress")

        complete_trip(trip_id, 180)
        with connection_scope() as connection:
            vehicle = connection.execute(
                "SELECT status, current_mileage FROM vehicles WHERE vehicle_id = ?",
                (self.vehicle_id,)
            ).fetchone()
        self.assertEqual(vehicle["status"], "Available")
        self.assertEqual(vehicle["current_mileage"], 180)

    def test_active_vehicle_cannot_be_assigned_to_another_trip(self):
        trip_date = date.today().isoformat()
        create_trip(
            self.vehicle_id, self.driver_id, "Pretoria", 100, trip_date
        )
        with self.assertRaisesRegex(ValueError, "not available"):
            create_trip(
                self.vehicle_id, self.driver_id, "Durban", 100, trip_date
            )
        with connection_scope() as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM trips"
            ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_driver_cannot_be_assigned_to_two_active_trips(self):
        trip_date = date.today().isoformat()
        create_trip(
            self.vehicle_id, self.driver_id, "Pretoria", 100, trip_date
        )
        with connection_scope() as connection:
            connection.execute(
                """
                INSERT INTO vehicles (
                    registration, vehicle_type, make, model, current_mileage
                )
                VALUES ('TEST-002', 'Bakkie', 'Test', 'Utility', 50)
                """
            )
            second_vehicle_id = connection.execute(
                "SELECT vehicle_id FROM vehicles WHERE registration = ?",
                ("TEST-002",)
            ).fetchone()["vehicle_id"]

        with self.assertRaisesRegex(ValueError, "already assigned"):
            create_trip(
                second_vehicle_id,
                self.driver_id,
                "Durban",
                50,
                trip_date
            )

    def test_driver_with_trip_history_cannot_be_deleted(self):
        create_trip(
            self.vehicle_id,
            self.driver_id,
            "Soweto",
            100,
            date.today().isoformat()
        )
        with self.assertRaisesRegex(ValueError, "trip history"):
            delete_driver(self.driver_id)

    def test_fuel_and_maintenance_records_feed_cost_reports(self):
        today = date.today().isoformat()
        save_fuel_record(self.vehicle_id, 42.5, 800.0, today)
        save_maintenance_record(
            self.vehicle_id,
            "Scheduled service",
            1250.0,
            today,
            "2027-01-01"
        )

        self.assertEqual(len(get_fuel_records()), 1)
        self.assertEqual(len(get_maintenance_records()), 1)
        summary = get_report_summary()
        self.assertEqual(summary["fuel_cost"], 800.0)
        self.assertEqual(summary["maintenance_cost"], 1250.0)
        costs = get_vehicle_costs()
        self.assertEqual(costs[0]["fuel_cost"], 800.0)
        self.assertEqual(costs[0]["maintenance_cost"], 1250.0)
        report_directory = Path(self.temporary_directory.name) / "reports"
        with patch(
            "services.report_service.REPORTS_DIRECTORY",
            report_directory
        ):
            report_path = export_vehicle_costs()
        self.assertTrue(report_path.is_file())
        self.assertIn("TEST-001", report_path.read_text(encoding="utf-8-sig"))

    def test_duplicate_driver_licence_is_rejected_by_database(self):
        with self.assertRaises(sqlite3.IntegrityError):
            save_driver("Another Driver", "LIC-001", "", "Active")


if __name__ == "__main__":
    unittest.main()
