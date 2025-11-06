from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import Counter
from services.caja_service import CajaService
from services.inventario_service import InventarioService
from services.pedidos_service import PedidosService
from models.pedido import EstadoPedido

class ReportesService:
    """Servicio para generar reportes de la pulpería."""
    
    def __init__(self, caja_service: CajaService, inventario_service: InventarioService, pedidos_service: PedidosService):
        """
        Inicializa el servicio de reportes.
        
        Args:
            caja_service (CajaService): Servicio de caja.
            inventario_service (InventarioService): Servicio de inventario.
            pedidos_service (PedidosService): Servicio de pedidos.
        """
        self.caja_service = caja_service
        self.inventario_service = inventario_service
        self.pedidos_service = pedidos_service
    
    def reporte_ventas_del_dia(self) -> dict:
        """
        Genera un reporte de ventas del día actual.
        
        Returns:
            dict: Reporte con total de ventas, cantidad de pedidos, etc.
        """
        hoy = datetime.now().date()
        facturas_hoy = [f for f in self.caja_service.listar_facturas() if f.fecha.date() == hoy]
        
        total_ventas = sum(f.total for f in facturas_hoy)
        cantidad_pedidos = len(facturas_hoy)
        
        # Métodos de pago
        metodos_pago = Counter(f.metodo_pago for f in facturas_hoy)
        
        return {
            "fecha": hoy.isoformat(),
            "total_ventas": total_ventas,
            "cantidad_pedidos": cantidad_pedidos,
            "ticket_promedio": total_ventas / cantidad_pedidos if cantidad_pedidos > 0 else 0,
            "metodos_pago": dict(metodos_pago)
        }
    
    def reporte_ventas_periodo(self, fecha_inicio: datetime, fecha_fin: datetime) -> dict:
        """
        Genera un reporte de ventas en un periodo.
        
        Args:
            fecha_inicio (datetime): Fecha de inicio.
            fecha_fin (datetime): Fecha de fin.
            
        Returns:
            dict: Reporte de ventas del periodo.
        """
        facturas_periodo = [f for f in self.caja_service.listar_facturas() if fecha_inicio <= f.fecha <= fecha_fin]
        
        total_ventas = sum(f.total for f in facturas_periodo)
        cantidad_pedidos = len(facturas_periodo)
        
        return {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "total_ventas": total_ventas,
            "cantidad_pedidos": cantidad_pedidos,
            "ticket_promedio": total_ventas / cantidad_pedidos if cantidad_pedidos > 0 else 0
        }
    
    def platos_mas_vendidos(self, limite: int = 10) -> List[Tuple[str, int, float]]:
        """
        Obtiene los platos más vendidos.
        
        Args:
            limite (int): Número máximo de resultados.
            
        Returns:
            List[Tuple[str, int, float]]: Lista de (nombre_producto, cantidad_vendida, ingresos_totales)
        """
        # Contar productos vendidos de todos los pedidos cobrados
        contador_productos = {}  # {producto_id: {"nombre": str, "cantidad": int, "ingresos": float}}
        
        pedidos_cobrados = self.pedidos_service.listar_pedidos(EstadoPedido.COBRADO.value)
        
        for pedido in pedidos_cobrados:
            for item in pedido.items:
                if item.producto_id not in contador_productos:
                    contador_productos[item.producto_id] = {
                        "nombre": item.nombre_producto,
                        "cantidad": 0,
                        "ingresos": 0.0
                    }
                contador_productos[item.producto_id]["cantidad"] += item.cantidad
                contador_productos[item.producto_id]["ingresos"] += item.subtotal()
        
        # Ordenar por cantidad vendida
        productos_ordenados = sorted(
            contador_productos.items(),
            key=lambda x: x[1]["cantidad"],
            reverse=True
        )
        
        # Formatear resultado
        resultado = [
            (datos["nombre"], datos["cantidad"], datos["ingresos"])
            for _, datos in productos_ordenados[:limite]
        ]
        
        return resultado
    
    def alertas_bajo_stock(self, umbral: float = None) -> List[dict]:
        """
        Genera alertas de ingredientes con bajo stock.
        
        Args:
            umbral (float): Umbral de cantidad. Si no se especifica, usa el predeterminado.
            
        Returns:
            List[dict]: Lista de ingredientes con bajo stock.
        """
        ingredientes_bajos = self.inventario_service.obtener_bajo_stock(umbral)
        
        alertas = []
        for ing in ingredientes_bajos:
            alertas.append({
                "id": ing.id,
                "nombre": ing.nombre,
                "cantidad_actual": ing.cantidad,
                "unidad": ing.unidad,
                "nivel": "CRÍTICO" if ing.cantidad < 5 else "BAJO"
            })
        
        return alertas
    
    def reporte_estado_mesas(self) -> dict:
        """
        Genera un reporte del estado de las mesas.
        
        Returns:
            dict: Información sobre mesas ocupadas y libres.
        """
        mesas = self.pedidos_service.listar_mesas()
        mesas_ocupadas = [m for m in mesas if m.ocupada]
        mesas_libres = [m for m in mesas if not m.ocupada]
        
        return {
            "total_mesas": len(mesas),
            "mesas_ocupadas": len(mesas_ocupadas),
            "mesas_libres": len(mesas_libres),
            "ocupacion_porcentaje": (len(mesas_ocupadas) / len(mesas) * 100) if mesas else 0,
            "detalle_ocupadas": [{"numero": m.numero, "capacidad": m.capacidad} for m in mesas_ocupadas]
        }
    
    def reporte_completo_diario(self) -> str:
        """
        Genera un reporte completo del día en formato texto.
        
        Returns:
            str: Reporte formateado.
        """
        reporte = "=" * 50 + "\n"
        reporte += "REPORTE DIARIO - PULPERÍA GALÁN\n"
        reporte += "=" * 50 + "\n\n"
        
        # Ventas del día
        ventas = self.reporte_ventas_del_dia()
        reporte += "VENTAS DEL DÍA\n"
        reporte += f"Fecha: {ventas['fecha']}\n"
        reporte += f"Total ventas: ${ventas['total_ventas']:.2f}\n"
        reporte += f"Cantidad de pedidos: {ventas['cantidad_pedidos']}\n"
        reporte += f"Ticket promedio: ${ventas['ticket_promedio']:.2f}\n"
        reporte += f"Métodos de pago: {ventas['metodos_pago']}\n\n"
        
        # Platos más vendidos
        top_platos = self.platos_mas_vendidos(5)
        reporte += "TOP 5 PLATOS MÁS VENDIDOS\n"
        for i, (nombre, cantidad, ingresos) in enumerate(top_platos, 1):
            reporte += f"{i}. {nombre}: {cantidad} unidades (${ingresos:.2f})\n"
        reporte += "\n"
        
        # Alertas de stock
        alertas = self.alertas_bajo_stock()
        if alertas:
            reporte += "ALERTAS DE INVENTARIO\n"
            for alerta in alertas:
                reporte += f"- {alerta['nombre']}: {alerta['cantidad_actual']} {alerta['unidad']} [{alerta['nivel']}]\n"
            reporte += "\n"
        
        # Estado de mesas
        estado_mesas = self.reporte_estado_mesas()
        reporte += "ESTADO DE MESAS\n"
        reporte += f"Ocupación: {estado_mesas['mesas_ocupadas']}/{estado_mesas['total_mesas']} "
        reporte += f"({estado_mesas['ocupacion_porcentaje']:.1f}%)\n"
        
        reporte += "=" * 50 + "\n"
        
        return reporte
