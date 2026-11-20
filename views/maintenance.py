import sqlite3
from datetime import date

import flet as ft

from services.record_service import (
    delete_maintenance_record,
    get_maintenance_records,
    get_vehicles,
    save_maintenance_record
)
from views.common import money, show_confirmation, show_error


def maintenance_view(page):
    record_list = ft.Column(spacing=10)

    def refresh():
        record_list.controls.clear()
        records = get_maintenance_records()
        for record in records:
            next_date = record["next_service_date"] or "Not scheduled"
            record_list.controls.append(
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
                                        f'{record["description"]}',
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        f'Cost: {money(record["cost"])} | '
                                        f'Service date: {record["service_date"]}'
                                    ),
                                    ft.Text(f"Next service: {next_date}")
                                ],
                                expand=True,
                                spacing=4
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Edit maintenance record",
                                on_click=lambda _, row=record: open_form(row)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Delete maintenance record",
                                icon_color="red",
                                on_click=lambda _, row=record: confirm_delete(row)
                            )
                        ]
                    )
                )
            )
        if not records:
            record_list.controls.append(
                ft.Text("No maintenance records found.")
            )
        page.update()

    def open_form(record=None):
        vehicles = get_vehicles()
        if not vehicles:
            show_error(page, "Register a vehicle before adding maintenance records.")
            return

        editing = record is not None
        vehicle = ft.Dropdown(
            label="Vehicle",
            options=[
                ft.dropdown.Option(
                    key=str(row["vehicle_id"]),
                    text=row["registration"]
                )
                for row in vehicles
            ],
            value=str(record["vehicle_id"]) if editing else str(vehicles[0]["vehicle_id"])
        )
        description = ft.TextField(
            label="Description",
            value=record["description"] if editing else ""
        )
        cost = ft.TextField(
            label="Cost",
            value=str(record["cost"]) if editing else "0",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        service_date = ft.TextField(
            label="Service date (YYYY-MM-DD)",
            value=record["service_date"] if editing else date.today().isoformat()
        )
        next_date = ft.TextField(
            label="Next service date (optional)",
            value=record["next_service_date"] or "" if editing else ""
        )
        error = ft.Text(color="red")

        def save(_):
            try:
                save_maintenance_record(
                    int(vehicle.value),
                    description.value or "",
                    float(cost.value or ""),
                    service_date.value or "",
                    next_date.value or None,
                    record["maintenance_id"] if editing else None
                )
            except ValueError as exception:
                error.value = str(exception)
                page.update()
                return
            except (TypeError, sqlite3.Error):
                error.value = "Enter valid maintenance details and select a vehicle."
                page.update()
                return

            page.pop_dialog()
            refresh()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "Edit Maintenance Record" if editing else "Add Maintenance Record"
                ),
                content=ft.Column(
                    controls=[
                        vehicle, description, cost, service_date, next_date, error
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda _: page.pop_dialog()
                    ),
                    ft.Button("Save Record", on_click=save)
                ]
            )
        )

    def confirm_delete(record):
        def remove(_):
            try:
                delete_maintenance_record(record["maintenance_id"])
            except sqlite3.Error as exception:
                page.pop_dialog()
                show_error(page, str(exception), "Maintenance record not deleted")
                return
            page.pop_dialog()
            refresh()

        show_confirmation(
            page,
            "Delete Maintenance Record",
            f'Delete service record for {record["registration"]}?',
            remove
        )

    refresh()
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Maintenance Records",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
                    ft.Button(
                        "Add Maintenance",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: open_form()
                    )
                ]
            ),
            record_list
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )
