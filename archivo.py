import json
import os
import logging

ARCHIVO_DATOS = "tickets.json"

def cargar_tickets() -> list[dict]:
    """Carga los tickets desde JSON. Si no existe o está corrupto, devuelve lista vacía."""
    if not os.path.exists(ARCHIVO_DATOS):
        guardar_tickets([])
        return []
    
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos if isinstance(datos, list) else []
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error al leer {ARCHIVO_DATOS}: {e}")
        return []

def guardar_tickets(tickets: list[dict]) -> bool:
    """Guarda la lista de tickets en el archivo JSON."""
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=4, ensure_ascii=False)
        return True
    except IOError as e:
        logging.error(f"Error al guardar en {ARCHIVO_DATOS}: {e}")
        return False