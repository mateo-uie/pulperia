"""
API REST para Sistema de Gestión de Pulpería Galán
"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from models.usuario import Usuario
from models.producto import Producto, Plato, Bebida
from models.pedido import EstadoPedido
from models.ingrediente import Ingrediente
from models.factura import Factura
from services.auth_service import AuthService
from services.menu_service import MenuService
from services.inventario_service import InventarioService
from services.pedidos_service import PedidosService
from services.caja_service import CajaService
from services.reportes_service import ReportesService

# Inicializar FastAPI
app = FastAPI(
    title="Pulpería Galán API",
    description="API REST para sistema de gestión de pulpería",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

# Inicializar servicios
auth_service = AuthService()
inventario_service = InventarioService()
menu_service = MenuService()
pedidos_service = PedidosService(inventario_service, menu_service)
caja_service = CajaService(pedidos_service)
reportes_service = ReportesService(caja_service, inventario_service, pedidos_service)

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ========== SCHEMAS PYDANTIC ==========

# Auth schemas
class UserRegister(BaseModel):
    """Schema para registro de usuario."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    rol: str = Field(default="empleado")


class UserLogin(BaseModel):
    """Schema para login de usuario."""
    username: str
    password: str


class Token(BaseModel):
    """Schema para respuesta de token JWT."""
    access_token: str
    token_type: str


class UserRead(BaseModel):
    """Schema para lectura de usuario (sin password)."""
    id: str
    username: str
    email: str
    rol: str
    created_at: Optional[str] = None
    is_active: bool


# Menu schemas
class ProductoCreate(BaseModel):
    """Schema para crear producto."""
    nombre: str
    precio: float
    tipo: str  # "plato" o "bebida"
    descripcion: Optional[str] = None
    tiempo_preparacion: Optional[int] = None  # para platos
    volumen: Optional[int] = None  # para bebidas


class ProductoRead(BaseModel):
    """Schema para lectura de producto."""
    id: str
    nombre: str
    precio: float
    tipo: str
    descripcion: Optional[str] = None


# Pedido schemas
class PedidoItemCreate(BaseModel):
    """Schema para item de pedido."""
    producto_id: str
    cantidad: int


class PedidoMesaCreate(BaseModel):
    """Schema para crear pedido de mesa."""
    numero_mesa: int
    items: List[PedidoItemCreate]


class PedidoDeliveryCreate(BaseModel):
    """Schema para crear pedido delivery."""
    direccion: str
    telefono: str
    items: List[PedidoItemCreate]


class PedidoItemRead(BaseModel):
    """Schema para item de pedido."""
    producto_id: str
    nombre: str
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    """Schema para lectura de pedido."""
    id: str
    tipo: str
    estado: str
    fecha: str
    total: float
    items: List[PedidoItemRead]
    numero_mesa: Optional[int] = None
    direccion: Optional[str] = None


# Inventario schemas
class IngredienteRead(BaseModel):
    """Schema para lectura de ingrediente."""
    id: str
    nombre: str
    unidad: str
    cantidad: float


class IngredienteCreate(BaseModel):
    """Schema para crear ingrediente."""
    nombre: str
    unidad: str
    cantidad: float


class IngredienteReponer(BaseModel):
    """Schema para reponer stock."""
    cantidad: float


# Caja schemas
class CobrarPedidoRequest(BaseModel):
    """Schema para cobrar un pedido."""
    metodo_pago: str = Field(default="efectivo")


class FacturaRead(BaseModel):
    """Schema para lectura de factura."""
    id: str
    pedido_id: str
    fecha: str
    total: float
    metodo_pago: str


# ========== DEPENDENCIAS ==========

def get_current_user(token: str = Depends(oauth2_scheme)) -> Usuario:
    """
    Obtiene el usuario actual desde el token JWT.
    
    Args:
        token (str): Token JWT.
        
    Returns:
        Usuario: Usuario autenticado.
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe.
    """
    username = auth_service.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Verifica que el usuario actual sea administrador.
    
    Args:
        current_user (Usuario): Usuario actual.
        
    Returns:
        Usuario: Usuario si es administrador.
        
    Raises:
        HTTPException: Si el usuario no es administrador.
    """
    if not current_user.es_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


# ========== ENDPOINTS DE AUTENTICACIÓN ==========

@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(datos: UserRegister):
    """
    Registra un nuevo usuario.
    
    Args:
        datos (UserRegister): Datos del usuario.
        
    Returns:
        UserRead: Usuario registrado.
    """
    try:
        user = auth_service.create_user(
            username=datos.username,
            email=datos.email,
            password=datos.password,
            rol=datos.rol
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    return UserRead(
        id=str(user.id),
        username=user.username,
        email=user.email,
        rol=user.rol,
        created_at=user.created_at.isoformat() if user.created_at else None,
        is_active=user.is_active
    )


@app.post("/auth/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login con credenciales para obtener token JWT.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Username y password.
        
    Returns:
        Token: Token JWT de acceso.
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/users", response_model=List[UserRead])
def list_users():
    """
    Lista todos los usuarios registrados.
    
    Returns:
        List[UserRead]: Lista de usuarios.
    """
    users = auth_service.list_users()
    return [
        UserRead(
            id=str(user.id),
            username=user.username or user.nombre,
            email=user.email,
            rol=user.rol,
            created_at=user.created_at.isoformat() if user.created_at else None,
            is_active=user.is_active
        )
        for user in users
    ]


@app.get("/auth/me", response_model=UserRead)
def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene información del usuario actual.
    
    Args:
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        UserRead: Información del usuario.
    """
    return UserRead(
        id=str(current_user.id),
        username=current_user.username or current_user.nombre,
        email=current_user.email,
        rol=current_user.rol,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
        is_active=current_user.is_active
    )


