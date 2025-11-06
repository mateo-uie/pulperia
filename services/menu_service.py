import json
import os
from typing import Dict, List
from models.producto import Producto, Plato, Bebida

class MenuService:
    """Servicio para gestionar el menú de la pulpería."""
    
    def __init__(self, archivo_json: str = "data/menu.json"):
        """
        Inicializa el servicio de menú.
        
        Args:
            archivo_json (str): Ruta al archivo JSON del menú.
        """
        self.archivo_json = archivo_json
        self.productos: Dict[str, Producto] = {}
        self.cargar_menu()
    
    def cargar_menu(self):
        """Carga el menú desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for prod_data in data.get("productos", []):
                        producto = Producto.from_dict(prod_data)
                        self.productos[producto.id] = producto
                print(f"Menú cargado: {len(self.productos)} productos")
            except Exception as e:
                print(f"Error cargando menú: {e}")
                self.productos = {}
        else:
            print(f"Archivo {self.archivo_json} no encontrado. Iniciando con menú vacío.")
            self.productos = {}
    
    def guardar_menu(self):
        """Guarda el menú en el archivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
            data = {
                "productos": [prod.to_dict() for prod in self.productos.values()]
            }
            with open(self.archivo_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Menú guardado correctamente")
        except Exception as e:
            print(f"✗ Error guardando menú: {e}")
    
    def agregar_producto(self, producto: Producto) -> Producto:
        """
        Agrega un producto al menú.
        
        Args:
            producto (Producto): Producto a agregar.
            
        Returns:
            Producto: El producto agregado.
        """
        self.productos[producto.id] = producto
        self.guardar_menu()
        return producto
    
    def eliminar_producto(self, producto_id: str) -> bool:
        """
        Elimina un producto del menú.
        
        Args:
            producto_id (str): ID del producto a eliminar.
            
        Returns:
            bool: True si se eliminó, False si no existía.
        """
        if producto_id in self.productos:
            del self.productos[producto_id]
            self.guardar_menu()
            return True
        return False
    
    def obtener_producto(self, producto_id: str) -> Producto:
        """
        Obtiene un producto por su ID.
        
        Args:
            producto_id (str): ID del producto.
            
        Returns:
            Producto: El producto encontrado o None.
        """
        return self.productos.get(producto_id)
    
    def listar_productos(self) -> List[Producto]:
        """
        Lista todos los productos del menú.
        
        Returns:
            List[Producto]: Lista de productos.
        """
        return list(self.productos.values())
    
    def listar_platos(self) -> List[Plato]:
        """
        Lista solo los platos del menú.
        
        Returns:
            List[Plato]: Lista de platos.
        """
        return [p for p in self.productos.values() if isinstance(p, Plato)]
    
    def listar_bebidas(self) -> List[Bebida]:
        """
        Lista solo las bebidas del menú.
        
        Returns:
            List[Bebida]: Lista de bebidas.
        """
        return [p for p in self.productos.values() if isinstance(p, Bebida)]
    
    def buscar_por_nombre(self, nombre: str) -> List[Producto]:
        """
        Busca productos por nombre.
        
        Args:
            nombre (str): Nombre o parte del nombre a buscar.
            
        Returns:
            List[Producto]: Lista de productos que coinciden.
        """
        return [p for p in self.productos.values() 
                if nombre.lower() in p.nombre.lower()]
