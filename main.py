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
    eliminar_ticket,
    ordenar_por_prioridad,
    filtrar_por_estado,
    filtrar_por_prioridad
)
from reportes import calcular_tiempo_abierto, mostrar_resumen, exportar_a_csv

logging.basicConfig(
    filename="helpdesk.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

console = Console()

def pedir_id_valido():
    entrada = questionary.text("Ingresá el ID del ticket:").ask()
    if entrada is None:
        return None
    try:
        ticket_id = int(entrada)
        if ticket_id <= 0:
            raise ValueError
        return ticket_id
    except ValueError:
        console.print("[bold red]El ID tiene que ser un número entero positivo.[/bold red]")
        logging.warning(f"Se ingresó un ID inválido: '{entrada}'")
        return None

def mostrar_tabla_tickets(tickets):
    if not tickets:
        console.print(Panel("No hay tickets para mostrar.", style="yellow"))
        return

    tabla = Table(title="Mesa de Ayuda - Gestión de Tickets", show_lines=True)
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

def main():
    logging.info("Inicio de sesión en el sistema Helpdesk")
    tickets = cargar_tickets()

    opciones_menu = [
        "1. Crear ticket",
        "2. Listar tickets",
        "3. Buscar ticket por ID",
        "4. Cambiar estado",
        "5. Eliminar ticket",
        "6. Filtrar tickets",
        "7. Ver resumen estadístico",
        "8. Exportar reporte a CSV",
        "9. Salir"
    ]

    while True:
        console.print("\n[bold cyan]=== SISTEMA HELPDESK ===[/bold cyan]")
        opcion = questionary.select(
            "¿Qué querés hacer?",
            choices=opciones_menu
        ).ask()

        if opcion is None or opcion.startswith("9."):
            logging.info("Cierre del sistema Helpdesk")
            console.print("[bold green]Cerrando sistema. ¡Nos vemos![/bold green]")
            break

        elif opcion.startswith("1."):
            titulo = questionary.text("Título del problema:").ask()
            if not titulo or not titulo.strip():
                console.print("[yellow]El título no puede quedar vacío.[/yellow]")
                continue

            descripcion = questionary.text("Descripción breve:").ask()
            if descripcion is None:
                continue

            prioridad = questionary.select(
                "Prioridad del ticket:",
                choices=["alta", "media", "baja"]
            ).ask()
            if not prioridad:
                continue

            nuevo = crear_ticket(tickets, titulo.strip(), descripcion.strip(), prioridad)
            guardar_tickets(tickets)
            console.print(f"[bold green]Ticket #{nuevo['id']} creado y guardado.[/bold green]")

        elif opcion.startswith("2."):
            mostrar_tabla_tickets(tickets)

        elif opcion.startswith("3."):
            ticket_id = pedir_id_valido()
            if ticket_id is None:
                continue

            ticket = buscar_ticket_por_id(tickets, ticket_id)
            if ticket:
                detalle = (
                    f"[bold]ID:[/bold] {ticket['id']}\n"
                    f"[bold]Título:[/bold] {ticket['titulo']}\n"
                    f"[bold]Descripción:[/bold] {ticket['descripcion']}\n"
                    f"[bold]Prioridad:[/bold] {ticket['prioridad']}\n"
                    f"[bold]Estado:[/bold] {ticket['estado']}\n"
                    f"[bold]Creado:[/bold] {ticket['fecha_creacion']}\n"
                    f"[bold]Tiempo abierto:[/bold] {calcular_tiempo_abierto(ticket)}"
                )
                console.print(Panel(detalle, title=f"Detalle del Ticket #{ticket_id}", border_style="cyan"))
            else:
                console.print(f"[yellow]No existe ningún ticket con el ID {ticket_id}.[/yellow]")

        elif opcion.startswith("4."):
            ticket_id = pedir_id_valido()
            if ticket_id is None:
                continue

            ticket = buscar_ticket_por_id(tickets, ticket_id)
            if not ticket:
                console.print(f"[yellow]No existe ningún ticket con el ID {ticket_id}.[/yellow]")
                continue

            nuevo_estado = questionary.select(
                f"Estado actual: '{ticket['estado']}'. Elegí el nuevo estado:",
                choices=["abierto", "en_curso", "resuelto"]
            ).ask()

            if nuevo_estado and cambiar_estado_ticket(tickets, ticket_id, nuevo_estado):
                guardar_tickets(tickets)
                console.print(f"[bold green]Se actualizó el ticket #{ticket_id} a '{nuevo_estado}'.[/bold green]")

        elif opcion.startswith("5."):
            ticket_id = pedir_id_valido()
            if ticket_id is None:
                continue

            ticket = buscar_ticket_por_id(tickets, ticket_id)
            if not ticket:
                console.print(f"[yellow]No existe ningún ticket con el ID {ticket_id}.[/yellow]")
                continue

            if ticket["estado"] != "resuelto":
                console.print("[yellow]No se puede borrar un ticket pendiente. Primero pasalo a 'resuelto'.[/yellow]")
                continue

            confirmar = questionary.confirm(
                f"¿Seguro que querés borrar el ticket #{ticket_id} ('{ticket['titulo']}')?",
                default=False
            ).ask()

            if confirmar:
                eliminar_ticket(tickets, ticket_id)
                guardar_tickets(tickets)
                console.print(f"[green]Ticket #{ticket_id} eliminado.[/green]")
            else:
                console.print("[cyan]Listo, se canceló.[/cyan]")

        elif opcion.startswith("6."):
            criterio = questionary.select(
                "Filtrar por:",
                choices=["Estado", "Prioridad", "Volver"]
            ).ask()

            if criterio == "Estado":
                estado = questionary.select(
                    "Elegí el estado:",
                    choices=["abierto", "en_curso", "resuelto"]
                ).ask()
                if estado:
                    mostrar_tabla_tickets(filtrar_por_estado(tickets, estado))

            elif criterio == "Prioridad":
                prioridad = questionary.select(
                    "Elegí la prioridad:",
                    choices=["alta", "media", "baja"]
                ).ask()
                if prioridad:
                    mostrar_tabla_tickets(filtrar_por_prioridad(tickets, prioridad))

        elif opcion.startswith("7."):
            mostrar_resumen(tickets, console)

        elif opcion.startswith("8."):
            if not tickets:
                console.print("[yellow]No hay tickets cargados para exportar.[/yellow]")
            elif exportar_a_csv(tickets):
                console.print("[bold green]Listo, se generó 'reporte_tickets.csv'.[/bold green]")
            else:
                console.print("[bold red]Hubo un problema al generar el CSV.[/bold red]")

if __name__ == "__main__":
    main()