# ========== ENDPOINTS DE MENÚ ==========

@app.get("/menu/productos", response_model=List[ProductoRead])
def listar_productos():
    """
    Lista todos los productos del menú.
    
    Returns:
        List[ProductoRead]: Lista de productos.
    """
    productos = menu_service.listar_productos()
    return [
        ProductoRead(
            id=producto.id,
            nombre=producto.nombre,
            precio=producto.precio,
            tipo=producto.__class__.__name__.lower(),
            descripcion=getattr(producto, 'descripcion', None)
        )
        for producto in productos
    ]


@app.post("/menu/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate, current_user: Usuario = Depends(require_admin)):
    """
    Crea un nuevo producto en el menú (requiere admin).
    
    Args:
        datos (ProductoCreate): Datos del producto.
        current_user (Usuario): Usuario administrador.
        
    Returns:
        ProductoRead: Producto creado.
    """
    try:
        if datos.tipo.lower() == "plato":
            producto = Plato(
                nombre=datos.nombre,
                precio=datos.precio,
                descripcion=datos.descripcion or "",
                categoria="Principal"
            )
        elif datos.tipo.lower() == "bebida":
            producto = Bebida(
                nombre=datos.nombre,
                precio=datos.precio,
                descripcion=datos.descripcion or "",
                alcoholica=False
            )
        else:
            raise HTTPException(status_code=400, detail="Tipo de producto inválido. Use 'plato' o 'bebida'")
        
        menu_service.agregar_producto(producto)
        
        return ProductoRead(
            id=producto.id,
            nombre=producto.nombre,
            precio=producto.precio,
            tipo=datos.tipo.lower(),
            descripcion=datos.descripcion
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.delete("/menu/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: str, current_user: Usuario = Depends(require_admin)):
    """
    Elimina un producto del menú (requiere admin).
    
    Args:
        producto_id (str): ID del producto.
        current_user (Usuario): Usuario administrador.
    """
    if not menu_service.eliminar_producto(producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")


# ========== ENDPOINTS DE INVENTARIO ==========

@app.get("/inventario/ingredientes", response_model=List[IngredienteRead])
def listar_ingredientes(current_user: Usuario = Depends(get_current_user)):
    """
    Lista todos los ingredientes del inventario (requiere autenticación).
    
    Args:
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        List[IngredienteRead]: Lista de ingredientes.
    """
    ingredientes = inventario_service.listar_ingredientes()
    return [
        IngredienteRead(
            id=ing.id,
            nombre=ing.nombre,
            unidad=ing.unidad,
            cantidad=ing.cantidad
        )
        for ing in ingredientes
    ]


@app.post("/inventario/ingredientes", response_model=IngredienteRead, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(datos: IngredienteCreate, current_user: Usuario = Depends(require_admin)):
    """
    Crea un nuevo ingrediente en el inventario (requiere admin).
    
    Args:
        datos (IngredienteCreate): Datos del ingrediente.
        current_user (Usuario): Usuario administrador.
        
    Returns:
        IngredienteRead: Ingrediente creado.
    """
    try:
        ingrediente = Ingrediente(
            nombre=datos.nombre,
            unidad=datos.unidad,
            cantidad=datos.cantidad
        )
        inventario_service.agregar_ingrediente(ingrediente)
        
        return IngredienteRead(
            id=ingrediente.id,
            nombre=ingrediente.nombre,
            unidad=ingrediente.unidad,
            cantidad=ingrediente.cantidad
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.patch("/inventario/ingredientes/{ingrediente_id}/reponer")
def reponer_stock(ingrediente_id: str, datos: IngredienteReponer, current_user: Usuario = Depends(require_admin)):
    """
    Repone el stock de un ingrediente (requiere admin).
    
    Args:
        ingrediente_id (str): ID del ingrediente.
        datos (IngredienteReponer): Cantidad a reponer.
        current_user (Usuario): Usuario administrador.
        
    Returns:
        dict: Mensaje de confirmación.
    """
    if not inventario_service.reponer_stock(ingrediente_id, datos.cantidad):
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    
    ingrediente = inventario_service.obtener_ingrediente(ingrediente_id)
    return {
        "message": "Stock repuesto correctamente",
        "ingrediente": ingrediente.nombre,
        "cantidad_actual": ingrediente.cantidad
    }


# ========== ENDPOINTS DE PEDIDOS ==========

@app.post("/pedidos/mesa", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido_mesa(datos: PedidoMesaCreate, current_user: Usuario = Depends(get_current_user)):
    """
    Crea un pedido de mesa (requiere autenticación).
    
    Args:
        datos (PedidoMesaCreate): Datos del pedido.
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        PedidoRead: Pedido creado.
    """
    productos_cantidades = {item.producto_id: item.cantidad for item in datos.items}
    exito, msg, pedido = pedidos_service.crear_pedido_mesa(datos.numero_mesa, productos_cantidades)
    
    if not exito:
        raise HTTPException(status_code=400, detail=msg)
    
    # Convertir items a schema
    items_read = []
    for item in pedido.items:
        items_read.append(PedidoItemRead(
            producto_id=item.producto_id,
            nombre=item.nombre_producto,
            cantidad=item.cantidad,
            subtotal=item.subtotal()
        ))
    
    return PedidoRead(
        id=pedido.id,
        tipo="mesa",
        estado=pedido.estado.value,
        fecha=pedido.fecha.isoformat(),
        total=pedido.calcular_total(),
        items=items_read,
        numero_mesa=datos.numero_mesa
    )


@app.post("/pedidos/delivery", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido_delivery(datos: PedidoDeliveryCreate, current_user: Usuario = Depends(get_current_user)):
    """
    Crea un pedido delivery (requiere autenticación).
    
    Args:
        datos (PedidoDeliveryCreate): Datos del pedido.
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        PedidoRead: Pedido creado.
    """
    productos_cantidades = {item.producto_id: item.cantidad for item in datos.items}
    exito, msg, pedido = pedidos_service.crear_pedido_delivery(
        datos.direccion,
        datos.telefono,
        productos_cantidades
    )
    
    if not exito:
        raise HTTPException(status_code=400, detail=msg)
    
    # Convertir items a schema
    items_read = []
    for item in pedido.items:
        items_read.append(PedidoItemRead(
            producto_id=item.producto_id,
            nombre=item.nombre_producto,
            cantidad=item.cantidad,
            subtotal=item.subtotal()
        ))
    
    return PedidoRead(
        id=pedido.id,
        tipo="delivery",
        estado=pedido.estado.value,
        fecha=pedido.fecha.isoformat(),
        total=pedido.calcular_total(),
        items=items_read,
        direccion=datos.direccion
    )


@app.get("/pedidos", response_model=List[PedidoRead])
def listar_pedidos(current_user: Usuario = Depends(get_current_user)):
    """
    Lista todos los pedidos (requiere autenticación).
    
    Args:
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        List[PedidoRead]: Lista de pedidos.
    """
    pedidos = list(pedidos_service.pedidos.values())
    result = []
    
    for pedido in pedidos:
        items_read = []
        for item in pedido.items:
            items_read.append(PedidoItemRead(
                producto_id=item.producto_id,
                nombre=item.nombre_producto,
                cantidad=item.cantidad,
                subtotal=item.subtotal()
            ))
        
        pedido_dict = {
            "id": pedido.id,
            "tipo": pedido.tipo,
            "estado": pedido.estado.value,
            "fecha": pedido.fecha.isoformat(),
            "total": pedido.calcular_total(),
            "items": items_read
        }
        
        # Agregar número de mesa si es pedido de mesa
        if pedido.tipo == "mesa" and pedido.mesa_id:
            # Buscar el número de mesa desde el ID
            for mesa in pedidos_service.mesas.values():
                if mesa.id == pedido.mesa_id:
                    pedido_dict["numero_mesa"] = mesa.numero
                    break
        
        # Agregar dirección si es pedido delivery
        if pedido.tipo == "delivery" and pedido.direccion_delivery:
            pedido_dict["direccion"] = pedido.direccion_delivery
        
        result.append(PedidoRead(**pedido_dict))
    
    return result


@app.patch("/pedidos/{pedido_id}/estado")
def cambiar_estado_pedido(
    pedido_id: str,
    nuevo_estado: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambia el estado de un pedido (requiere autenticación).
    
    Args:
        pedido_id (str): ID del pedido.
        nuevo_estado (str): Nuevo estado del pedido.
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        dict: Mensaje de confirmación.
    """
    try:
        pedidos_service.cambiar_estado_pedido(pedido_id, nuevo_estado)
        return {"message": f"Estado del pedido {pedido_id} cambiado a {nuevo_estado}"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ========== ENDPOINTS DE CAJA ==========

@app.post("/caja/cobrar/{pedido_id}", response_model=FacturaRead)
def cobrar_pedido(pedido_id: str, datos: CobrarPedidoRequest, current_user: Usuario = Depends(get_current_user)):
    """
    Cobra un pedido y genera su factura (requiere autenticación).
    
    Args:
        pedido_id (str): ID del pedido.
        datos (CobrarPedidoRequest): Método de pago.
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        FacturaRead: Factura generada.
    """
    exito, mensaje, factura = caja_service.cobrar_pedido(pedido_id, datos.metodo_pago)
    
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    
    return FacturaRead(
        id=factura.id,
        pedido_id=factura.pedido_id,
        fecha=factura.fecha.isoformat(),
        total=factura.total,
        metodo_pago=factura.metodo_pago
    )


@app.get("/caja/facturas", response_model=List[FacturaRead])
def listar_facturas(current_user: Usuario = Depends(get_current_user)):
    """
    Lista todas las facturas (requiere autenticación).
    
    Args:
        current_user (Usuario): Usuario autenticado.
        
    Returns:
        List[FacturaRead]: Lista de facturas.
    """
    facturas = caja_service.listar_facturas()
    return [
        FacturaRead(
            id=fac.id,
            pedido_id=fac.pedido_id,
            fecha=fac.fecha.isoformat(),
            total=fac.total,
            metodo_pago=fac.metodo_pago
        )
        for fac in facturas
    ]


@app.get("/caja/estado")
def estado_caja(current_user: Usuario = Depends(require_admin)):
    """
    Obtiene el estado actual de la caja (requiere admin).
    
    Args:
        current_user (Usuario): Usuario administrador.
        
    Returns:
        dict: Estado de la caja con totales por método de pago.
    """
    total_dia = caja_service.obtener_total_dia()
    facturas = caja_service.listar_facturas()
    
    # Calcular totales por método de pago
    totales_por_metodo = {}
    for fac in facturas:
        metodo = fac.metodo_pago
        if metodo not in totales_por_metodo:
            totales_por_metodo[metodo] = 0
        totales_por_metodo[metodo] += fac.total
    
    return {
        "total_dia": total_dia,
        "total_facturas": len(facturas),
        "totales_por_metodo": totales_por_metodo
    }


# ========== ENDPOINTS DE REPORTES ==========

@app.get("/reportes/ventas")
def reporte_ventas(current_user: Usuario = Depends(require_admin)):
    """
    Genera reporte de ventas del día (requiere admin).
    
    Args:
        current_user (Usuario): Usuario administrador.
        
    Returns:
        dict: Reporte de ventas.
    """
    try:
        return reportes_service.reporte_ventas_del_dia()
    except Exception as e:
        print(f"Error en reporte de ventas: {e}")
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "total_ventas": 0.0,
            "cantidad_pedidos": 0,
            "ticket_promedio": 0.0
        }


@app.get("/reportes/productos-mas-vendidos")
def productos_mas_vendidos(limit: int = 10, current_user: Usuario = Depends(require_admin)):
    """
    Obtiene los productos más vendidos (requiere admin).
    
    Args:
        limit (int): Cantidad de productos a retornar.
        current_user (Usuario): Usuario administrador.
        
    Returns:
        list: Lista de productos más vendidos.
    """
    try:
        top = reportes_service.platos_mas_vendidos(limit)
        return [
            {
                "nombre": nombre,
                "cantidad": cantidad,
                "ingredientes": ingredientes
            }
            for nombre, cantidad, ingredientes in top
        ]
    except Exception as e:
        print(f"Error en productos más vendidos: {e}")
        return []


@app.get("/reportes/alertas-stock")
def alertas_stock(current_user: Usuario = Depends(require_admin)):
    """
    Obtiene alertas de productos con stock bajo (requiere admin).
    
    Args:
        current_user (Usuario): Usuario administrador.
        
    Returns:
        list: Lista de alertas de stock.
    """
    try:
        return reportes_service.alertas_bajo_stock()
    except Exception as e:
        print(f"Error en alertas de stock: {e}")
        return []


# ========== ROOT ==========

@app.get("/")
def root():
    """Sirve el frontend HTML."""
    return FileResponse("index.html")

@app.get("/styles.css")
def styles():
    """Sirve el archivo CSS."""
    return FileResponse("styles.css", media_type="text/css")

@app.get("/api")
def api_info():
    """Endpoint con información de la API."""
    return {
        "message": "Pulpería Galán API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth/*",
            "menu": "/menu/*",
            "pedidos": "/pedidos/*",
            "reportes": "/reportes/*",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
