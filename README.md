# API REST - Sistema de Punto de Venta (POS)

## Descripción

Este API REST está destinado a un sistema de gestion de las madre beneficiarias de acovichay alto con funcionalidades principales como:

- Manejo de los productos ingresantes al almacén.
- Registro y actualizacion de los datos de las beneficiarias participes.
- Control y seguimiento de la caja tanto entradas como salidas.
- Registro de asistencias por reuniones organizadas.
- Registro y asiganción de multas por diversas multas.

### Tecnologías utilizadas:

- **Backend:** Python, Flask
- **Base de datos:** MySQL, SQLAlchemy
- **Otros:** CORS, dotenv, mysqlclient

---

## Instalación

### 1. Crear un entorno virtual para Python

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

- En Windows:

```bash
venv\Scripts\activate
```

- En macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Copiar el archivo `.env.example` como `.env` y modificar los parámetros según la configuración deseada.

```bash
cp .env.example .env
```

Editar el archivo `.env` con los valores correspondientes, como las credenciales de la base de datos.

### 5. Ejecutar el servidor

```bash
python index.py
```

---

## Notas

- Asegúrate de configurar correctamente la base de datos en el archivo `.env`.
- Para pruebas, usa Postman o Thunder Client.
- El sistema requiere autenticación para la mayoría de las rutas.

---

### Autor

Desarrollado por Duran
