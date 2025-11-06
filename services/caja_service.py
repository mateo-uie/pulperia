import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from models.factura import Factura
from models.pedido import EstadoPedido
from services.pedidos_service import PedidosService

class CajaService:
    """Servicio para gestionar la caja y facturación de la pulpería."""
    
    def __init__(self, pedidos_service: PedidosService, archivo_json: str = "data/facturas.json"):
        """
        Inicializa el servicio de caja.
        
        Args:
            pedidos_service (PedidosService): Servicio de pedidos.
            archivo_json (str): Ruta al archivo JSON de facturas.
        """
        self.archivo_json = archivo_json
        self.pedidos_service = pedidos_service
        self.facturas: Dict[str, Factura] = {}
        self.cargar_facturas()
    
    def cargar_facturas(self):
        """Carga las facturas desde el archivo JSON."""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for fac_data in data.get("facturas", []):
                        factura = Factura.from_dict(fac_data)
                        self.facturas[factura.id] = factura
                print(f"Facturas cargadas: {len(self.facturas)} facturas")
            except Exception as e:
                print(f"Error cargando facturas: {e}")
                self.facturas = {}
        else:
            print(f"Archivo {self.archivo_json} no encontrado. Iniciando sin facturas.")
            self.facturas = {}
    
    def guardar_facturas(self):
        """Guarda las facturas en el archivo JSON."""
        try:
            os.makedirs(os.path.dirname(self.archivo_json), exist_ok=True)
            data = {
                "facturas": [fac.to_dict() for fac in self.facturas.values()]
            }
            with open(self.archivo_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Facturas guardadas correctamente")
        except Exception as e:
            print(f"✗ Error guardando facturas: {e}")
    
    def cobrar_pedido(self, pedido_id: str, metodo_pago: str = "efectivo") -> tuple[bool, str, Optional[Factura]]:
        """
        Cobra un pedido y genera su factura.
        
        Args:
            pedido_id (str): ID del pedido.
            metodo_pago (str): Método de pago.
            
        Returns:
            tuple[bool, str, Optional[Factura]]: (éxito, mensaje, factura)
        """
        pedido = self.pedidos_service.obtener_pedido(pedido_id)
        if not pedido:
            return (False, "Pedido no encontrado", None)
        
        if pedido.estado == EstadoPedido.COBRADO:
            return (False, "El pedido ya fue cobrado", None)
        
        if pedido.estado != EstadoPedido.LISTO:
            return (False, f"El pedido debe estar LISTO para cobrarse (estado actual: {pedido.estado.value})", None)
        
        # Generar factura
        total = pedido.calcular_total()
        factura = Factura(pedido_id, total, metodo_pago)
        self.facturas[factura.id] = factura
        
        # Cambiar estado del pedido a COBRADO
        pedido.cambiar_estado(EstadoPedido.COBRADO)
        self.pedidos_service.guardar_pedidos()
        
        # Guardar factura
        self.guardar_facturas()
        
        return (True, "Pedido cobrado correctamente", factura)
    
    def obtener_factura(self, factura_id: str) -> Optional[Factura]:
        """
        Obtiene una factura por su ID.
        
        Args:
            factura_id (str): ID de la factura.
            
        Returns:
            Optional[Factura]: La factura o None.
        """
        return self.facturas.get(factura_id)
    
    def listar_facturas(self) -> List[Factura]:
        """
        Lista todas las facturas.
        
        Returns:
            List[Factura]: Lista de facturas.
        """
        return list(self.facturas.values())
    
    def calcular_ingresos_periodo(self, fecha_inicio: datetime, fecha_fin: datetime) -> float:
        """
        Calcula los ingresos totales en un periodo.
        
        Args:
            fecha_inicio (datetime): Fecha de inicio.
            fecha_fin (datetime): Fecha de fin.
            
        Returns:
            float: Total de ingresos.
        """
        total = 0.0
        for factura in self.facturas.values():
            if fecha_inicio <= factura.fecha <= fecha_fin:
                total += factura.total
        return total
    
    def calcular_ingresos_hoy(self) -> float:
        """
        Calcula los ingresos del día actual.
        
        Returns:
            float: Total de ingresos de hoy.
        """
        hoy = datetime.now().date()
        total = 0.0
        for factura in self.facturas.values():
            if factura.fecha.date() == hoy:
                total += factura.total
        return total
