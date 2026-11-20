import sqlite3

import flet as ft

from services.driver_service import delete_driver, get_drivers, save_driver
from views.common import show_confirmation, show_error


def drivers_view(page):
    search_field = ft.TextField(
        label="Search name or licence number",
        prefix_icon=ft.Icons.SEARCH,
        expand=True
    )
    driver_list = ft.Column(spacing=10)

    def refresh():
        driver_list.controls.clear()
        records = get_drivers(search_field.value or "")
        for record in records:
            driver_list.controls.append(
                ft.Container(
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        record["full_name"],
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        f'Licence: {record["licence_number"]}'
                                    ),
                                    ft.Text(record["phone"] or "No phone number"),
                                ],
                                expand=True,
                                spacing=4
                            ),
                            ft.Text(record["status"]),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Edit driver",
                                on_click=lambda _, row=record: open_form(row)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Delete driver",
                                icon_color="red",
                                on_click=lambda _, row=record: confirm_delete(row)
                            )
                        ]
                    )
                )
            )
        if not records:
            driver_list.controls.append(ft.Text("No drivers found."))
        page.update()

    def open_form(record=None):
        editing = record is not None
        name = ft.TextField(
            label="Full name",
            value=record["full_name"] if editing else ""
        )
        licence = ft.TextField(
            label="Licence number",
            value=record["licence_number"] if editing else ""
        )
        phone = ft.TextField(
            label="Phone (optional)",
            value=record["phone"] or "" if editing else ""
        )
        status = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("Active"),
                ft.dropdown.Option("Inactive")
            ],
            value=record["status"] if editing else "Active"
        )
        error = ft.Text(color="red")

        def save(_):
            try:
                save_driver(
                    name.value or "",
                    licence.value or "",
                    phone.value or "",
                    status.value or "",
                    record["driver_id"] if editing else None
                )
            except ValueError as exception:
                error.value = str(exception)
                page.update()
                return
            except sqlite3.IntegrityError:
                error.value = "That licence number is already registered."
                page.update()
                return

            page.pop_dialog()
            refresh()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Edit Driver" if editing else "Add Driver"),
                content=ft.Column(
                    controls=[name, licence, phone, status, error],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO
                ),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda _: page.pop_dialog()
                    ),
                    ft.Button("Save Driver", on_click=save)
                ]
            )
        )

    def confirm_delete(record):
        def remove(_):
            try:
                delete_driver(record["driver_id"])
            except ValueError as exception:
                page.pop_dialog()
                show_error(page, str(exception), "Driver not deleted")
                return

            page.pop_dialog()
            refresh()

        show_confirmation(
            page,
            "Delete Driver",
            f'Delete {record["full_name"]}? Drivers with trip history must be archived.',
            remove
        )

    search_field.on_change = lambda _: refresh()
    refresh()
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Driver Management",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
                    ft.Button(
                        "Add Driver",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: open_form()
                    )
                ]
            ),
            search_field,
            driver_list
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )
