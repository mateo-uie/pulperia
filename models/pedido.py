import uuid
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

class EstadoPedido(Enum):
    """Enumeración de estados de un pedido."""
    PENDIENTE = "PENDIENTE"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    COBRADO = "COBRADO"
    CANCELADO = "CANCELADO"


class ItemPedido:
    """Clase que representa un ítem dentro de un pedido."""
    
    def __init__(self, producto_id: str, nombre_producto: str, cantidad: int, precio_unitario: float):
        """
        Inicializa un ítem de pedido.
        
        Args:
            producto_id (str): ID del producto.
            nombre_producto (str): Nombre del producto.
            cantidad (int): Cantidad del producto.
            precio_unitario (float): Precio unitario del producto.
        """
        self.producto_id = producto_id
        self.nombre_producto = nombre_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
    
    def subtotal(self) -> float:
        """
        Calcula el subtotal del ítem.
        
        Returns:
            float: Subtotal del ítem.
        """
        return self.cantidad * self.precio_unitario
    
    def to_dict(self) -> dict:
        """Convierte el ítem a diccionario para JSON."""
        return {
            "producto_id": self.producto_id,
            "nombre_producto": self.nombre_producto,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'ItemPedido':
        """Crea un ítem desde un diccionario."""
        return ItemPedido(
            data["producto_id"],
            data["nombre_producto"],
            data["cantidad"],
            data["precio_unitario"]
        )
    
    def __str__(self) -> str:
        return f"{self.nombre_producto} x{self.cantidad} - ${self.subtotal():.2f}"


class Pedido:
    """Clase que representa un pedido (de mesa o delivery)."""
    
    def __init__(self, tipo: str, items: list = None, mesa_id: Optional[str] = None, 
                 direccion_delivery: Optional[str] = None, telefono_delivery: Optional[str] = None):
        """
        Inicializa un pedido.
        
        Args:
            tipo (str): Tipo de pedido ("mesa" o "delivery").
            items (list): Lista de ItemPedido.
            mesa_id (str, optional): ID de la mesa (si es pedido de mesa).
            direccion_delivery (str, optional): Dirección de entrega (si es delivery).
            telefono_delivery (str, optional): Teléfono de contacto (si es delivery).
        """
        self.id = str(uuid.uuid4())
        self.tipo = tipo  # "mesa" o "delivery"
        self.fecha = datetime.now()
        self.items: list = items if items else []
        self.estado = EstadoPedido.PENDIENTE
        self.mesa_id = mesa_id
        self.direccion_delivery = direccion_delivery
        self.telefono_delivery = telefono_delivery
    
    def agregar_item(self, item: ItemPedido):
        """
        Agrega un ítem al pedido.
        
        Args:
            item (ItemPedido): Ítem a agregar.
        """
        self.items.append(item)
    
    def calcular_total(self) -> float:
        """
        Calcula el total del pedido.
        
        Returns:
            float: Total del pedido.
        """
        return sum(item.subtotal() for item in self.items)
    
    def cambiar_estado(self, nuevo_estado: EstadoPedido):
        """
        Cambia el estado del pedido.
        
        Args:
            nuevo_estado (EstadoPedido): Nuevo estado del pedido.
        """
        self.estado = nuevo_estado
    
    def to_dict(self) -> dict:
        """Convierte el pedido a diccionario para JSON."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "fecha": self.fecha.isoformat(),
            "items": [item.to_dict() for item in self.items],
            "estado": self.estado.value,
            "mesa_id": self.mesa_id,
            "direccion_delivery": self.direccion_delivery,
            "telefono_delivery": self.telefono_delivery
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Pedido':
        """Crea un pedido desde un diccionario."""
        items = [ItemPedido.from_dict(item_data) for item_data in data.get("items", [])]
        pedido = Pedido(
            data["tipo"],
            items,
            data.get("mesa_id"),
            data.get("direccion_delivery"),
            data.get("telefono_delivery")
        )
        pedido.id = data["id"]
        pedido.fecha = datetime.fromisoformat(data["fecha"])
        pedido.estado = EstadoPedido(data["estado"])
        return pedido
    
    def __str__(self) -> str:
        items_str = "\n  ".join([str(item) for item in self.items])
        tipo_info = f"Mesa {self.mesa_id}" if self.tipo == "mesa" else f"Delivery: {self.direccion_delivery}"
        return (f"Pedido {self.id} ({self.tipo})\n"
                f"Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M')}\n"
                f"{tipo_info}\n"
                f"Estado: {self.estado.value}\n"
                f"Items:\n  {items_str}\n"
                f"Total: ${self.calcular_total():.2f}")
