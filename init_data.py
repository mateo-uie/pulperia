#!/usr/bin/env python3
"""
Script de inicialización de datos de ejemplo para Pulpería Galán
Crea usuarios, productos, ingredientes, pedidos y facturas
"""

import sys
import requests
import time

API_URL = "http://localhost"

# Colores para la consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_section(msg):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

# Datos de usuarios
USUARIOS = [
    {
        "username": "admin",
        "email": "admin@pulperia.com",
        "password": "admin123",
        "rol": "administrador"
    },
    {
        "username": "fernando_mesero",
        "email": "fernando@pulperia.com",
        "password": "fernando123",
        "rol": "mesero"
    },
    {
        "username": "alvaro_cocinero",
        "email": "alvaro@pulperia.com",
        "password": "alvaro123",
        "rol": "cocinero"
    },
    {
        "username": "rosa_cocinera",
        "email": "rosa@pulperia.com",
        "password": "rosa123",
        "rol": "cocinero"
    },
    {
        "username": "antonio_cocinero",
        "email": "antonio@pulperia.com",
        "password": "antonio123",
        "rol": "cocinero"
    },
    {
        "username": "cliente1",
        "email": "cliente1@example.com",
        "password": "cliente123",
        "rol": "empleado"
    }
]

# Datos de productos
PRODUCTOS = [
    {
        "nombre": "Pulpo a la Gallega",
        "precio": 18.50,
        "tipo": "plato",
        "descripcion": "Pulpo cocido con papas, aceite de oliva y pimentón"
    },
    {
        "nombre": "Empanada Gallega",
        "precio": 3.50,
        "tipo": "plato",
        "descripcion": "Empanada tradicional de carne"
    },
    {
        "nombre": "Bocadillo de Jamón",
        "precio": 5.00,
        "tipo": "plato",
        "descripcion": "Bocadillo de jamón serrano con tomate"
    },
    {
        "nombre": "Tarta de Santiago",
        "precio": 4.50,
        "tipo": "plato",
        "descripcion": "Tarta tradicional de almendras"
    },
    {
        "nombre": "Caldo Gallego",
        "precio": 6.00,
        "tipo": "plato",
        "descripcion": "Caldo tradicional gallego con grelos"
    },
    {
        "nombre": "Albariño",
        "precio": 12.00,
        "tipo": "bebida",
        "descripcion": "Vino blanco gallego"
    },
    {
        "nombre": "Ribeiro",
        "precio": 10.00,
        "tipo": "bebida",
        "descripcion": "Vino tinto joven"
    },
    {
        "nombre": "Agua Mineral",
        "precio": 1.50,
        "tipo": "bebida",
        "descripcion": "Agua mineral natural"
    },
    {
        "nombre": "Café",
        "precio": 1.20,
        "tipo": "bebida",
        "descripcion": "Café expreso"
    },
    {
        "nombre": "Cerveza Estrella Galicia",
        "precio": 2.50,
        "tipo": "bebida",
        "descripcion": "Cerveza gallega"
    }
]

# Datos de ingredientes
INGREDIENTES = [
    {"nombre": "Pulpo", "unidad": "kg", "cantidad": 50.0},
    {"nombre": "Papas", "unidad": "kg", "cantidad": 45.0},
    {"nombre": "Aceite de oliva", "unidad": "litros", "cantidad": 15.0},
    {"nombre": "Pimentón", "unidad": "kg", "cantidad": 8.0},
    {"nombre": "Empanada (masa)", "unidad": "unidades", "cantidad": 200.0},
    {"nombre": "Carne picada", "unidad": "kg", "cantidad": 20.0},
    {"nombre": "Cebolla", "unidad": "kg", "cantidad": 12.0},
    {"nombre": "Pan", "unidad": "unidades", "cantidad": 100.0},
    {"nombre": "Jamón serrano", "unidad": "kg", "cantidad": 15.0},
    {"nombre": "Tomate", "unidad": "kg", "cantidad": 8.0},
    {"nombre": "Harina de almendra", "unidad": "kg", "cantidad": 10.0},
    {"nombre": "Azúcar", "unidad": "kg", "cantidad": 15.0},
    {"nombre": "Huevos", "unidad": "docenas", "cantidad": 25.0},
    {"nombre": "Grelos", "unidad": "kg", "cantidad": 8.0},
    {"nombre": "Chorizo", "unidad": "kg", "cantidad": 6.0},
    {"nombre": "Vino Albariño", "unidad": "botellas", "cantidad": 30.0},
    {"nombre": "Vino Ribeiro", "unidad": "botellas", "cantidad": 25.0},
    {"nombre": "Agua", "unidad": "botellas", "cantidad": 100.0},
    {"nombre": "Café", "unidad": "kg", "cantidad": 5.0},
    {"nombre": "Cerveza", "unidad": "botellas", "cantidad": 80.0}
]

