# Sistema de Gestión - Pulpería Galán

Sistema de gestión integral para restaurantes y pulperías desarrollado en Python. Permite administrar el menú, inventario, pedidos, facturación y generar reportes de ventas.

## Características

- Gestión de menú (platos y bebidas)
- Control de inventario de ingredientes
- Gestión de pedidos (mesa y delivery)
- Sistema de facturación
- Reportes de ventas y estadísticas
- Alertas de stock bajo

## Estructura del Proyecto

```
Pulperia/
├── main.py                     # Archivo principal de demostración
├── data/                       # Archivos JSON de datos
│   ├── empleados.json
│   ├── facturas.json
│   ├── inventario.json
│   ├── menu.json
│   └── pedidos.json
├── models/                     # Modelos de datos
│   ├── factura.py
│   ├── ingrediente.py
│   ├── mesa.py
│   ├── pedido.py
│   ├── producto.py
│   └── usuario.py
└── services/                   # Lógica de negocio
    ├── caja_service.py
    ├── empleados_service.py
    ├── inventario_service.py
    ├── menu_service.py
    ├── pedidos_service.py
    └── reportes_service.py
```

## Datos Iniciales

El sistema carga datos desde archivos JSON en la carpeta `data/`. Los archivos incluyen:
- **menu.json**: Catálogo de platos y bebidas con sus recetas
- **inventario.json**: Stock de ingredientes disponibles
- **pedidos.json**: Historial de pedidos
- **facturas.json**: Registro de facturas emitidas
- **empleados.json**: Datos de empleados del sistema

## Funcionalidades Principales

### Gestión de Menú
- Agregar/modificar platos y bebidas
- Definir recetas e ingredientes necesarios
- Listar productos por categoría

### Inventario
- Registrar ingredientes con stock y unidades
- Actualizar cantidades disponibles
- Alertas de stock bajo

### Pedidos
- Crear pedidos de mesa o delivery
- Confirmar y cambiar estados de pedidos
- Calcular totales automáticamente

### Facturación
- Cobrar pedidos (efectivo/tarjeta)
- Generar facturas con detalles
- Registro de todas las transacciones

### Reportes
- Ventas del día (total e ingresos)
- Productos más vendidos
- Ingredientes con stock crítico

