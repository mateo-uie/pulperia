import uuid

class Ingrediente:
    """Clase que representa un ingrediente en el inventario."""
    
    def __init__(self, nombre: str, unidad: str, cantidad: float):
        """
        Inicializa un ingrediente.
        
        Args:
            nombre (str): Nombre del ingrediente.
            unidad (str): Unidad de medida (kg, litros, unidades, etc.).
            cantidad (float): Cantidad disponible en inventario.
        """
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.unidad = unidad
        self.cantidad = cantidad
    
    def hay_suficiente(self, cantidad_requerida: float) -> bool:
        """
        Verifica si hay suficiente cantidad del ingrediente.
        
        Args:
            cantidad_requerida (float): Cantidad necesaria.
            
        Returns:
            bool: True si hay suficiente, False en caso contrario.
        """
        return self.cantidad >= cantidad_requerida
    
    def descontar(self, cantidad: float):
        """
        Descuenta una cantidad del ingrediente.
        
        Args:
            cantidad (float): Cantidad a descontar.
            
        Raises:
            ValueError: Si no hay suficiente cantidad.
        """
        if not self.hay_suficiente(cantidad):
            raise ValueError(f"No hay suficiente {self.nombre}. Disponible: {self.cantidad} {self.unidad}")
        self.cantidad -= cantidad
    
    def reponer(self, cantidad: float):
        """
        Añade cantidad al ingrediente.
        
        Args:
            cantidad (float): Cantidad a añadir.
        """
        self.cantidad += cantidad
    
    def to_dict(self) -> dict:
        """Convierte el ingrediente a diccionario para JSON."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "unidad": self.unidad,
            "cantidad": self.cantidad
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Ingrediente':
        """Crea un ingrediente desde un diccionario."""
        ing = Ingrediente(data["nombre"], data["unidad"], data["cantidad"])
        ing.id = data["id"]
        return ing
    
    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre}: {self.cantidad} {self.unidad}"
