# Mesa de Ayuda (Helpdesk) - Soporte Técnico

Sistema de gestión de tickets por consola desarrollado en Python para el área de soporte técnico de una empresa. Permite registrar incidentes, hacer seguimiento de su estado, auditar cambios mediante logs y persistir toda la información de forma local.

## Requisitos previos
- Python 3.10 o superior
- `pip` (gestor de paquetes de Python)

## Instalación

1. Clonar este repositorio:
   ```bash
   git clone https://github.com/marianoriglesias/mesa_de_ayuda.git
   cd mesa_de_ayuda

### Mejoras Opcionales Implementadas
- **Prioridades con código de colores:** Diferenciación visual en la tabla (`alta` en rojo, `media` en amarillo, `baja` en verde).
- **Ordenamiento por prioridad:** Los listados muestran automáticamente primero los tickets de prioridad `alta`, seguidos por `media` y `baja`.
- **Filtrado de tickets:** Permite listar tickets filtrando por estado o por prioridad.
