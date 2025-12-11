from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional

class Usuario:
    """Clase base que representa un usuario/empleado del sistema."""
    
    def __init__(self, nombre: str, email: str, rol: str = "empleado"):
        """
        Inicializa un usuario.
        
        Args:
            nombre (str): Nombre del usuario.
            email (str): Correo electrónico.
            rol (str): Rol del usuario.
        """
        self.id: UUID = uuid4()
        self.nombre = nombre
        self.email = email
        self.rol = rol
        # Campos para autenticación (opcionales)
        self.username: Optional[str] = None
        self.hashed_password: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.is_active: bool = True
    
    def es_admin(self) -> bool:
        """
        Verifica si el usuario es administrador.
        
        Returns:
            bool: True si es admin, False en caso contrario.
        """
        return False
    
    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario para JSON."""
        data = {
            "id": str(self.id),
            "tipo": self.__class__.__name__,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol
        }
        if self.username:
            data["username"] = self.username
        if self.hashed_password:
            data["hashed_password"] = self.hashed_password
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        data["is_active"] = self.is_active
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'Usuario':
        """Crea un usuario desde un diccionario."""
        tipo = data.get("tipo", "Empleado")
        if tipo == "Administrador":
            user = Administrador(data["nombre"], data["email"])
        elif tipo == "Mesero":
            user = Mesero(data["nombre"], data["email"])
        elif tipo == "Cocinero":
            user = Cocinero(data["nombre"], data["email"])
        else:
            user = Usuario(data["nombre"], data["email"], data.get("rol", "empleado"))
        
        # Restaurar ID y campos de autenticación
        from uuid import UUID
        user.id = UUID(data["id"]) if isinstance(data["id"], str) else data["id"]
        user.username = data.get("username")
        user.hashed_password = data.get("hashed_password")
        user.is_active = data.get("is_active", True)
        if "created_at" in data:
            user.created_at = datetime.fromisoformat(data["created_at"])
        
        return user
    
    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} ({self.rol}) - {self.email}"


class Administrador(Usuario):
    """Clase que representa un administrador del sistema."""
    
    def __init__(self, nombre: str, email: str):
        """
        Inicializa un administrador.
        
        Args:
            nombre (str): Nombre del administrador.
            email (str): Correo electrónico.
        """
        super().__init__(nombre, email, "administrador")
    
    def es_admin(self) -> bool:
        """
        Verifica si el usuario es administrador.
        
        Returns:
            bool: True siempre para administradores.
        """
        return True


class Mesero(Usuario):
    """Clase que representa un mesero."""
    
    def __init__(self, nombre: str, email: str):
        """
        Inicializa un mesero.
        
        Args:
            nombre (str): Nombre del mesero.
            email (str): Correo electrónico.
        """
        super().__init__(nombre, email, "mesero")


class Cocinero(Usuario):
    """Clase que representa un cocinero."""
    
    def __init__(self, nombre: str, email: str):
        """
        Inicializa un cocinero.
        
        Args:
            nombre (str): Nombre del cocinero.
            email (str): Correo electrónico.
        """
        super().__init__(nombre, email, "cocinero")
