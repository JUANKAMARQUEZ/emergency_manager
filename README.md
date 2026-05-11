# 🚨 Emergency Manager

Aplicación web desarrollada con Flask para la gestión de emergencias e incidencias.

## 📌 Descripción

Emergency Manager es una aplicación orientada a la gestión de incidencias, recursos y usuarios, permitiendo controlar emergencias mediante un mapa interactivo y un sistema de gestión completo.

El proyecto ha sido desarrollado como Trabajo Fin de Grado (TFG) del ciclo Desarrollo de Aplicaciones Web (DAW).

---

## 🚀 Funcionalidades

### 👤 Gestión de usuarios

- Inicio y cierre de sesión
- Roles de usuario
- Administración de usuarios
- Contraseñas cifradas con PBKDF2

### 🚨 Gestión de incidencias

- Crear incidencias
- Gestionar incidencias
- Finalizar incidencias
- Resoluciones
- Filtros por estado
- Historial de incidencias

### 🚓 Gestión de recursos

- Asignación de recursos
- Control de recursos ocupados
- Liberación automática al finalizar incidencias

### 🗺️ Mapa interactivo

- Geolocalización de incidencias
- Visualización mediante Leaflet y OpenStreetMap

---

## 🛠️ Tecnologías utilizadas

- Python
- Flask
- SQLAlchemy
- Flask-Login
- MySQL
- Bootstrap 5
- Leaflet
- HTML5
- CSS3
- JavaScript

---

## 🔐 Seguridad

- Contraseñas cifradas mediante PBKDF2
- Validación de formularios
- Control de acceso por roles
- Protección de rutas mediante login_required

---

## 📷 Capturas

### Dashboard

![(Añadir captura)](capturas/dashboard.png)

### Gestión de incidencias

(Añadir captura)

### Mapa interactivo

(Añadir captura)

---

## ⚙️ Instalación

### 1️⃣ Clonar repositorio

```bash
git clone https://github.com/JUANKAMARQUEZ/emergency_manager.git
```

### 2️⃣ Crear entorno virtual

```bash
python -m venv venv
```

### 3️⃣ Activar entorno virtual

#### Windows

```bash
venv\Scripts\activate
```

### 4️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5️⃣ Ejecutar aplicación

```bash
python run.py
```

---

## 👨‍💻 Autor

Juan Carlos Márquez Romero

Proyecto desarrollado como TFG DAW.