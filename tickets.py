from datetime import datetime
import logging

def generar_nuevo_id(tickets: list[dict]) -> int:
    """Calcula el próximo ID único basado en el máximo existente."""
    if not tickets:
        return 1
    return max(ticket["id"] for ticket in tickets) + 1

def crear_ticket(tickets: list[dict], titulo: str, descripcion: str, prioridad: str) -> dict:
    """Crea un nuevo ticket, lo agrega a la lista y registra en el log."""
    nuevo_ticket = {
        "id": generar_nuevo_id(tickets),
        "titulo": titulo.strip(),
        "descripcion": descripcion.strip(),
        "prioridad": prioridad.lower(),
        "estado": "abierto",
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    tickets.append(nuevo_ticket)
    logging.info(f"Ticket #{nuevo_ticket['id']} creado (prioridad {nuevo_ticket['prioridad']})")
    return nuevo_ticket

def buscar_ticket_por_id(tickets: list[dict], ticket_id: int) -> dict | None:
    """Busca y retorna un ticket por su ID, o None si no existe."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    return None

def cambiar_estado_ticket(ticket: dict) -> tuple[bool, str]:
    """
    Avanza el estado del ticket: abierto -> en_curso -> resuelto.
    Retorna (exito, mensaje).
    """
    transiciones = {
        "abierto": "en_curso",
        "en_curso": "resuelto"
    }
    estado_actual = ticket["estado"]
    
    if estado_actual not in transiciones:
        return False, f"El ticket #{ticket['id']} ya está resuelto y no puede avanzar más."
    
    nuevo_estado = transiciones[estado_actual]
    ticket["estado"] = nuevo_estado
    logging.info(f"Ticket #{ticket['id']} cambió a {nuevo_estado}")
    return True, f"Ticket #{ticket['id']} actualizado a '{nuevo_estado}'."

def eliminar_ticket(tickets: list[dict], ticket_id: int) -> bool:
    """Elimina un ticket de la lista por su ID y registra en el log."""
    ticket = buscar_ticket_por_id(tickets, ticket_id)
    if ticket:
        tickets.remove(ticket)
        logging.info(f"Ticket #{ticket_id} eliminado")
        return True
    return False

def ordenar_por_prioridad(tickets: list[dict]) -> list[dict]:
    """Devuelve una copia de los tickets ordenada: alta -> media -> baja."""
    pesos = {"alta": 1, "media": 2, "baja": 3}
    return sorted(tickets, key=lambda t: pesos.get(t["prioridad"], 4))

def filtrar_por_estado(tickets: list[dict], estado: str) -> list[dict]:
    """Filtra los tickets que coincidan con el estado indicado."""
    return [t for t in tickets if t["estado"] == estado]

def filtrar_por_prioridad(tickets: list[dict], prioridad: str) -> list[dict]:
    """Filtra los tickets que coincidan con la prioridad indicada."""
    return [t for t in tickets if t["prioridad"] == prioridad]