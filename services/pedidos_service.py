import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from models.pedido import Pedido, ItemPedido, EstadoPedido
from models.mesa import Mesa
from services.menu_service import MenuService
from services.inventario_service import InventarioService

class PedidosService:
    """Servicio para gestionar pedidos de la pulpería."""
    
    def __init__(self, inventario_service: InventarioService, menu_service=None, archivo_json: str = "data/pedidos.json"):
        """
        Inicializa el servicio de pedidos.
        
        Args:
            inventario_service (InventarioService): Servicio de inventario.
            menu_service (MenuService, optional): Servicio de menú.
            archivo_json (str): Ruta al archivo JSON de pedidos.
        """
        self.archivo_json = archivo_json
        self.inventario_service = inventario_service
        self.menu_service = menu_service
        self.pedidos: Dict[str, Pedido] = {}
        self.mesas: Dict[str, Mesa] = {}
        self._inicializar_mesas()
        self.cargar_pedidos()
    
    def _inicializar_mesas(self):
        """Inicializa las mesas del restaurante."""
        # Crear 10 mesas de ejemplo
        for i in range(1, 11):
            capacidad = 4 if i <= 6 else 6  # Mesas 1-6 para 4 personas, 7-10 para 6
            mesa = Mesa(i, capacidad)
            self.mesas[mesa.id] = mesa
    
    def cargar_pedidos(self):
        """Carga los pedidos desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ped_data in data.get("pedidos", []):
                        pedido = Pedido.from_dict(ped_data)
                        self.pedidos[pedido.id] = pedido
                print(f"Pedidos cargados: {len(self.pedidos)} pedidos")
            except Exception as e:
                print(f"Error cargando pedidos: {e}")
                self.pedidos = {}
        else:
            print(f"Archivo {self.archivo_json} no encontrado. Iniciando sin pedidos.")
            self.pedidos = {}
    
    def guardar_pedidos(self):
        """Guarda los pedidos en el archivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
            data = {
                "pedidos": [ped.to_dict() for ped in self.pedidos.values()]
            }
            with open(self.archivo_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Pedidos guardados correctamente")
        except Exception as e:
            print(f"✗ Error guardando pedidos: {e}")
    
    def crear_pedido_mesa(self, numero_mesa: int, productos_cantidades: Dict[str, int]) -> tuple[bool, str, Optional[Pedido]]:
        """
        Crea un pedido para una mesa.
        
        Args:
            numero_mesa (int): Número de la mesa.
            productos_cantidades (Dict[str, int]): Diccionario de {producto_id: cantidad}
            
        Returns:
            tuple[bool, str, Optional[Pedido]]: (éxito, mensaje, pedido)
            
        Example:
            pedidos.crear_pedido_mesa(3, {"prod-001": 1, "prod-007": 2})
        """
        if not self.menu_service:
            return (False, "MenuService no configurado", None)
        
        # Buscar la mesa
        mesa = None
        for m in self.mesas.values():
            if m.numero == numero_mesa:
                mesa = m
                break
        
        if not mesa:
            return (False, f"Mesa {numero_mesa} no encontrada", None)
        
        # Convertir productos_cantidades a items_data
        items_data = []
        for prod_id, cantidad in productos_cantidades.items():
            producto = self.menu_service.obtener_producto(prod_id)
            if not producto:
                return (False, f"Producto {prod_id} no encontrado", None)
            
            items_data.append({
                "producto_id": prod_id,
                "nombre": producto.nombre,
                "cantidad": cantidad,
                "precio": producto.precio,
                "receta": producto.receta
            })
        
        return self._crear_pedido("mesa", items_data, mesa_id=mesa.id)
    
    def crear_pedido_delivery(self, direccion: str, telefono: str, 
                               productos_cantidades: Dict[str, int]) -> tuple[bool, str, Optional[Pedido]]:
        """
        Crea un pedido para delivery.
        
        Args:
            direccion (str): Dirección de entrega.
            telefono (str): Teléfono de contacto.
            productos_cantidades (Dict[str, int]): Diccionario de {producto_id: cantidad}
            
        Returns:
            tuple[bool, str, Optional[Pedido]]: (éxito, mensaje, pedido)
            
        Example:
            pedidos.crear_pedido_delivery("Calle Real 45", "981-123", {"prod-002": 3})
        """
        if not self.menu_service:
            return (False, "MenuService no configurado", None)
        
        # Convertir productos_cantidades a items_data
        items_data = []
        for prod_id, cantidad in productos_cantidades.items():
            producto = self.menu_service.obtener_producto(prod_id)
            if not producto:
                return (False, f"Producto {prod_id} no encontrado", None)
            
            items_data.append({
                "producto_id": prod_id,
                "nombre": producto.nombre,
                "cantidad": cantidad,
                "precio": producto.precio,
                "receta": producto.receta
            })
        
        return self._crear_pedido("delivery", items_data, 
                                 direccion_delivery=direccion, 
                                 telefono_delivery=telefono)
    
    def _crear_pedido(self, tipo: str, items_data: List[dict], 
                      mesa_id: Optional[str] = None,
                      direccion_delivery: Optional[str] = None,
                      telefono_delivery: Optional[str] = None) -> tuple[bool, str, Optional[Pedido]]:
        """
        Método interno para crear un pedido.
        
        Args:
            tipo (str): Tipo de pedido.
            items_data (List[dict]): Lista de items.
            mesa_id (str, optional): ID de la mesa.
            direccion_delivery (str, optional): Dirección de delivery.
            telefono_delivery (str, optional): Teléfono de delivery.
            
        Returns:
            tuple[bool, str, Optional[Pedido]]: (éxito, mensaje, pedido)
        """
        
        # Crear items del pedido y verificar recetas
        items = []
        recetas_totales = {}
        
        for item_data in items_data:
            producto_id = item_data["producto_id"]
            cantidad = item_data["cantidad"]
            
            # Buscar producto en MenuService (necesitamos acceso al menú)
            # Por ahora usamos los datos que vienen en item_data
            item = ItemPedido(
                producto_id,
                item_data["nombre"],
                cantidad,
                item_data["precio"]
            )
            items.append(item)
            
            # Acumular recetas si existen
            if "receta" in item_data and item_data["receta"]:
                for ing_id, cant_ing in item_data["receta"].items():
                    if ing_id not in recetas_totales:
                        recetas_totales[ing_id] = 0
                    recetas_totales[ing_id] += cant_ing * cantidad
        
        # Verificar inventario
        if recetas_totales:
            hay_stock, faltantes = self.inventario_service.verificar_receta(recetas_totales)
            if not hay_stock:
                return (False, f"Stock insuficiente: {', '.join(faltantes)}", None)
        
        # Crear el pedido
        pedido = Pedido(tipo, items, mesa_id, direccion_delivery, telefono_delivery)
        
        # Descontar ingredientes del inventario
        if recetas_totales:
            for ing_id, cantidad in recetas_totales.items():
                ingrediente = self.inventario_service.obtener_ingrediente(ing_id)
                if ingrediente:
                    try:
                        ingrediente.descontar(cantidad)
                        print(f"✓ Descontado {cantidad} {ingrediente.unidad} de {ingrediente.nombre}")
                    except ValueError as e:
                        # Revertir cambios si hay error
                        return (False, f"Error al descontar inventario: {str(e)}", None)
            
            # Guardar inventario actualizado
            self.inventario_service.guardar_inventario()
        
        self.pedidos[pedido.id] = pedido
        
        # Si es pedido de mesa, actualizar la mesa
        if mesa_id:
            mesa = self.mesas.get(mesa_id)
            if mesa:
                mesa.agregar_pedido(pedido.id)
        
        self.guardar_pedidos()
        return (True, "Pedido creado correctamente", pedido)
    
    def confirmar_pedido(self, pedido_id: str) -> tuple[bool, str]:
        """
        Confirma un pedido y descuenta el inventario.
        
        Args:
            pedido_id (str): ID del pedido.
            
        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        pedido = self.pedidos.get(pedido_id)
        if not pedido:
            return (False, "Pedido no encontrado")
        
        if pedido.estado != EstadoPedido.PENDIENTE:
            return (False, f"Pedido ya está en estado {pedido.estado.value}")
        
        # Aquí deberíamos tener acceso a las recetas de los productos
        # Por simplicidad, asumimos que ya se verificó al crear
        
        pedido.cambiar_estado(EstadoPedido.EN_PREPARACION)
        self.guardar_pedidos()
        return (True, "Pedido confirmado y en preparación")
    
    def cambiar_estado_pedido(self, pedido_id: str, nuevo_estado: str) -> tuple[bool, str]:
        """
        Cambia el estado de un pedido.
        
        Args:
            pedido_id (str): ID del pedido.
            nuevo_estado (str): Nuevo estado.
            
        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        pedido = self.pedidos.get(pedido_id)
        if not pedido:
            return (False, "Pedido no encontrado")
        
        try:
            estado = EstadoPedido(nuevo_estado)
            pedido.cambiar_estado(estado)
            self.guardar_pedidos()
            return (True, f"Estado cambiado a {nuevo_estado}")
        except ValueError:
            return (False, f"Estado no válido: {nuevo_estado}")
    
    def obtener_pedido(self, pedido_id: str) -> Optional[Pedido]:
        """
        Obtiene un pedido por su ID.
        
        Args:
            pedido_id (str): ID del pedido.
            
        Returns:
            Optional[Pedido]: El pedido o None.
        """
        return self.pedidos.get(pedido_id)
    
    def listar_pedidos(self, estado: Optional[str] = None) -> List[Pedido]:
        """
        Lista pedidos, opcionalmente filtrados por estado.
        
        Args:
            estado (str, optional): Estado para filtrar.
            
        Returns:
            List[Pedido]: Lista de pedidos.
        """
        if estado:
            try:
                est = EstadoPedido(estado)
                return [p for p in self.pedidos.values() if p.estado == est]
            except ValueError:
                return []
        return list(self.pedidos.values())
    
    def listar_mesas(self) -> List[Mesa]:
        """
        Lista todas las mesas.
        
        Returns:
            List[Mesa]: Lista de mesas.
        """
        return list(self.mesas.values())
    
    def obtener_mesa(self, numero_mesa: int) -> Optional[Mesa]:
        """
        Obtiene una mesa por su número.
        
        Args:
            numero_mesa (int): Número de la mesa.
            
        Returns:
            Optional[Mesa]: La mesa o None.
        """
        for mesa in self.mesas.values():
            if mesa.numero == numero_mesa:
                return mesa
        return None