# Pedidos de ejemplo
PEDIDOS_MESA = [
    {
        "numero_mesa": 1,
        "productos": ["Pulpo a la Gallega", "Albariño", "Tarta de Santiago"]
    },
    {
        "numero_mesa": 2,
        "productos": ["Empanada Gallega", "Empanada Gallega", "Cerveza Estrella Galicia", "Cerveza Estrella Galicia"]
    },
    {
        "numero_mesa": 3,
        "productos": ["Caldo Gallego", "Bocadillo de Jamón", "Agua Mineral"]
    },
    {
        "numero_mesa": 4,
        "productos": ["Pulpo a la Gallega", "Pulpo a la Gallega", "Ribeiro", "Tarta de Santiago", "Café"]
    },
    {
        "numero_mesa": 5,
        "productos": ["Empanada Gallega", "Caldo Gallego", "Agua Mineral", "Café"]
    }
]

PEDIDOS_DELIVERY = [
    {
        "direccion": "Calle Real 123, Santiago",
        "telefono": "981-123-456",
        "productos": ["Empanada Gallega", "Empanada Gallega", "Empanada Gallega", "Cerveza Estrella Galicia"]
    },
    {
        "direccion": "Avenida de Compostela 45, A Coruña",
        "telefono": "981-234-567",
        "productos": ["Pulpo a la Gallega", "Tarta de Santiago", "Agua Mineral"]
    },
    {
        "direccion": "Plaza de España 7, Vigo",
        "telefono": "986-345-678",
        "productos": ["Bocadillo de Jamón", "Bocadillo de Jamón", "Agua Mineral", "Agua Mineral"]
    }
]

def registrar_usuarios():
    """Registra usuarios en el sistema"""
    print_section("📝 REGISTRANDO USUARIOS")
    
    tokens = {}
    
    for user in USUARIOS:
        try:
            response = requests.post(
                f"{API_URL}/auth/register",
                json=user
            )
            
            if response.status_code == 201:
                print_success(f"Usuario '{user['username']}' ({user['rol']}) registrado")
                
                # Iniciar sesión para obtener token
                login_response = requests.post(
                    f"{API_URL}/auth/login",
                    data={
                        "username": user['username'],
                        "password": user['password']
                    }
                )
                
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    tokens[user['username']] = token_data['access_token']
                    print_info(f"  Token obtenido para {user['username']}")
            else:
                error = response.json()
                print_error(f"Error registrando '{user['username']}': {error.get('detail', 'Error desconocido')}")
        
        except Exception as e:
            print_error(f"Error conectando con API al registrar '{user['username']}': {str(e)}")
    
    return tokens

