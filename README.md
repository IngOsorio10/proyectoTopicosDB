
# 🌱 Proyecto de Integración de Datos para el Ecoturismo en Colombia

**Autores**: Sebastián Martínez, María Montenegro, Juan Diego Osorio, Luis CarlosFernández  
**Universidad**: Pontificia Universidad Javeriana - Maestría en Inteligencia Artificial e Ing. De sistemas & Computación

**Curso**: Tópicos Avanzados en Bases de Datos

## 🧭 Descripción General

Este proyecto desarrolla una solución de integración y análisis de datos que consolida información **geoespacial, documental y relacional** para apoyar la **planificación territorial del ecoturismo** en Colombia. A través de un tablero interactivo en Power BI, se visualizan **reservas naturales**, su **accesibilidad vial**, y la **oferta de servicios turísticos** circundantes.

## 🎯 Objetivos

- Unificar datos del **Registro Nacional de Turismo (RNT)**, **reservas forestales** y **red vial** nacional.
- Identificar **brechas de conectividad** en torno a reservas naturales.
- Proveer visualizaciones interactivas que permitan **tomar decisiones basadas en evidencia** para un ecoturismo sostenible.

## 🗺️ Arquitectura

El sistema está compuesto por:

| Componente         | Descripción                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| **MongoDB Atlas**  | Almacena datos semiestructurados del RNT.                                   |
| **PostgreSQL + PostGIS (AWS RDS)** | Maneja datos geoespaciales de reservas, vías y municipios.         |
| **Google BigQuery**| Consolida datos procesados y preparados para análisis.                      |
| **API REST (FastAPI)** | Intermedia entre MongoDB y Power BI para consultas filtradas.          |
| **Power BI**       | Dashboard final con filtros, mapas y visualizaciones interactivas.          |

## 🧪 Flujo de Procesamiento

El código principal realiza las siguientes acciones:

1. 🔐 **Conexión segura** a MongoDB, PostgreSQL y BigQuery usando `dotenv`.
2. 📥 **Descarga y limpieza** de datasets abiertos desde [datos.gov.co](https://www.datos.gov.co/).
3. 🗂️ **Inserción de datos** limpios en:
   - MongoDB: establecimientos turísticos.
   - PostGIS: geometría de reservas, municipios y vías.
4. 📍 **Cálculo geoespacial**:
   - Distancia entre reservas y vías más cercanas.
   - Identificación de establecimientos turísticos dentro del polígono de reservas.
5. 🔄 **Unificación de datos** y exportación a BigQuery con esquema predefinido usando PyArrow.
6. 📊 **Consumo final** desde Power BI usando conectores ODBC y API REST.

## 🧱 Estructura de Datos

### MongoDB: `proyecto.rnt`

```json
{
  "codigo_rnt": 12345,
  "municipio": "Leticia",
  "departamento": "Amazonas",
  "categoria": "ALOJAMIENTO TURÍSTICO",
  ...
}
```

### PostGIS: Tablas

- `tramos_vias (LINESTRING)`
- `reservas (POLYGON)`
- `municipios (POLYGON)`

### BigQuery: `Proyecto.datos_consolidados`

| Columna                  | Tipo        |
|--------------------------|-------------|
| id_pnn                   | INTEGER     |
| nombre                   | STRING      |
| hectareas                | FLOAT       |
| vias_cercanas_datos      | RECORD[]    |
| alojamiento_turistico    | RECORD[]    |
| actividades_turisticas   | RECORD[]    |
| servicios_complementarios| RECORD[]    |
| ...                      | ...         |

## 📊 Dashboard Final
 [**TABLERO ECOTURISMO**](https://app.powerbi.com/onedrive/open?pbi_source=ODSPViewer&driveId=b!WhN-3GRLQka6ZX7oBgysdyMxSvBjJNtFtKc-NQrAS0FIJZdPny-WSasJS2iut6XC&itemId=01IOE4TCIIRQQ7IAYY4ZF2QR2OB54BWO53)

Este dashboard en Power BI permite:

- Filtrar por **reserva, municipio, tipo de vía y categoría turística**.
- Ver en mapas coropléticos la **accesibilidad vial** y **servicios turísticos cercanos**.
- Identificar zonas críticas con **baja conectividad y alta biodiversidad**.

Para la parte web de los datos, y todo el proceso de renderizado del mapa se realizó mediante github. ![github](data/img.png)

El proyecto utilizado es el siguiente: [***Ecoturismo_rendering***](https://github.com/Maria-mon/ecoturismo-api)


## 📎 Tecnologías Usadas

- 🐘 PostgreSQL + PostGIS
- 🍃 MongoDB Atlas
- ☁️ Google BigQuery
- 🐍 Python (pandas, geopandas, pyarrow, SQLAlchemy)
- 🚀 FastAPI
- 📊 Power BI

## 🔒 Seguridad

- Variables de entorno `.env` para credenciales sensibles.
- API con autenticación basada en tokens.
- Conexiones seguras a través de SSL y claves de servicio de Google.

## 📌 Requisitos Previos

- Python 3.10+
- `.env` con las siguientes variables:
  ```env
  MONGODB_USER=
  MONGODB_KEY=
  AWS_PASS=
  DB_NAME=
  DB_USER=
  DB_HOST=
  DB_PORT=
  GOOGLE_APPLICATION_CREDENTIALS=
  ```

## 🚀 Cómo Ejecutar

```bash
pip install -r requirements.txt
python main.py
```

## 📁 Estructura del Repositorio

```
📦 ecoturismo-colombia
 ┣ 📜 main.py
 ┣ 📜 .env
 ┣ 📜 README.md
 ┗ 📁 data/
  ┗ 📜 infraestructuravial_.geojson
```

## 🧭 Futuro

- Agregar paneles de monitoreo de biodiversidad.
- Incorporar predicción de flujos turísticos.
- Integrar datos de sensores IoT y alertas ambientales.
