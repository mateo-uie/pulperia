import uuid
from typing import Dict, Optional

class Producto:
    """Clase base que representa un producto del menú."""
    
    def __init__(self, nombre: str, precio: float, descripcion: str = ""):
        """
        Inicializa un producto.
        
        Args:
            nombre (str): Nombre del producto.
            precio (float): Precio del producto.
            descripcion (str): Descripción del producto.
        """
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.receta: Dict[str, float] = {}  # {ingrediente_id: cantidad}
    
    def agregar_ingrediente(self, ingrediente_id: str, cantidad: float):
        """
        Agrega un ingrediente a la receta del producto.
        
        Args:
            ingrediente_id (str): ID del ingrediente.
            cantidad (float): Cantidad necesaria del ingrediente.
        """
        self.receta[ingrediente_id] = cantidad
    
    def to_dict(self) -> dict:
        """Convierte el producto a diccionario para JSON."""
        return {
            "id": self.id,
            "tipo": self.__class__.__name__,
            "nombre": self.nombre,
            "precio": self.precio,
            "descripcion": self.descripcion,
            "receta": self.receta
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Producto':
        """Crea un producto desde un diccionario."""
        tipo = data.get("tipo", "Plato")
        if tipo == "Bebida":
            prod = Bebida(
                data["nombre"], 
                data["precio"], 
                data["descripcion"],
                data.get("alcoholica", False)
            )
        else:
            prod = Plato(
                data["nombre"], 
                data["precio"], 
                data["descripcion"],
                data.get("categoria", "Principal")
            )
        prod.id = data["id"]
        prod.receta = data.get("receta", {})
        return prod
    
    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} - ${self.precio:.2f}"


class Plato(Producto):
    """Clase que representa un plato de comida."""
    
    def __init__(self, nombre: str, precio: float, descripcion: str = "", categoria: str = "Principal"):
        """
        Inicializa un plato.
        
        Args:
            nombre (str): Nombre del plato.
            precio (float): Precio del plato.
            descripcion (str): Descripción del plato.
            categoria (str): Categoría (Entrada, Principal, Postre).
        """
        super().__init__(nombre, precio, descripcion)
        self.categoria = categoria
    
    def to_dict(self) -> dict:
        """Convierte el plato a diccionario para JSON."""
        data = super().to_dict()
        data["categoria"] = self.categoria
        return data
    
    def __str__(self) -> str:
        return f"{super().__str__()} [{self.categoria}]"


class Bebida(Producto):
    """Clase que representa una bebida."""
    
    def __init__(self, nombre: str, precio: float, descripcion: str = "", alcoholica: bool = False):
        """
        Inicializa una bebida.
        
        Args:
            nombre (str): Nombre de la bebida.
            precio (float): Precio de la bebida.
            descripcion (str): Descripción de la bebida.
            alcoholica (bool): Si es alcohólica o no.
        """
        super().__init__(nombre, precio, descripcion)
        self.alcoholica = alcoholica
    
    def to_dict(self) -> dict:
        """Convierte la bebida a diccionario para JSON."""
        data = super().to_dict()
        data["alcoholica"] = self.alcoholica
        return data
    
    def __str__(self) -> str:
        tipo = "Alcohólica" if self.alcoholica else "Sin alcohol"
        return f"{super().__str__()} [{tipo}]"
