"""
Sistema de Gestion para Pulperia Galan
Demostracion del sistema
"""

from services.menu_service import MenuService
from services.inventario_service import InventarioService
from services.pedidos_service import PedidosService
from services.caja_service import CajaService
from services.reportes_service import ReportesService
from models.pedido import EstadoPedido


def main():
    """Funcion principal del sistema."""
    
    print("\n" + "="*60)
    print("  SISTEMA DE GESTION - PULPERIA GALAN")
    print("="*60 + "\n")
    
    # Inicializar servicios
    print("Inicializando servicios...")
    inventario = InventarioService()
    menu = MenuService()
    pedidos = PedidosService(inventario, menu)  # Pasamos menu_service
    caja = CajaService(pedidos)
    reportes = ReportesService(caja, inventario, pedidos)
    print("Servicios listos\n")
    
    # Mostrar datos iniciales
    print("--- DATOS INICIALES ---")
    print(f"Platos: {len(menu.listar_platos())}")
    print(f"Bebidas: {len(menu.listar_bebidas())}")
    print(f"Ingredientes: {len(inventario.listar_ingredientes())}\n")
    
    # CASO 1: Pedido de mesa
    print("--- CASO 1: PEDIDO DE MESA ---")
    exito, msg, ped1 = pedidos.crear_pedido_mesa(3, {
        "prod-001": 1,  # 1 Pulpo a la Gallega
        "prod-007": 2   # 2 Cervezas
    })
    
    if exito:
        print(f"[OK] {msg} - Total: ${ped1.calcular_total():.2f}")
        pedidos.confirmar_pedido(ped1.id)
        pedidos.cambiar_estado_pedido(ped1.id, EstadoPedido.LISTO.value)
    
    # CASO 2: Pedido delivery
    print("\n--- CASO 2: PEDIDO DELIVERY ---")
    exito, msg, ped2 = pedidos.crear_pedido_delivery(
        "Calle Real 45", 
        "981-123-456",
        {"prod-002": 3}  # 3 Empanadas
    )
    if exito:
        print(f"[OK] {msg} - Total: ${ped2.calcular_total():.2f}")
        pedidos.confirmar_pedido(ped2.id)
        pedidos.cambiar_estado_pedido(ped2.id, EstadoPedido.LISTO.value)
    
    # CASO 3: Facturacion
    print("\n--- CASO 3: FACTURACION ---")
    exito, msg, fac1 = caja.cobrar_pedido(ped1.id, "tarjeta")
    if exito:
        print(f"[OK] Mesa 3 cobrada: ${fac1.total:.2f}")
    
    exito, msg, fac2 = caja.cobrar_pedido(ped2.id, "efectivo")
    if exito:
        print(f"[OK] Delivery cobrado: ${fac2.total:.2f}")
    
    # CASO 4: Reportes
    print("\n--- REPORTES ---")
    ventas = reportes.reporte_ventas_del_dia()
    print(f"Total ventas: ${ventas['total_ventas']:.2f}")
    print(f"Pedidos: {ventas['cantidad_pedidos']}")
    
    top = reportes.platos_mas_vendidos(3)
    print("\nTop 3 productos:")
    for i, (nombre, cant, ing) in enumerate(top, 1):
        print(f"  {i}. {nombre}: {cant} uds")
    
    alertas = reportes.alertas_bajo_stock()
    if alertas:
        print(f"\n[ALERTA] {len(alertas)} ingredientes con stock bajo")
    

if __name__ == "__main__":
    main()
