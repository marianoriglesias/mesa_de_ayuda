import logging
from datetime import datetime

def obtener_siguiente_id(tickets):
    if not tickets:
        return 1
    return max(t["id"] for t in tickets) + 1

def crear_ticket(tickets, titulo, descripcion, prioridad):
    nuevo_id = obtener_siguiente_id(tickets)
    ticket = {
        "id": nuevo_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "estado": "abierto",
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    tickets.append(ticket)
    logging.info(f"Ticket #{nuevo_id} creado ({prioridad}): {titulo}")
    return ticket

def buscar_ticket_por_id(tickets, ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    return None

def cambiar_estado_ticket(tickets, ticket_id, nuevo_estado):
    ticket = buscar_ticket_por_id(tickets, ticket_id)
    if ticket:
        estado_anterior = ticket["estado"]
        ticket["estado"] = nuevo_estado
        logging.info(f"Ticket #{ticket_id}: estado cambiado de '{estado_anterior}' a '{nuevo_estado}'")
        return True
    return False

def eliminar_ticket(tickets, ticket_id):
    ticket = buscar_ticket_por_id(tickets, ticket_id)
    if ticket:
        tickets.remove(ticket)
        logging.info(f"Ticket #{ticket_id} eliminado")
        return True
    return False

def ordenar_por_prioridad(tickets):
    orden = {"alta": 1, "media": 2, "baja": 3}
    return sorted(tickets, key=lambda t: orden.get(t["prioridad"], 4))

def filtrar_por_estado(tickets, estado):
    return [t for t in tickets if t["estado"] == estado]

def filtrar_por_prioridad(tickets, prioridad):
    return [t for t in tickets if t["prioridad"] == prioridad]