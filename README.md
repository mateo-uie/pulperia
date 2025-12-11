# Sistema de Gestión - Pulpería Galán

API REST con arquitectura de 3 capas para gestión de restaurantes. Incluye autenticación JWT, control de roles (Admin, Mesero, Cocinero), gestión de pedidos con verificación automática de recetas, y sistema de facturación completo.

## Características

- **Autenticación JWT** con refresh tokens
- **Control de roles**: Admin, Mesero, Cocinero
- **Gestión de menú** con recetas y stock
- **Verificación automática** de ingredientes al crear pedidos
- **Flujo de estados**: PENDIENTE → EN_PREPARACION → LISTO → COBRADO
- **Sistema de facturación** con métodos de pago
- **Reportes de ventas** y estadísticas
- **Frontend SPA** con diseño responsive

## Ejecutar aplicación

### Con Docker:

#### Construir imagen:
```bash
docker build -t pulperia-galan .
```
#### Ejecutar imagen:

```bash
docker run --name pulperia-galan -p 80:80 -v $(pwd)/data:/app/data pulperia-galan
```

#### Crear usuarios, menus y pedidos de prueba (opcional):
```bash
python3 init_data.py
```

#### Acceder a la url:

```bash
http:/localhost/
```
### Sin Docker

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python3 main.py

# Inicializar datos (opcional)
python3 init_data.py

# Acceder
http://localhost
```
### Comandos adicionales de docker
#### Ver logs

```bash
docker logs -f pulperia-galan
```

#### Detener el contenedor

```bash
docker stop pulperia-galan
```

#### Eliminar el contenedor

```bash
docker rm pulperia-galan
```

## 📋 Funcionalidades por Rol

### Admin
- Gestión completa de usuarios, productos e ingredientes
- Acceso a todos los reportes y estadísticas
- Configuración del sistema

### Mesero
- Crear y visualizar pedidos
- Cobrar pedidos listos (Caja)
- Consultar menú disponible

### Cocinero
- Ver pedidos pendientes
- Cambiar estados: PENDIENTE → EN_PREPARACION → LISTO
- Consultar recetas e ingredientes

## 🏗️ Arquitectura

**Capa de Presentación**: Frontend SPA (HTML/CSS/JS)  
**Capa de Negocio**: API REST con FastAPI  
**Capa de Datos**: TinyDB (JSON persistente)

## 🔑 Características Técnicas

- **API REST** con FastAPI y Uvicorn
- **Autenticación JWT** (access + refresh tokens)
- **Validación automática** de recetas al crear pedidos
- **Descuento automático** de stock al confirmar pedidos
- **Base de datos** TinyDB con persistencia en JSON
- **CORS** habilitado para desarrollo
- **Documentación** automática en `/docs`

