import uuid
from datetime import datetime
from typing import Optional

class Factura:
    """Clase que representa una factura/ticket de un pedido."""
    
    def __init__(self, pedido_id: str, total: float, metodo_pago: str = "efectivo"):
        """
        Inicializa una factura.
        
        Args:
            pedido_id (str): ID del pedido asociado.
            total (float): Total de la factura.
            metodo_pago (str): Método de pago (efectivo, tarjeta, etc.).
        """
        self.id = str(uuid.uuid4())
        self.pedido_id = pedido_id
        self.fecha = datetime.now()
        self.total = total
        self.metodo_pago = metodo_pago
    
    def to_dict(self) -> dict:
        """Convierte la factura a diccionario para JSON."""
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "fecha": self.fecha.isoformat(),
            "total": self.total,
            "metodo_pago": self.metodo_pago
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Factura':
        """Crea una factura desde un diccionario."""
        factura = Factura(
            data["pedido_id"],
            data["total"],
            data.get("metodo_pago", "efectivo")
        )
        factura.id = data["id"]
        factura.fecha = datetime.fromisoformat(data["fecha"])
        return factura
    
    def __str__(self) -> str:
        return (f"========== FACTURA ==========\n"
                f"ID: {self.id}\n"
                f"Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M')}\n"
                f"Pedido: {self.pedido_id}\n"
                f"Método de pago: {self.metodo_pago}\n"
                f"TOTAL: ${self.total:.2f}\n"
                f"============================")
