import flet as ft


def show_error(page, message, title="Unable to complete"):
    page.show_dialog(
        ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda _: page.pop_dialog()
                )
            ]
        )
    )


def show_confirmation(page, title, message, on_confirm):
    page.show_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: page.pop_dialog()
                ),
                ft.Button(
                    "Confirm",
                    on_click=on_confirm
                )
            ]
        )
    )


def money(value):
    return f"{float(value):,.2f}"
