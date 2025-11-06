import json
import os
from typing import Dict, List
from models.usuario import Usuario, Administrador, Mesero, Cocinero

class EmpleadosService:
    """Servicio para gestionar empleados de la pulpería."""
    
    def __init__(self, archivo_json: str = "data/empleados.json"):
        """
        Inicializa el servicio de empleados.
        
        Args:
            archivo_json (str): Ruta al archivo JSON de empleados.
        """
        self.archivo_json = archivo_json
        self.empleados: Dict[str, Usuario] = {}
        self.cargar_empleados()
    
    def cargar_empleados(self):
        """Carga los empleados desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for emp_data in data.get("empleados", []):
                        empleado = Usuario.from_dict(emp_data)
                        self.empleados[empleado.id] = empleado
                print(f"Empleados cargados: {len(self.empleados)} empleados")
            except Exception as e:
                print(f"Error cargando empleados: {e}")
                self.empleados = {}
        else:
            print(f"Archivo {self.archivo_json} no encontrado. Iniciando sin empleados.")
            self.empleados = {}
    
    def guardar_empleados(self):
        """Guarda los empleados en el archivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
            data = {
                "empleados": [emp.to_dict() for emp in self.empleados.values()]
            }
            with open(self.archivo_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Empleados guardados correctamente")
        except Exception as e:
            print(f"✗ Error guardando empleados: {e}")
    
    def registrar_empleado(self, tipo: str, nombre: str, email: str) -> Usuario:
        """
        Registra un nuevo empleado.
        
        Args:
            tipo (str): Tipo de empleado ("admin", "mesero", "cocinero").
            nombre (str): Nombre del empleado.
            email (str): Email del empleado.
            
        Returns:
            Usuario: El empleado registrado.
            
        Raises:
            ValueError: Si el tipo de empleado no es válido.
        """
        if tipo == "admin":
            empleado = Administrador(nombre, email)
        elif tipo == "mesero":
            empleado = Mesero(nombre, email)
        elif tipo == "cocinero":
            empleado = Cocinero(nombre, email)
        else:
            raise ValueError(f"Tipo de empleado no válido: {tipo}")
        
        self.empleados[empleado.id] = empleado
        self.guardar_empleados()
        return empleado
    
    def obtener_empleado(self, empleado_id: str) -> Usuario:
        """
        Obtiene un empleado por su ID.
        
        Args:
            empleado_id (str): ID del empleado.
            
        Returns:
            Usuario: El empleado o None.
        """
        return self.empleados.get(empleado_id)
    
    def eliminar_empleado(self, empleado_id: str) -> bool:
        """
        Elimina un empleado.
        
        Args:
            empleado_id (str): ID del empleado.
            
        Returns:
            bool: True si se eliminó, False si no existía.
        """
        if empleado_id in self.empleados:
            del self.empleados[empleado_id]
            self.guardar_empleados()
            return True
        return False
    
    def listar_empleados(self) -> List[Usuario]:
        """
        Lista todos los empleados.
        
        Returns:
            List[Usuario]: Lista de empleados.
        """
        return list(self.empleados.values())
    
    def listar_por_rol(self, rol: str) -> List[Usuario]:
        """
        Lista empleados por rol.
        
        Args:
            rol (str): Rol a filtrar.
            
        Returns:
            List[Usuario]: Lista de empleados con ese rol.
        """
        return [emp for emp in self.empleados.values() if emp.rol == rol]
    
    def login_basico(self, email: str) -> Usuario:
        """
        Login básico por email.
        
        Args:
            email (str): Email del empleado.
            
        Returns:
            Usuario: El empleado o None si no se encuentra.
        """
        for empleado in self.empleados.values():
            if empleado.email == email:
                return empleado
        return None
