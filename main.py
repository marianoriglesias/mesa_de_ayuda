import logging
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from archivo import cargar_tickets, guardar_tickets
from tickets import (
    crear_ticket,
    buscar_ticket_por_id,
    cambiar_estado_ticket,
    eliminar_ticket
)

from tickets import (
    crear_ticket,
    buscar_ticket_por_id,
    cambiar_estado_ticket,
    eliminar_ticket,
    ordenar_por_prioridad,
    filtrar_por_estado,
    filtrar_por_prioridad
)
import tickets

logging.basicConfig(
    filename="helpdesk.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

from reportes import calcular_tiempo_abierto, mostrar_resumen

console = Console()

def pedir_id_valido(mensaje: str = "Ingresá el ID del ticket:") -> int | None:
    """Pide un ID numérico y maneja errores de conversión con try-except."""
    entrada = questionary.text(mensaje).ask()
    if entrada is None:
        return None
    try:
        ticket_id = int(entrada)
        if ticket_id <= 0:
            console.print("[red]El ID debe ser un número positivo.[/red]")
            return None
        return ticket_id
    except ValueError:
        console.print("[red]Error: Tenés que ingresar un número entero válido.[/red]")
        return None

def mostrar_tabla_tickets(tickets: list[dict]):
    """Renderiza todos los tickets en una tabla formateada con Rich."""
    if not tickets:
        console.print(Panel("No hay tickets registrados en el sistema.", style="yellow"))
        return

    tabla = Table(title="📋 Listado de Tickets - Mesa de Ayuda", show_lines=True)
    tabla.add_column("ID", justify="center", style="cyan", no_wrap=True)
    tabla.add_column("Título", style="bold white")
    tabla.add_column("Prioridad", justify="center")
    tabla.add_column("Estado", justify="center")
    tabla.add_column("Fecha Creación", justify="center", style="dim")
    tabla.add_column("Tiempo Abierto", justify="center", style="magenta")

    colores_prioridad = {"alta": "red", "media": "yellow", "baja": "green"}
    tickets_ordenados = ordenar_por_prioridad(tickets)

    for t in tickets_ordenados:
        color = colores_prioridad.get(t["prioridad"], "white")
        prioridad_fmt = f"[{color}]{t['prioridad'].upper()}[/{color}]"
        tabla.add_row(
            str(t["id"]),
            t["titulo"],
            prioridad_fmt,
            t["estado"],
            t["fecha_creacion"],
            calcular_tiempo_abierto(t)
        )

    console.print(tabla)

def mostrar_detalle_ticket(ticket: dict):
    """Muestra toda la información de un ticket específico."""
    detalle = (
        f"[bold cyan]ID:[/bold cyan] {ticket['id']}\n"
        f"[bold cyan]Título:[/bold cyan] {ticket['titulo']}\n"
        f"[bold cyan]Descripción:[/bold cyan] {ticket['descripcion']}\n"
        f"[bold cyan]Prioridad:[/bold cyan] {ticket['prioridad'].upper()}\n"
        f"[bold cyan]Estado:[/bold cyan] {ticket['estado']}\n"
        f"[bold cyan]Fecha de creación:[/bold cyan] {ticket['fecha_creacion']}"
    )
    console.print(Panel(detalle, title=f"Detalle del Ticket #{ticket['id']}", expand=False))

def main():
    tickets = cargar_tickets()
    console.print(Panel.fit("[bold blue]Sistema de Mesa de Ayuda (Helpdesk)[/bold blue]"))

    opciones_menu = [
        "1. Crear ticket",
        "2. Listar tickets",
        "3. Buscar ticket por ID",
        "4. Cambiar estado",
        "5. Eliminar ticket",
        "6. Filtrar tickets",
        "7. Ver resumen estadístico",
        "8. Salir"
    ]

    while True:
        console.print()
        opcion = questionary.select("Seleccioná una opción:", choices=opciones_menu).ask()

        if opcion is None or opcion.startswith("8."):
            if guardar_tickets(tickets):
                console.print("[bold green]Datos guardados correctamente. ¡Hasta luego![/bold green]")
            else:
                console.print("[bold red]Hubo un problema al guardar los datos.[/bold red]")
            break

        elif opcion.startswith("1."):
            titulo = questionary.text(
                "Título del problema:",
                validate=lambda text: True if len(text.strip()) > 0 else "El título no puede estar vacío."
            ).ask()
            if titulo is None:
                continue

            descripcion = questionary.text("Descripción detallada:").ask() or ""
            prioridad = questionary.select(
                "Prioridad:",
                choices=["alta", "media", "baja"]
            ).ask()
            if prioridad is None:
                continue

            nuevo = crear_ticket(tickets, titulo, descripcion, prioridad)
            guardar_tickets(tickets)
            console.print(f"[green]✔ Ticket #{nuevo['id']} creado con éxito.[/green]")

        elif opcion.startswith("2."):
            mostrar_tabla_tickets(tickets)

        elif opcion.startswith("3."):
            ticket_id = pedir_id_valido()
            if ticket_id is not None:
                ticket = buscar_ticket_por_id(tickets, ticket_id)
                if ticket:
                    mostrar_detalle_ticket(ticket)
                else:
                    console.print(f"[yellow]No se encontró ningún ticket con ID #{ticket_id}.[/yellow]")

        elif opcion.startswith("4."):
            ticket_id = pedir_id_valido("Ingresá el ID del ticket para avanzar su estado:")
            if ticket_id is not None:
                ticket = buscar_ticket_por_id(tickets, ticket_id)
                if ticket:
                    exito, msg = cambiar_estado_ticket(ticket)
                    if exito:
                        guardar_tickets(tickets)
                        console.print(f"[green]✔ {msg}[/green]")
                    else:
                        console.print(f"[yellow]{msg}[/yellow]")
                else:
                    console.print(f"[yellow]No se encontró ningún ticket con ID #{ticket_id}.[/yellow]")

        elif opcion.startswith("5."):
            ticket_id = pedir_id_valido("Ingresá el ID del ticket a eliminar:")
            if ticket_id is not None:
                ticket = buscar_ticket_por_id(tickets, ticket_id)
                if ticket:
                    mostrar_detalle_ticket(ticket)
                    confirmar = questionary.confirm(
                        f"¿Estás seguro de que querés eliminar el ticket #{ticket_id}?",
                        default=False
                    ).ask()
                    if confirmar:
                        eliminar_ticket(tickets, ticket_id)
                        guardar_tickets(tickets)
                        console.print(f"[green]✔ Ticket #{ticket_id} eliminado.[/green]")
                    else:
                        console.print("[cyan]Operación cancelada.[/cyan]")
                else:
                    console.print(f"[yellow]No se encontró ningún ticket con ID #{ticket_id}.[/yellow]")

        elif opcion.startswith("6."):            
            criterio = questionary.select(
                "¿Cómo querés filtrar?",
                choices=["Por estado", "Por prioridad", "Cancelar"]
            ).ask()

            if criterio == "Por estado":
                estado = questionary.select(
                    "Elegí el estado:",
                    choices=["abierto", "en_curso", "resuelto"]
                ).ask()
                if estado:
                    mostrar_tabla_tickets(filtrar_por_estado(tickets, estado))

            elif criterio == "Por prioridad":
                prioridad = questionary.select(
                    "Elegí la prioridad:",
                    choices=["alta", "media", "baja"]
                ).ask()
                if prioridad:
                    mostrar_tabla_tickets(filtrar_por_prioridad(tickets, prioridad))

        elif opcion.startswith("7."):
            mostrar_resumen(tickets, console)
            
if __name__ == "__main__":
    main()