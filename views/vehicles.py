
import sqlite3

import flet as ft

from models.vehicle import Vehicle
from services.vehicle_service import (
    add_vehicle,
    get_all_vehicles,
    update_vehicle,
    delete_vehicle,
    search_vehicles
)


def vehicles_view(page):

    search_field = ft.TextField(
        label="Search registration, make or model",
        prefix_icon=ft.Icons.SEARCH,
        expand=True
    )

    vehicle_table = ft.Column(spacing=10)

    def refresh_table(keyword=""):

        vehicle_table.controls.clear()

        records = (
            search_vehicles(keyword)
            if keyword
            else get_all_vehicles()
        )

        for record in records:

            vehicle_table.controls.append(
                ft.Container(
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        record["registration"],
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        f'{record["make"]} {record["model"]}'
                                    ),
                                    ft.Text(
                                        f'{record["vehicle_type"]} | '
                                        f'{record["current_mileage"]} km'
                                    ),
                                ],
                                expand=True,
                                spacing=4
                            ),
                            ft.Text(record["status"]),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Edit vehicle",
                                on_click=lambda _, r=record: (
                                    open_form(r)
                                )
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Delete vehicle",
                                icon_color="red",
                                on_click=lambda _, r=record: (
                                    confirm_delete(r)
                                )
                            )
                        ]
                    )
                )
            )

        if not records:
            vehicle_table.controls.append(
                ft.Text("No vehicles found.")
            )

        page.update()

    def open_form(record=None):

        editing = record is not None

        registration = ft.TextField(
            label="Registration Number",
            value=record["registration"] if editing else ""
        )

        vehicle_type = ft.Dropdown(
            label="Vehicle Type",
            options=[
                ft.dropdown.Option("Truck"),
                ft.dropdown.Option("Bakkie"),
                ft.dropdown.Option("Other")
            ],
            value=record["vehicle_type"] if editing else "Bakkie"
        )

        make = ft.TextField(
            label="Make",
            value=record["make"] if editing else ""
        )

        model = ft.TextField(
            label="Model",
            value=record["model"] if editing else ""
        )

        year = ft.TextField(
            label="Year",
            value=str(record["year"]) if editing and record["year"] else ""
        )

        mileage = ft.TextField(
            label="Current Mileage",
            value=str(record["current_mileage"]) if editing else "0",
            disabled=editing and record["status"] == "On Trip"
        )

        status_options = [
            ft.dropdown.Option("Available"),
            ft.dropdown.Option("Maintenance")
        ]
        if editing and record["status"] == "On Trip":
            status_options.append(ft.dropdown.Option("On Trip"))
        status = ft.Dropdown(
            label="Status",
            options=status_options,
            value=record["status"] if editing else "Available",
            disabled=editing and record["status"] == "On Trip"
        )

        error_text = ft.Text(color="red")

        def save_vehicle(_):

            try:
                if not all([
                    registration.value.strip(),
                    make.value.strip(),
                    model.value.strip(),
                    year.value.strip(),
                    mileage.value.strip()
                ]):
                    raise ValueError("Complete all required fields.")

                year_value = int(year.value)
                mileage_value = int(mileage.value)

                if not 1900 <= year_value <= 2100:
                    raise ValueError("Enter a valid manufacturing year.")

                if mileage_value < 0:
                    raise ValueError("Mileage cannot be negative.")

                vehicle = Vehicle(
                    registration=registration.value,
                    vehicle_type=vehicle_type.value,
                    make=make.value.strip(),
                    model=model.value.strip(),
                    year=year_value,
                    current_mileage=mileage_value,
                    status=status.value
                )

                if editing:
                    update_vehicle(record["vehicle_id"], vehicle)
                else:
                    add_vehicle(vehicle)

                page.pop_dialog()
                refresh_table(search_field.value or "")

            except ValueError as ex:
                error_text.value = str(ex)
                page.update()

            except sqlite3.IntegrityError:
                error_text.value = "That registration number is already in use."
                page.update()

            except sqlite3.Error as ex:
                error_text.value = f"Unable to save vehicle: {ex}"
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Edit Vehicle" if editing else "Register Vehicle"
            ),
            content=ft.Column(
                controls=[
                    registration,
                    vehicle_type,
                    make,
                    model,
                    year,
                    mileage,
                    status,
                    error_text
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: page.pop_dialog()
                ),
                ft.Button(
                    "Save Vehicle",
                    on_click=save_vehicle
                )
            ]
        )

        page.show_dialog(dialog)

    def confirm_delete(record):

        def remove_vehicle(_):

            try:
                delete_vehicle(record["vehicle_id"])
                page.pop_dialog()
                refresh_table(search_field.value or "")

            except sqlite3.IntegrityError:
                page.pop_dialog()
                page.show_dialog(
                    ft.AlertDialog(
                        title=ft.Text("Unable to delete"),
                        content=ft.Text(
                            "This vehicle may have related trip, "
                            "fuel or maintenance records."
                        ),
                        actions=[
                            ft.TextButton(
                                "Close",
                                on_click=lambda _: page.pop_dialog()
                            )
                        ]
                    )
                )

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Delete Vehicle"),
                content=ft.Text(
                    f'Delete {record["registration"]}?'
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda _: page.pop_dialog()
                    ),
                    ft.Button(
                        "Delete",
                        on_click=remove_vehicle
                    )
                ]
            )
        )

    search_field.on_change = lambda _: refresh_table(
        search_field.value
    )

    refresh_table()

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Vehicle Management",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
                    ft.Button(
                        "Register Vehicle",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: open_form()
                    )
                ]
            ),
            search_field,
            vehicle_table
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )
