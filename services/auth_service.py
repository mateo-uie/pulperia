"""
Servicio de autenticación con JWT y hashing de contraseñas.
"""
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from models.usuario import Usuario, Administrador, Mesero, Cocinero

# Configuración de seguridad
def get_or_create_secret_key() -> str:
    """Obtiene o crea una SECRET_KEY segura."""
    env_path = Path(__file__).parent.parent / ".env"
    
    # Intentar leer de .env
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("SECRET_KEY="):
                    return line.split("=", 1)[1].strip()
    
    # Generar nueva clave si no existe
    new_key = secrets.token_urlsafe(32)
    
    # Guardar en .env
    with open(env_path, "a") as f:
        f.write(f"\nSECRET_KEY={new_key}\n")
    
    return new_key

SECRET_KEY = get_or_create_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """Servicio para gestionar autenticación y usuarios."""
    
    def __init__(self, archivo_json: str = "data/usuarios.json"):
        """Inicializa el servicio con diccionario de usuarios."""
        self.archivo_json = archivo_json
        self.users: Dict[UUID, Usuario] = {}
        self.users_by_username: Dict[str, Usuario] = {}
        self.users_by_email: Dict[str, Usuario] = {}
        self.cargar_usuarios()
    
    def cargar_usuarios(self):
        """Carga los usuarios desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data.get("usuarios", []):
                        # Reconstruir usuario según tipo
                        tipo = user_data.get("tipo", "Usuario")
                        if tipo == "Administrador":
                            user = Administrador.from_dict(user_data)
                        elif tipo == "Mesero":
                            user = Mesero.from_dict(user_data)
                        elif tipo == "Cocinero":
                            user = Cocinero.from_dict(user_data)
                        else:
                            user = Usuario.from_dict(user_data)
                        
                        # Registrar en índices
                        self.users[user.id] = user
                        if hasattr(user, 'username') and user.username:
                            self.users_by_username[user.username] = user
                        if user.email:
                            self.users_by_email[user.email] = user
                            
                print(f"Usuarios cargados: {len(self.users)} usuarios")
            except Exception as e:
                print(f"Error cargando usuarios: {e}")
                self.users = {}
        else:
            print(f"Archivo {self.archivo_json} no encontrado. Iniciando sin usuarios.")
    
    def guardar_usuarios(self):
        """Guarda los usuarios en el archivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
            data = {
                "usuarios": [user.to_dict() for user in self.users.values()]
            }
            with open(self.archivo_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Usuarios guardados correctamente")
        except Exception as e:
            print(f"✗ Error guardando usuarios: {e}")
    
    def hash_password(self, password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        
        Args:
            password (str): Contraseña en texto plano.
            
        Returns:
            str: Contraseña hasheada.
        """
        # Convertir a bytes y generar salt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con el hash.
        
        Args:
            plain_password (str): Contraseña en texto plano.
            hashed_password (str): Contraseña hasheada.
            
        Returns:
            bool: True si coinciden, False en caso contrario.
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def create_user(self, username: str, email: str, password: str, rol: str = "empleado") -> Usuario:
        """
        Crea un nuevo usuario.
        
        Args:
            username (str): Nombre de usuario.
            email (str): Correo electrónico.
            password (str): Contraseña en texto plano.
            rol (str): Rol del usuario.
            
        Returns:
            Usuario: Usuario creado.
            
        Raises:
            ValueError: Si el usuario o email ya existen.
        """
        # Verificar duplicados
        if username in self.users_by_username:
            raise ValueError(f"El nombre de usuario '{username}' ya está registrado")
        
        if email in self.users_by_email:
            raise ValueError(f"El email '{email}' ya está registrado")
        
        # Hashear contraseña y crear usuario según rol
        hashed_password = self.hash_password(password)
        
        # Crear instancia según el rol
        if rol.lower() == "administrador":
            user = Administrador(nombre=username, email=email)
        elif rol.lower() == "mesero":
            user = Mesero(nombre=username, email=email)
        elif rol.lower() == "cocinero":
            user = Cocinero(nombre=username, email=email)
        else:
            user = Usuario(nombre=username, email=email, rol=rol)
        
        user.username = username
        user.hashed_password = hashed_password
        user.created_at = datetime.now()
        user.is_active = True
        
        # Guardar en índices
        self.users[user.id] = user
        self.users_by_username[username] = user
        self.users_by_email[email] = user
        
        # Persistir en JSON
        self.guardar_usuarios()
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario verificando credenciales.
        
        Args:
            username (str): Nombre de usuario.
            password (str): Contraseña en texto plano.
            
        Returns:
            Optional[Usuario]: Usuario si las credenciales son válidas, None en caso contrario.
        """
        user = self.users_by_username.get(username)
        if not user:
            return None
        
        if not hasattr(user, 'hashed_password') or not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT.
        
        Args:
            data (dict): Datos a incluir en el token.
            expires_delta (Optional[timedelta]): Tiempo de expiración.
            
        Returns:
            str: Token JWT.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """
        Verifica un token JWT y extrae el username.
        
        Args:
            token (str): Token JWT.
            
        Returns:
            Optional[str]: Username si el token es válido, None en caso contrario.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            username (str): Nombre de usuario.
            
        Returns:
            Optional[Usuario]: Usuario si existe, None en caso contrario.
        """
        return self.users_by_username.get(username)
    
    def list_users(self) -> list[Usuario]:
        """
        Lista todos los usuarios registrados.
        
        Returns:
            list[Usuario]: Lista de usuarios.
        """
        return list(self.users.values())
