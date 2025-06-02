
Autor: Justino Daniel Guerrero Rivera

***
# museo_bot: Proyecto para la materia de AI y Backend 1
Este proyecto proposito del proyecto es un bot que sirva como tipo guia turistico, pero que brinde informacion mas detallada dandole un tipo de realidad aumentada con Imagen, Video, Audio o Textos(datos curiosos) de las obras.

#Funcionamiento
-Analiis de fotos por comparacion con banco de imagenes de las obras **(En desarrollo)**
-Analsis de texto de fotos para mejorar la identificacion de la obra, en caso de que se este una placa con detalles de la obra **(En desarrollo)**
-Busqueda por QR personalizado: se añadio la funcion para porcesar el codigo QR con idenficador unico (UUID) de esa forma se realizara una peticion a la API para obtener datos de esa obra

-se creo una pequeña API con FastAPI para que en futuro se pueda integrar en un proyecto mas robusto, integrando funciones de Realidad Aumentad (AR)

## Requisitos

- Python 3.9 o superior
- pip
- PostgreSQL 14.18 

## Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/licandragon/museo_bot.git
cd proyecto_torres_meteorologicas
python -m venv venv
source venv/bin/activate
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```
### 3. Importar base de datos
Crea una base de datos en PostgreSQL con el nombre **museo** y ejecutar el query del archivo database.sql

### 3. Configura las variables de entorno

Renombra el archivo `.env.example` por `.env` y configura las variables de entorno:
-Genera la token del bot con @BotFather en telegram
-Genera un API_KEY con el comando
-Configura los datos para el acceso a la base de datos

```
# Configuración del Bot
BOT_TOKEN="token_de_telegram"

# Configuración de la API
API_BASE_URL="http://localhost:8000"
API_KEY_NAME = "X-API-Key"
API_KEY= "clave_secreta_api"   #openssl rand -hex 16

# Base de Datos (PostgreSQL)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=museum
```
