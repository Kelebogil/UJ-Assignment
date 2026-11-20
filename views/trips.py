from datetime import date
import sqlite3

import flet as ft

from services.trip_service import (
    complete_trip,
    create_trip,
    delete_trip,
    get_active_drivers,
    get_available_vehicles,
    get_trips
)
from views.common import show_confirmation, show_error


def trips_view(page):
    trip_list = ft.Column(spacing=10)

    def refresh():
        trip_list.controls.clear()
        records = get_trips()
        for record in records:
            actions = []
            if record["status"] == "In Progress":
                actions.append(
                    ft.Button(
                        "Complete",
                        on_click=lambda _, row=record: open_complete_form(row)
                    )
                )
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Delete trip",
                    icon_color="red",
                    on_click=lambda _, row=record: confirm_delete(row)
                )
            )
            trip_list.controls.append(
                ft.Container(
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        f'{record["registration"]} - '
                                        f'{record["destination"]}',
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        f'Driver: {record["full_name"]} | '
                                        f'Date: {record["trip_date"]}'
                                    ),
                                    ft.Text(
                                        f'Start: {record["start_mileage"]} km | '
                                        f'End: {record["end_mileage"] if record["end_mileage"] is not None else "In progress"}'
                                    )
                                ],
                                expand=True,
                                spacing=4
                            ),
                            ft.Text(record["status"]),
                            *actions
                        ]
                    )
                )
            )
        if not records:
            trip_list.controls.append(ft.Text("No trips recorded."))
        page.update()

    def open_trip_form(_):
        vehicles = get_available_vehicles()
        drivers = get_active_drivers()
        if not vehicles:
            show_error(page, "Add an available vehicle before creating a trip.")
            return
        if not drivers:
            show_error(page, "Add an active driver before creating a trip.")
            return

        vehicle = ft.Dropdown(
            label="Vehicle",
            options=[
                ft.dropdown.Option(
                    key=str(row["vehicle_id"]),
                    text=f'{row["registration"]} ({row["current_mileage"]} km)'
                )
                for row in vehicles
            ],
            value=str(vehicles[0]["vehicle_id"])
        )
        driver = ft.Dropdown(
            label="Driver",
            options=[
                ft.dropdown.Option(
                    key=str(row["driver_id"]),
                    text=row["full_name"]
                )
                for row in drivers
            ],
            value=str(drivers[0]["driver_id"])
        )
        destination = ft.TextField(label="Destination")
        start_mileage = ft.TextField(
            label="Starting mileage",
            value=str(vehicles[0]["current_mileage"]),
            keyboard_type=ft.KeyboardType.NUMBER
        )
        trip_date = ft.TextField(
            label="Trip date (YYYY-MM-DD)",
            value=date.today().isoformat()
        )
        error = ft.Text(color="red")

        def update_start_mileage(_):
            selected = next(
                (row for row in vehicles if str(row["vehicle_id"]) == vehicle.value),
                None
            )
            if selected:
                start_mileage.value = str(selected["current_mileage"])
                page.update()

        vehicle.on_change = update_start_mileage

        def save(_):
            try:
                create_trip(
                    int(vehicle.value),
                    int(driver.value),
                    destination.value or "",
                    int(start_mileage.value or ""),
                    trip_date.value or ""
                )
            except (ValueError, TypeError) as exception:
                error.value = str(exception) or "Enter a valid starting mileage."
                page.update()
                return
            except sqlite3.Error as exception:
                error.value = f"Trip could not be started: {exception}"
                page.update()
                return

            page.pop_dialog()
            refresh()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Start Trip"),
                content=ft.Column(
                    controls=[
                        vehicle, driver, destination, start_mileage, trip_date, error
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda _: page.pop_dialog()
                    ),
                    ft.Button("Start Trip", on_click=save)
                ]
            )
        )

    def open_complete_form(record):
        end_mileage = ft.TextField(
            label="Ending mileage",
            value=str(record["start_mileage"]),
            keyboard_type=ft.KeyboardType.NUMBER
        )
        error = ft.Text(color="red")

        def save(_):
            try:
                complete_trip(record["trip_id"], int(end_mileage.value or ""))
            except (ValueError, TypeError) as exception:
                error.value = str(exception) or "Enter a valid ending mileage."
                page.update()
                return
            except sqlite3.Error as exception:
                error.value = f"Trip could not be completed: {exception}"
                page.update()
                return

            page.pop_dialog()
            refresh()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Complete Trip"),
                content=ft.Column(
                    controls=[end_mileage, error],
                    tight=True
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda _: page.pop_dialog()
                    ),
                    ft.Button("Complete", on_click=save)
                ]
            )
        )

    def confirm_delete(record):
        def remove(_):
            try:
                delete_trip(record["trip_id"])
            except sqlite3.Error as exception:
                page.pop_dialog()
                show_error(page, str(exception), "Trip not deleted")
                return
            page.pop_dialog()
            refresh()

        show_confirmation(
            page,
            "Delete Trip",
            f'Delete the trip to {record["destination"]}?',
            remove
        )

    refresh()
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Trip Management",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
                    ft.Button(
                        "Start Trip",
                        icon=ft.Icons.ADD,
                        on_click=open_trip_form
                    )
                ]
            ),
            trip_list
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )
