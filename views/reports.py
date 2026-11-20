import flet as ft

from services.report_service import (
    export_vehicle_costs,
    get_report_summary,
    get_vehicle_costs
)
from views.common import money, show_error


def reports_view(page):
    summary = get_report_summary()
    vehicle_costs = get_vehicle_costs()
    export_status = ft.Text(color="#64748B")

    def stat_card(title, value, detail):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=14, color="#64748B"),
                    ft.Text(
                        str(value),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="#172B46"
                    ),
                    ft.Text(detail, size=12, color="#64748B")
                ],
                spacing=6
            ),
            bgcolor="white",
            padding=16,
            border_radius=10,
            expand=True
        )

    def export_report(_):
        try:
            path = export_vehicle_costs()
        except OSError as error:
            show_error(page, f"Could not export the report: {error}")
            return
        export_status.value = f"CSV saved to {path}"
        page.update()

    cost_rows = []
    for row in vehicle_costs:
        cost_rows.append(
            ft.Container(
                padding=10,
                bgcolor="white",
                border_radius=6,
                content=ft.Row(
                    controls=[
                        ft.Text(
                            f'{row["registration"]} - {row["make"]} {row["model"]}',
                            expand=True
                        ),
                        ft.Text(f'Fuel: {money(row["fuel_cost"])}'),
                        ft.Text(f'Maintenance: {money(row["maintenance_cost"])}')
                    ]
                )
            )
        )
    if not cost_rows:
        cost_rows.append(ft.Text("Register a vehicle to see cost reports."))

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Fleet Reports",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        expand=True
                    ),
                    ft.Button(
                        "Export vehicle costs",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=export_report
                    )
                ]
            ),
            ft.Row(
                controls=[
                    stat_card("Vehicles", summary["vehicles"], "In the fleet"),
                    stat_card(
                        "Available",
                        summary["available_vehicles"],
                        "Ready for assignment"
                    ),
                    stat_card("Drivers", summary["drivers"], "Registered"),
                ],
                spacing=12
            ),
            ft.Row(
                controls=[
                    stat_card(
                        "Trips",
                        summary["completed_trips"],
                        "Completed"
                    ),
                    stat_card(
                        "Active trips",
                        summary["active_trips"],
                        "Currently in progress"
                    ),
                    stat_card(
                        "Fuel spend",
                        money(summary["fuel_cost"]),
                        "Recorded total"
                    ),
                    stat_card(
                        "Maintenance spend",
                        money(summary["maintenance_cost"]),
                        "Recorded total"
                    )
                ],
                spacing=12
            ),
            ft.Text(
                "Vehicle operating costs",
                size=19,
                weight=ft.FontWeight.BOLD
            ),
            *cost_rows,
            export_status
        ],
        expand=True,
        spacing=12,
        scroll=ft.ScrollMode.AUTO
    )
