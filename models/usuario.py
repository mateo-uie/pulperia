import uuid

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
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.email = email
        self.rol = rol
    
    def es_admin(self) -> bool:
        """
        Verifica si el usuario es administrador.
        
        Returns:
            bool: True si es admin, False en caso contrario.
        """
        return False
    
    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario para JSON."""
        return {
            "id": self.id,
            "tipo": self.__class__.__name__,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol
        }
    
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
        user.id = data["id"]
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
