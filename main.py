
import flet as ft

from database.database import (
    initialise_database,
)
from services.report_service import get_report_summary
from views.drivers import drivers_view
from views.fuel import fuel_view
from views.maintenance import maintenance_view
from views.reports import reports_view
from views.trips import trips_view
from views.vehicles import vehicles_view


def get_fleet_statistics():
    return get_report_summary()


def main(page: ft.Page):

    initialise_database()

    page.title = "Truck & Bakkie Fleet Management"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F3F5F9"
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600

    # Main content area
    content = ft.Container(
        expand=True,
        padding=30
    )

    def create_stat_card(title, value, description):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        title,
                        size=14,
                        color="#64748B"
                    ),
                    ft.Text(
                        str(value),
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color="#172B46"
                    ),
                    ft.Text(
                        description,
                        size=12,
                        color="#64748B"
                    )
                ],
                spacing=8
            ),
            bgcolor="white",
            padding=20,
            border_radius=12,
            expand=True
        )

    def show_dashboard():

        statistics = get_fleet_statistics()

        content.content = ft.Column(
            controls=[
                ft.Text(
                    "Fleet Dashboard",
                    size=28,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Overview of your fleet operations",
                    color="#64748B"
                ),
                ft.Row(
                    controls=[
                        create_stat_card(
                            "Total Vehicles",
                            statistics["vehicles"],
                            "Registered fleet vehicles"
                        ),
                        create_stat_card(
                            "Available Vehicles",
                            statistics["available_vehicles"],
                            "Ready for assignment"
                        ),
                    ],
                    spacing=15
                ),
                ft.Row(
                    controls=[
                        create_stat_card(
                            "Total Drivers",
                            statistics["drivers"],
                            "Registered drivers"
                        ),
                        create_stat_card(
                            "Under Maintenance",
                            statistics["maintenance_vehicles"],
                            "Vehicles requiring service"
                        ),
                    ],
                    spacing=15
                ),
                ft.Row(
                    controls=[
                        create_stat_card(
                            "Active Trips",
                            statistics["active_trips"],
                            "Currently on the road"
                        ),
                        create_stat_card(
                            "Recorded Fuel Spend",
                            f'{statistics["fuel_cost"]:,.2f}',
                            "Across all vehicles"
                        ),
                    ],
                    spacing=15
                ),
                ft.Container(height=10),
                ft.Text(
                    "Welcome to Fleet Manager",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Use the navigation menu to manage "
                    "your vehicles, drivers and operations."
                )
            ],
            spacing=18,
            scroll=ft.ScrollMode.AUTO
        )

        page.update()

    def show_module(module_name):
        views = {
            "Vehicles": vehicles_view,
            "Drivers": drivers_view,
            "Trips": trips_view,
            "Fuel Management": fuel_view,
            "Maintenance": maintenance_view,
            "Reports": reports_view
        }
        content.content = views[module_name](page)
        page.update()

    # Navigation sidebar
    sidebar = ft.Container(
        width=240,
        bgcolor="#172B46",
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text(
                    "FLEET MANAGER",
                    size=21,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Text(
                    "TRUCK & BAKKIE MANAGEMENT",
                    size=10,
                    color="#AFC2D9"
                ),
                ft.Divider(color="#40536B"),
                ft.Button(
                    "Dashboard",
                    width=200,
                    on_click=lambda _: show_dashboard()
                ),
                ft.Button(
                    "Vehicles",
                    width=200,
                    on_click=lambda _: show_module("Vehicles")
                ),
                ft.Button(
                    "Drivers",
                    width=200,
                    on_click=lambda _: show_module("Drivers")
                ),
                ft.Button(
                    "Trips",
                    width=200,
                    on_click=lambda _: show_module("Trips")
                ),
                ft.Button(
                    "Fuel Management",
                    width=200,
                    on_click=lambda _: show_module("Fuel Management")
                ),
                ft.Button(
                    "Maintenance",
                    width=200,
                    on_click=lambda _: show_module("Maintenance")
                ),
                ft.Button(
                    "Reports",
                    width=200,
                    on_click=lambda _: show_module("Reports")
                ),
                ft.Container(expand=True),
                ft.Text(
                    "Local Administrator",
                    color="#AFC2D9",
                    size=12
                ),
                ft.Text(
                    "Version 1.0",
                    color="#AFC2D9",
                    size=11
                )
            ],
            spacing=12,
            expand=True
        )
    )

    # Main application layout
    page.add(
        ft.Row(
            controls=[
                sidebar,
                content
            ],
            expand=True,
            spacing=0
        )
    )

    show_dashboard()


if __name__ == "__main__":
    ft.run(main)
