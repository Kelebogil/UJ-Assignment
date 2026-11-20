import sqlite3
from datetime import date

import flet as ft

from services.record_service import (
    delete_fuel_record,
    get_fuel_records,
    get_vehicles,
    save_fuel_record
)
from views.common import money, show_confirmation, show_error


def fuel_view(page):
    record_list = ft.Column(spacing=10)

    def refresh():
        record_list.controls.clear()
        records = get_fuel_records()
        for record in records:
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
                                        f'{record["litres"]:.2f} L',
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        f'Cost: {money(record["cost"])} | '
                                        f'Date: {record["purchase_date"]}'
                                    )
                                ],
                                expand=True,
                                spacing=4
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Edit fuel record",
                                on_click=lambda _, row=record: open_form(row)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Delete fuel record",
                                icon_color="red",
                                on_click=lambda _, row=record: confirm_delete(row)
                            )
                        ]
                    )
                )
            )
        if not records:
            record_list.controls.append(ft.Text("No fuel records found."))
        page.update()

    def open_form(record=None):
        vehicles = get_vehicles()
        if not vehicles:
            show_error(page, "Register a vehicle before adding fuel records.")
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
        litres = ft.TextField(
            label="Litres",
            value=str(record["litres"]) if editing else "",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        cost = ft.TextField(
            label="Cost",
            value=str(record["cost"]) if editing else "",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        purchase_date = ft.TextField(
            label="Purchase date (YYYY-MM-DD)",
            value=record["purchase_date"] if editing else date.today().isoformat()
        )
        error = ft.Text(color="red")

        def save(_):
            try:
                save_fuel_record(
                    int(vehicle.value),
                    float(litres.value or ""),
                    float(cost.value or ""),
                    purchase_date.value or "",
                    record["fuel_id"] if editing else None
                )
            except ValueError as exception:
                error.value = str(exception)
                page.update()
                return
            except (TypeError, sqlite3.Error):
                error.value = "Enter valid fuel values and select a vehicle."
                page.update()
                return

            page.pop_dialog()
            refresh()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Edit Fuel Record" if editing else "Add Fuel Record"),
                content=ft.Column(
                    controls=[vehicle, litres, cost, purchase_date, error],
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
                delete_fuel_record(record["fuel_id"])
            except sqlite3.Error as exception:
                page.pop_dialog()
                show_error(page, str(exception), "Fuel record not deleted")
                return
            page.pop_dialog()
            refresh()

        show_confirmation(
            page,
            "Delete Fuel Record",
            f'Delete fuel entry for {record["registration"]}?',
            remove
        )

    refresh()
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Fuel Management",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
                    ft.Button(
                        "Add Fuel",
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
