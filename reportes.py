import csv
import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def calcular_tiempo_abierto(ticket):
    if ticket["estado"] == "resuelto":
        return "Resuelto"
    
    try:
        creacion = datetime.strptime(ticket["fecha_creacion"], "%Y-%m-%d %H:%M")
        diferencia = datetime.now() - creacion
        horas = diferencia.total_seconds() / 3600
        if horas < 1:
            minutos = int(diferencia.total_seconds() / 60)
            return f"{minutos} min"
        return f"{horas:.1f} hs"
    except ValueError:
        return "N/D"

def generar_estadisticas(tickets):
    por_estado = {"abierto": 0, "en_curso": 0, "resuelto": 0}
    por_prioridad = {"alta": 0, "media": 0, "baja": 0}

    for t in tickets:
        est = t.get("estado")
        prio = t.get("prioridad")
        if est in por_estado:
            por_estado[est] += 1
        if prio in por_prioridad:
            por_prioridad[prio] += 1

    return {
        "total": len(tickets),
        "por_estado": por_estado,
        "por_prioridad": por_prioridad
    }

def mostrar_resumen(tickets, console):
    if not tickets:
        console.print(Panel("No hay tickets cargados para armar el resumen.", style="yellow"))
        return

    stats = generar_estadisticas(tickets)

    tabla_estados = Table(title="Tickets por Estado", show_header=True)
    tabla_estados.add_column("Estado", style="cyan")
    tabla_estados.add_column("Cantidad", justify="center", style="bold white")
    for estado, cant in stats["por_estado"].items():
        tabla_estados.add_row(estado, str(cant))

    tabla_prio = Table(title="Tickets por Prioridad", show_header=True)
    tabla_prio.add_column("Prioridad", style="magenta")
    tabla_prio.add_column("Cantidad", justify="center", style="bold white")
    for prio, cant in stats["por_prioridad"].items():
        tabla_prio.add_row(prio.upper(), str(cant))

    console.print(Panel.fit(f"[bold]Total de tickets en sistema:[/bold] {stats['total']}", style="blue"))
    console.print(tabla_estados)
    console.print(tabla_prio)

def exportar_a_csv(tickets, nombre_archivo="reporte_tickets.csv"):
    """Exporta los tickets actuales a un CSV separado por punto y coma para Excel."""
    if not tickets:
        return False

    campos = ["id", "titulo", "descripcion", "prioridad", "estado", "fecha_creacion", "tiempo_abierto"]

    try:
        with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
            escritor = csv.DictWriter(f, fieldnames=campos, delimiter=";")
            escritor.writeheader()
            for t in tickets:
                datos_fila = {
                    "id": t["id"],
                    "titulo": t["titulo"],
                    "descripcion": t["descripcion"],
                    "prioridad": t["prioridad"],
                    "estado": t["estado"],
                    "fecha_creacion": t["fecha_creacion"],
                    "tiempo_abierto": calcular_tiempo_abierto(t)
                }
                escritor.writerow(datos_fila)
        logging.info(f"Reporte CSV generado: {nombre_archivo}")
        return True
    except IOError as e:
        logging.error(f"No se pudo generar el CSV {nombre_archivo}: {e}")
        return False