import json
import os
from typing import Dict, List
from models.ingrediente import Ingrediente

class InventarioService:
    """Servicio para gestionar el inventario de ingredientes."""
    
    def __init__(self, archivo_json: str = "data/inventario.json"):
        """
        Inicializa el servicio de inventario.
        
        Args:
            archivo_json (str): Ruta al archivo JSON del inventario.
        """
        self.archivo_json = archivo_json
        self.ingredientes: Dict[str, Ingrediente] = {}
        self.umbral_bajo_stock = 10.0  # Umbral para alertas de bajo stock
        self.cargar_inventario()
    
    def cargar_inventario(self):
        """Carga el inventario desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ing_data in data.get("ingredientes", []):
                        ingrediente = Ingrediente.from_dict(ing_data)
                        self.ingredientes[ingrediente.id] = ingrediente
                print(f"Inventario cargado: {len(self.ingredientes)} ingredientes")
            except Exception as e:
                print(f"Error cargando inventario: {e}")
                self.ingredientes = {}
        else:
            print(f"Archivo {self.archivo_json} no encontrado. Iniciando con inventario vacío.")
            self.ingredientes = {}
    
    def guardar_inventario(self):
        """Guarda el inventario en el archivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
            data = {
                "ingredientes": [ing.to_dict() for ing in self.ingredientes.values()]
            }
            with open(self.archivo_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Inventario guardado correctamente")
        except Exception as e:
            print(f"✗ Error guardando inventario: {e}")
    
    def agregar_ingrediente(self, ingrediente: Ingrediente) -> Ingrediente:
        """
        Agrega un ingrediente al inventario.
        
        Args:
            ingrediente (Ingrediente): Ingrediente a agregar.
            
        Returns:
            Ingrediente: El ingrediente agregado.
        """
        self.ingredientes[ingrediente.id] = ingrediente
        self.guardar_inventario()
        return ingrediente
    
    def obtener_ingrediente(self, ingrediente_id: str) -> Ingrediente:
        """
        Obtiene un ingrediente por su ID.
        
        Args:
            ingrediente_id (str): ID del ingrediente.
            
        Returns:
            Ingrediente: El ingrediente o None.
        """
        return self.ingredientes.get(ingrediente_id)
    
    def reponer_stock(self, ingrediente_id: str, cantidad: float) -> bool:
        """
        Repone el stock de un ingrediente.
        
        Args:
            ingrediente_id (str): ID del ingrediente.
            cantidad (float): Cantidad a reponer.
            
        Returns:
            bool: True si se repuso, False si no existe el ingrediente.
        """
        ingrediente = self.obtener_ingrediente(ingrediente_id)
        if ingrediente:
            ingrediente.reponer(cantidad)
            self.guardar_inventario()
            return True
        return False
    
    def verificar_receta(self, receta: Dict[str, float]) -> tuple[bool, List[str]]:
        """
        Verifica si hay suficientes ingredientes para una receta.
        
        Args:
            receta (Dict[str, float]): Diccionario {ingrediente_id: cantidad}.
            
        Returns:
            tuple[bool, List[str]]: (hay_suficiente, lista_faltantes)
        """
        faltantes = []
        for ing_id, cantidad in receta.items():
            ingrediente = self.obtener_ingrediente(ing_id)
            if not ingrediente:
                faltantes.append(f"Ingrediente {ing_id} no existe en inventario")
            elif not ingrediente.hay_suficiente(cantidad):
                faltantes.append(f"{ingrediente.nombre}: necesita {cantidad} {ingrediente.unidad}, "
                               f"disponible {ingrediente.cantidad} {ingrediente.unidad}")
        
        return (len(faltantes) == 0, faltantes)
    
    def descontar_receta(self, receta: Dict[str, float]) -> bool:
        """
        Descuenta los ingredientes de una receta del inventario.
        
        Args:
            receta (Dict[str, float]): Diccionario {ingrediente_id: cantidad}.
            
        Returns:
            bool: True si se descontó correctamente, False en caso contrario.
        """
        # Primero verificar que hay suficiente de todo
        hay_suficiente, faltantes = self.verificar_receta(receta)
        if not hay_suficiente:
            print(f"✗ No se puede descontar receta. Faltantes: {faltantes}")
            return False
        
        # Descontar
        for ing_id, cantidad in receta.items():
            ingrediente = self.obtener_ingrediente(ing_id)
            ingrediente.descontar(cantidad)
        
        self.guardar_inventario()
        return True
    
    def listar_ingredientes(self) -> List[Ingrediente]:
        """
        Lista todos los ingredientes.
        
        Returns:
            List[Ingrediente]: Lista de ingredientes.
        """
        return list(self.ingredientes.values())
    
    def obtener_bajo_stock(self, umbral: float = None) -> List[Ingrediente]:
        """
        Obtiene ingredientes con bajo stock.
        
        Args:
            umbral (float): Umbral de cantidad. Si no se especifica, usa el predeterminado.
            
        Returns:
            List[Ingrediente]: Lista de ingredientes con bajo stock.
        """
        if umbral is None:
            umbral = self.umbral_bajo_stock
        
        return [ing for ing in self.ingredientes.values() if ing.cantidad < umbral]
