import uuid
from typing import List

class Mesa:
    """Clase que representa una mesa del restaurante."""
    
    def __init__(self, numero: int, capacidad: int):
        """
        Inicializa una mesa.
        
        Args:
            numero (int): Número de la mesa.
            capacidad (int): Capacidad de personas.
        """
        self.id = str(uuid.uuid4())
        self.numero = numero
        self.capacidad = capacidad
        self.ocupada = False
        self.pedidos_activos: List[str] = []  # Lista de IDs de pedidos
    
    def ocupar(self):
        """Marca la mesa como ocupada."""
        self.ocupada = True
    
    def liberar(self):
        """Marca la mesa como libre."""
        self.ocupada = False
        self.pedidos_activos = []
    
    def agregar_pedido(self, pedido_id: str):
        """
        Agrega un pedido a la mesa.
        
        Args:
            pedido_id (str): ID del pedido.
        """
        if not self.ocupada:
            self.ocupar()
        self.pedidos_activos.append(pedido_id)
    
    def to_dict(self) -> dict:
        """Convierte la mesa a diccionario para JSON."""
        return {
            "id": self.id,
            "numero": self.numero,
            "capacidad": self.capacidad,
            "ocupada": self.ocupada,
            "pedidos_activos": self.pedidos_activos
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Mesa':
        """Crea una mesa desde un diccionario."""
        mesa = Mesa(data["numero"], data["capacidad"])
        mesa.id = data["id"]
        mesa.ocupada = data.get("ocupada", False)
        mesa.pedidos_activos = data.get("pedidos_activos", [])
        return mesa
    
    def __str__(self) -> str:
        estado = "Ocupada" if self.ocupada else "Libre"
        return f"Mesa {self.numero} (Cap: {self.capacidad}) - {estado}"