def crear_productos(admin_token, ingredientes_map):
    """Crea productos en el menú con recetas vinculadas a ingredientes"""
    print_section("🍽️ CREANDO PRODUCTOS DEL MENÚ")
    
    # Mapeo de productos a sus ingredientes
    RECETAS = {
        "Pulpo a la Gallega": {
            "Pulpo": 0.3,
            "Papas": 0.4,
            "Aceite de oliva": 0.05,
            "Pimentón": 0.02
        },
        "Empanada Gallega": {
            "Empanada (masa)": 1,
            "Carne picada": 0.15,
            "Cebolla": 0.05
        },
        "Bocadillo de Jamón": {
            "Pan": 1,
            "Jamón serrano": 0.08,
            "Tomate": 0.05
        },
        "Tarta de Santiago": {
            "Harina de almendra": 0.2,
            "Azúcar": 0.15,
            "Huevos": 0.25
        },
        "Caldo Gallego": {
            "Papas": 0.3,
            "Grelos": 0.2,
            "Chorizo": 0.1
        },
        "Albariño": {
            "Vino Albariño": 1
        },
        "Ribeiro": {
            "Vino Ribeiro": 1
        },
        "Agua Mineral": {
            "Agua": 1
        },
        "Café": {
            "Café": 0.02
        },
        "Cerveza Estrella Galicia": {
            "Cerveza": 1
        }
    }
    
    productos_ids = {}
    
    for producto in PRODUCTOS:
        try:
            # Preparar datos del producto con receta si existe
            producto_data = producto.copy()
            
            # Agregar receta con IDs de ingredientes si existe
            if producto['nombre'] in RECETAS:
                receta_con_ids = {}
                for ing_nombre, cantidad in RECETAS[producto['nombre']].items():
                    if ing_nombre in ingredientes_map:
                        receta_con_ids[ingredientes_map[ing_nombre]] = cantidad
                
                if receta_con_ids:
                    producto_data['receta'] = receta_con_ids
            
            response = requests.post(
                f"{API_URL}/menu/productos",
                json=producto_data,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            if response.status_code == 201:
                data = response.json()
                producto_id = data['id']
                productos_ids[producto['nombre']] = producto_id
                print_success(f"Producto '{producto['nombre']}' creado (€{producto['precio']})")
                
                # Mostrar info de receta
                if 'receta' in producto_data:
                    print_info(f"  → Receta: {len(producto_data['receta'])} ingredientes vinculados")
            else:
                error = response.json()
                print_error(f"Error creando '{producto['nombre']}': {error.get('detail', 'Error desconocido')}")
        
        except Exception as e:
            print_error(f"Error conectando con API al crear '{producto['nombre']}': {str(e)}")
    
    return productos_ids

def crear_ingredientes(admin_token):
    """Crea ingredientes en el inventario y retorna mapeo nombre->id"""
    print_section("📦 CREANDO INGREDIENTES DEL INVENTARIO")
    
    ingredientes_map = {}
    
    for ingrediente in INGREDIENTES:
        try:
            response = requests.post(
                f"{API_URL}/inventario/ingredientes",
                json=ingrediente,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            if response.status_code == 201:
                data = response.json()
                ingredientes_map[ingrediente['nombre']] = data['id']
                print_success(f"Ingrediente '{ingrediente['nombre']}' agregado ({ingrediente['cantidad']} {ingrediente['unidad']})")
            else:
                error = response.json()
                print_error(f"Error creando '{ingrediente['nombre']}': {error.get('detail', 'Error desconocido')}")
        
        except Exception as e:
            print_error(f"Error conectando con API al crear '{ingrediente['nombre']}': {str(e)}")
    
    return ingredientes_map

def crear_pedidos(productos_ids, user_token):
    """Crea pedidos de mesa y delivery"""
    print_section("🛎️ CREANDO PEDIDOS")
    
    pedidos_ids = []
    
    # Obtener lista de productos para mapear nombres a IDs
    try:
        response = requests.get(f"{API_URL}/menu/productos")
        productos_disponibles = response.json()
        nombre_to_id = {p['nombre']: p['id'] for p in productos_disponibles}
    except:
        print_error("No se pudo obtener lista de productos")
        return pedidos_ids
    
    # Crear pedidos de mesa
    print_info("\nCreando pedidos de mesa...")
    for pedido in PEDIDOS_MESA:
        items = []
        for producto_nombre in pedido['productos']:
            if producto_nombre in nombre_to_id:
                items.append({
                    "producto_id": nombre_to_id[producto_nombre],
                    "cantidad": 1
                })
        
        if items:
            try:
                response = requests.post(
                    f"{API_URL}/pedidos/mesa",
                    json={
                        "numero_mesa": pedido['numero_mesa'],
                        "items": items
                    },
                    headers={"Authorization": f"Bearer {user_token}"}
                )
                
                if response.status_code == 201:
                    data = response.json()
                    pedidos_ids.append(data['id'])
                    print_success(f"Pedido mesa {pedido['numero_mesa']} creado - Total: €{data['total']:.2f}")
                else:
                    error = response.json()
                    print_error(f"Error creando pedido mesa {pedido['numero_mesa']}: {error.get('detail', 'Error')}")
            except Exception as e:
                print_error(f"Error al crear pedido mesa {pedido['numero_mesa']}: {str(e)}")
    
    # Crear pedidos delivery
    print_info("\nCreando pedidos delivery...")
    for pedido in PEDIDOS_DELIVERY:
        items = []
        for producto_nombre in pedido['productos']:
            if producto_nombre in nombre_to_id:
                items.append({
                    "producto_id": nombre_to_id[producto_nombre],
                    "cantidad": 1
                })
        
        if items:
            try:
                response = requests.post(
                    f"{API_URL}/pedidos/delivery",
                    json={
                        "direccion": pedido['direccion'],
                        "telefono": pedido['telefono'],
                        "items": items
                    },
                    headers={"Authorization": f"Bearer {user_token}"}
                )
                
                if response.status_code == 201:
                    data = response.json()
                    pedidos_ids.append(data['id'])
                    print_success(f"Pedido delivery a '{pedido['direccion'][:30]}...' - Total: €{data['total']:.2f}")
                else:
                    error = response.json()
                    print_error(f"Error creando pedido delivery: {error.get('detail', 'Error')}")
            except Exception as e:
                print_error(f"Error al crear pedido delivery: {str(e)}")
    
    return pedidos_ids

def procesar_pedidos(pedidos_ids, user_token):
    """Cambia estado de pedidos y cobra algunos"""
    print_section("⚙️ PROCESANDO PEDIDOS")
    
    # Cambiar algunos pedidos a "en_preparacion"
    for i, pedido_id in enumerate(pedidos_ids[:5]):
        try:
            response = requests.patch(
                f"{API_URL}/pedidos/{pedido_id}/estado?nuevo_estado=EN_PREPARACION",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            if response.ok:
                print_success(f"Pedido {i+1} → EN_PREPARACION")
        except:
            pass
        
        time.sleep(0.1)
    
    # Cambiar algunos a "listo"
    for i, pedido_id in enumerate(pedidos_ids[:3]):
        try:
            response = requests.patch(
                f"{API_URL}/pedidos/{pedido_id}/estado?nuevo_estado=LISTO",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            if response.ok:
                print_success(f"Pedido {i+1} → LISTO")
        except:
            pass
        
        time.sleep(0.1)
    
    # Cobrar los pedidos listos
    print_info("\nCobrando pedidos...")
    metodos_pago = ["efectivo", "tarjeta", "efectivo"]
    
    for i, pedido_id in enumerate(pedidos_ids[:3]):
        metodo = metodos_pago[i % len(metodos_pago)]
        
        try:
            response = requests.post(
                f"{API_URL}/caja/cobrar/{pedido_id}",
                json={"metodo_pago": metodo},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Pedido {i+1} cobrado ({metodo}) - €{data['total']:.2f}")
        except Exception as e:
            print_error(f"Error cobrando pedido {i+1}: {str(e)}")
        
        time.sleep(0.1)

def mostrar_resumen(admin_token):
    """Muestra resumen del sistema"""
    print_section("📊 RESUMEN DEL SISTEMA")
    
    try:
        # Usuarios
        response = requests.get(f"{API_URL}/auth/users")
        usuarios = response.json()
        print_info(f"👥 Usuarios registrados: {len(usuarios)}")
        
        # Productos
        response = requests.get(f"{API_URL}/menu/productos")
        productos = response.json()
        print_info(f"🍽️  Productos en menú: {len(productos)}")
        
        # Ingredientes
        response = requests.get(
            f"{API_URL}/inventario/ingredientes",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        ingredientes = response.json()
        print_info(f"📦 Ingredientes en inventario: {len(ingredientes)}")
        
        # Pedidos
        response = requests.get(
            f"{API_URL}/pedidos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        pedidos = response.json()
        print_info(f"🛎️  Pedidos totales: {len(pedidos)}")
        
        # Facturas
        response = requests.get(
            f"{API_URL}/caja/facturas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        facturas = response.json()
        total_facturado = sum(f['total'] for f in facturas)
        print_info(f"💰 Facturas emitidas: {len(facturas)}")
        print_info(f"💵 Total facturado: €{total_facturado:.2f}")
        
        # Estado de caja
        response = requests.get(
            f"{API_URL}/caja/estado",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.ok:
            estado = response.json()
            print_info(f"🏦 Total en caja hoy: €{estado['total_dia']:.2f}")
    
    except Exception as e:
        print_error(f"Error obteniendo resumen: {str(e)}")

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("   INICIALIZADOR DE DATOS - PULPERÍA GALÁN")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info(f"API URL: {API_URL}")
    
    try:
        # 1. Registrar usuarios
        tokens = registrar_usuarios()
        
        if not tokens or 'admin' not in tokens:
            print_error("\n❌ No se pudo obtener token de administrador. Abortando.")
            return
        
        admin_token = tokens['admin']
        user_token = tokens.get('fernando_mesero', admin_token)
        
        time.sleep(0.5)
        
        # 2. Crear ingredientes primero (necesitamos sus IDs)
        ingredientes_map = crear_ingredientes(admin_token)
        time.sleep(0.5)
        
        # 3. Crear productos con recetas vinculadas
        productos_ids = crear_productos(admin_token, ingredientes_map)
        time.sleep(0.5)
        
        # 4. Crear pedidos
        pedidos_ids = crear_pedidos(productos_ids, user_token)
        time.sleep(0.5)
        
        # 5. Procesar pedidos
        if pedidos_ids:
            procesar_pedidos(pedidos_ids, user_token)
            time.sleep(0.5)
        
        # 6. Mostrar resumen
        mostrar_resumen(admin_token)
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}✓ INICIALIZACIÓN COMPLETADA EXITOSAMENTE{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}\n")
        
        print(f"{Colors.CYAN}Credenciales de acceso:{Colors.END}")
        print(f"  • Admin:    usuario='admin'         password='admin123'")
        print(f"  • Mesero:   usuario='fernando_mesero'  password='fernando123'")
        print(f"  • Cocinero: usuario='alvaro_cocinero' password='alvaro123'")
        print(f"\n{Colors.CYAN}Accede al sistema en: {Colors.BOLD}http://localhost/{Colors.END}\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Proceso interrumpido por el usuario{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}❌ Error inesperado: {str(e)}{Colors.END}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
