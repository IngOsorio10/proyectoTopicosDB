import json
import os

import pandas as pd
import geopandas as gpd
import pyarrow as pa
import requests

from dotenv import load_dotenv
from google.cloud import bigquery
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from shapely.geometry import Point, shape
from sqlalchemy import create_engine, text

def main():
    load_dotenv()

    username = os.getenv("MONGODB_USER")
    password = os.getenv("MONGODB_KEY")

    if not username or not password:
        raise ValueError("Las variables de entorno MONGODB_USER o MONGODB_KEY no están definidas.")

    # URI de conexión
    uri = f"mongodb+srv://{username}:{password}@cluster0.nmdqner.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Crear cliente MongoDB con Server API v1
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Verificar la conexión
    try:
        client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB!")
    except Exception as e:
        print("❌ Error al conectar con MongoDB:")
        print(e)


    url = "https://www.datos.gov.co/resource/thwd-ivmp.json?$limit=200000"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta error si status no es 200

        data = response.json()

        if not isinstance(data, list):
            print("Los datos NO son una lista.")
            print("Tipo de datos:", type(data))
            print("Contenido de los datos:", data)
            data = []  # Evitar errores si no es lista

    except requests.exceptions.RequestException as e:
        print("Error al descargar el archivo:", e)
        data = []
    except ValueError as e:
        print("Error al interpretar JSON:", e)
        data = []

    # Solo procesar si tenemos datos válidos
    if data:
        for record in data:
            try:
                # Casteo seguro, chequea si las claves existen y si el valor es convertible
                record['codigo_rnt'] = int(record.get('codigo_rnt', 0))
                record['cod_mun'] = int(record.get('cod_mun', 0))
                record['cod_dpto'] = int(record.get('cod_dpto', 0))
                record['habitaciones'] = int(record.get('habitaciones', 0))
                record['camas'] = int(record.get('camas', 0))
                record['num_emp1'] = int(record.get('num_emp1', 0))

                # Para la fecha, asegurarse de que 'ano' y 'mes' existan y sean válidos
                ano = record.get('ano')
                mes = record.get('mes')
                if ano and mes:
                    record['fecha_registro'] = pd.to_datetime(f"{ano}-{mes}-01", errors='coerce').to_pydatetime()
                else:
                    record['fecha_registro'] = None

            except (ValueError, TypeError) as e:
                print(f"Error al castear registro {record}: {e}")

        # Inserción a MongoDB
        db = client['proyecto']
        collection = db['rnt']

        try:
            collection.insert_many(data)
            print("Datos insertados en MongoDB.")
        except Exception as e:
            print("Error al insertar datos en MongoDB:", e)
    else:
        print("No hay datos válidos para procesar.")


    # URL del archivo JSON
    url = "https://www.datos.gov.co/resource/9a89-px8u.json?$limit=200000"

    # Descargar el contenido del archivo
    response = requests.get(url)

    # Verificar si la descarga fue exitosa
    if response.status_code == 200:
        data = response.json()  # Cargar el JSON en memoria
        print("JSON descargado con éxito.")

        # Verificar si 'data' es una lista
        if isinstance(data, list):
            print("Los datos son una lista.")
        else:
            print("Los datos NO son una lista.")
            print("Tipo de datos:", type(data))

        # Opcional: Imprimir la estructura de los primeros elementos si no es una lista
        if not isinstance(data, list):
            print("Contenido de los datos:", data)

    else:
        print("Error al descargar el archivo:", response.status_code)

    for record in data:
        record['fid'] = int(record['fid'])
        record['objectid'] = int(record['objectid'])
        record['id_pnn'] = int(record['id_pnn'])
        record['resoluci_n'] = int(record['resoluci_n'])
        record['hectareas'] = float(record['hectareas'])
        record['wkid'] = int(record['wkid'])
        record['app_id'] = int(record['app_id'])
        record['record_id'] = int(record['record_id'])
        record['fecha_regi'] = pd.to_datetime(record['fecha_regi'])
        record['hectareas0'] = float(record['hectareas0'])
        record['perimetro'] = float(record['perimetro'])
        record['sde_state_'] = int(record['sde_state_'])
        #geo
        record['latdec'] = float(record['centroid_y'])
        record['londec'] = float(record['centroid_x'])
        record['coordinates'] = [record['latdec'], record['londec']]


    # Accede a la base de datos si no existe, se creará al insertar el primer documento
    db = client['proyecto']
    collection = db['reservas']

    if isinstance(data, list):  # Asegurarse de que 'data' sea una lista
        collection.insert_many(data)
        print("Datos insertados en MongoDB.")
    else:
        print("Los datos no estaban en el formato correcto (deberían ser una lista).")

    #Carga Base de Datos - Tramos Vías Nacionales




    gdf = gpd.read_file("data/infraestructuravial_.geojson")
    gdf = gdf.to_crs(epsg=4326)

    # Lee las variables
    db_pass = os.getenv('AWS_PASS')
    db_name = os.getenv('DB_NAME')

    # Parámetros fijos
    db_user = os.getenv('DB_USER')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    # Crea el engine SQLAlchemy
    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT version();")
            version = result.fetchone()
            print("Conectado a PostgreSQL versión:", version[0])
    except Exception as e:
        print("Error al conectar a PostgreSQL:", e)


    gdf.to_postgis(
        name='tramos_vias',
        con=engine,
        if_exists='append',  # or 'replace' or 'fail'
        index=False
    )

    #Carga Base de Datos Forestales

    # URL del archivo JSON
    url = "https://www.datos.gov.co/resource/9a89-px8u.json?$limit=200000"

    # Descargar el contenido del archivo
    response = requests.get(url)

    # Verificar si la descarga fue exitosa
    if response.status_code == 200:
        data = response.json()  # Cargar el JSON en memoria
        print("JSON descargado con éxito.")

        # Verificar si 'data' es una lista
        if isinstance(data, list):
            print("Los datos son una lista.")
        else:
            print("Los datos NO son una lista.")
            print("Tipo de datos:", type(data))

        # Opcional: Imprimir la estructura de los primeros elementos si no es una lista
        if not isinstance(data, list):
            print("Contenido de los datos:", data)

    else:
        print("Error al descargar el archivo:", response.status_code)


    for record in data:
        record['fid'] = int(record['fid'])
        record['objectid'] = int(record['objectid'])
        record['id_pnn'] = int(record['id_pnn'])
        record['resoluci_n'] = int(record['resoluci_n'])
        record['hectareas'] = float(record['hectareas'])
        record['wkid'] = int(record['wkid'])
        record['app_id'] = int(record['app_id'])
        record['record_id'] = int(record['record_id'])
        record['fecha_regi'] = pd.to_datetime(record['fecha_regi'])
        record['hectareas0'] = float(record['hectareas0'])
        record['perimetro'] = float(record['perimetro'])
        record['sde_state_'] = int(record['sde_state_'])



    df = pd.DataFrame(data)

    geometry = [Point(xy) for xy in zip(df['centroid_x'], df['centroid_y'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)

    gdf.set_crs(epsg=4326, inplace=True)
    gdf.rename_geometry("geom", inplace=True)

    gdf.to_postgis(
        name='reservas',
        con=engine,
        if_exists='append',  # or 'replace' or 'fail'
        index=False
    )


    BASE_URL = "https://bogota-laburbano.opendatasoft.com/api/explore/v2.1/catalog/datasets/shapes/records"
    LIMIT = 100
    TOTAL = 1122

    all_records = []

    for offset in range(0, TOTAL, LIMIT):
        params = {
            "select": "*",
            "limit": LIMIT,
            "offset": offset
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        all_records.extend(data.get('results', []))

    # 1122 municipios en la base

    print(f"Total records fetched: {len(all_records)}")

    df = pd.DataFrame(all_records)

    # Función para definir geometría
    def get_polygon_geometry(row):
        if row.get("geo_shape"):
            try:
                return shape(row["geo_shape"])
            except Exception as e:
                print(f"Invalid geometry for row: {row} — Error: {e}")
                return None
        else:
            return None

    df["geometry"] = df.apply(get_polygon_geometry, axis=1)

    df = df[df["geometry"].notnull()]

    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    gdf.to_postgis(
        name='municipios',
        con=engine,
        if_exists='append',  # or 'replace' or 'fail'
        index=False
    )

    #UNIFICAR EN BIG QUERY

    vias = gpd.read_postgis("SELECT cod_tramo, territoria, key, tramo, sector, calzada, geom FROM tramos_vias;", con=engine, geom_col='geom')
    rf = gpd.read_postgis("SELECT id_pnn, nombre, categoria, hectareas, fecha_regi, geom FROM reservas;", con=engine, geom_col='geom')

    # Encontrar vías más cercanas a cada parque/reserva

    resultados = []

    # Usar CRS proyectado para calcular distancias

    projected_crs = "EPSG:3116"

    rf_proj = rf.to_crs(projected_crs)
    vias_proj = vias.to_crs(projected_crs)

    for index, reserva in rf_proj.iterrows():
        reserva_geom = reserva['geom']
        distancias = vias_proj.distance(reserva_geom)

        vias_cercanas_indices = distancias.nsmallest(3).index
        vias_cercanas = vias_proj.loc[vias_cercanas_indices]

        detalles = []
        for idx in vias_cercanas_indices:
            distancia_km = round(distancias.at[idx] / 1000, 2)
            detalles.append({
                'via': vias_proj.at[idx, 'sector'],
                'tipo_via': vias_proj.at[idx, 'key'],
                'calzada_via': vias_proj.at[idx, 'calzada'],
                'distancia_km': distancia_km
            })

        resultados.append({
            'id_reserva': reserva['id_pnn'],
            'vias_cercanas_datos': detalles
        })

    rf_vias_cercanas = pd.DataFrame(resultados).drop_duplicates(subset='id_reserva')


    db = client['proyecto']
    collection = db['rnt']
    # Leer base de RNT
    documents = list(collection.find(
        {},
        {
            'codigo_rnt': 1,
            'cod_mun': 1,
            'cod_dpto': 1,
            'razon_social_establecimiento': 1,
            'departamento': 1,
            'municipio': 1,
            'categoria': 1,
            'habitaciones': 1,
            'camas': 1,
            'num_emp1': 1,
            'correo_establecimiento': 1,
            '_id': 0
        }
    ))

    rnt = pd.DataFrame(documents)

    municipios = gpd.read_postgis("SELECT dpto, mpios, nombre_dpt, nombre_mpi, geometry FROM municipios;", con=engine, geom_col='geometry')

    municipios['dpto'] = municipios['dpto'].astype(int)
    municipios['mpios'] = municipios['mpios'].astype(int)
    municipios.rename(columns={'mpios': 'cod_mun', 'dpto': 'cod_dpto'}, inplace=True)

    # Todos los registros con departamento BOGOTA deben tener código 11001

    rnt.loc[rnt['departamento'] == 'BOGOTA', 'cod_mun'] = 11001
    rnt_poly = pd.merge(rnt, municipios, on=['cod_mun', 'cod_dpto'], how='left')
    # Se eliminan los registros sin poligono correspondiente

    rnt_poly = rnt_poly.dropna(subset=['geometry'])

    # Se eliminan establecimientos sin nombre

    rnt_poly = rnt_poly.dropna(subset=['razon_social_establecimiento'])

    # Re definir como gdf

    rnt_poly = gpd.GeoDataFrame(rnt_poly, geometry='geometry', crs=4326)


    # Asignar categoría según tipo de establecimiento turistico

    def asignar_grupo_categoria(categoria):
        if categoria in [
            "VIVIENDAS TURÍSTICAS", "ESTABLECIMIENTOS DE ALOJAMIENTO TURÍSTICO",
            "OTROS TIPOS DE HOSPEDAJE TURÍSTICOS NO PERMANENTES",
            "EMPRESAS DE TIEMPO COMPARTIDO Y MULTIPROPIEDAD",
            "COMPAÑÍAS DE INTERCAMBIO VACACIONAL"
        ]:
            return "alojamiento_turistico"
        elif categoria in [
            "AGENCIAS DE VIAJES", "EMPRESAS DE TRANSPORTE TERRESTRE AUTOMOTOR",
            "ARRENDADORES DE VEHÍCULOS PARA TURISMO NACIONAL E INTERNACIONAL",
            "OFICINAS DE REPRESENTACION TURÍSTICA",
            "OPERADORES DE PLATAFORMAS ELECTRÓNICAS O DIGITALES DE SERVICIOS TURÍSTICOS",
            "EMPRESAS CAPTADORAS DE AHORRO PARA VIAJES"
        ]:
            return "servicios_viaje_transporte"
        elif categoria in [
            "GUIAS DE TURISMO", "PARQUES TEMÁTICOS",
            "CONCESIONARIOS DE SERVICIOS TURÍSTICOS EN PARQUE",
            "USUARIOS INDUSTRIALES OPERADORES O DESARROLLADORES DE SERVICIOS TURISTICOS DE LAS ZONAS FRANCAS"
        ]:
            return "actividades_turisticas_recreativas"
        elif categoria in [
            "ESTABLECIMIENTOS DE GASTRONOMÍA", "BARES",
            "ORGANIZADORES DE BODA DESTINO",
            "OPERADORES PROFESIONALES DE CONGRESOS FERIAS Y CONVENCIONES"
        ]:
            return "servicios_complementarios"
        else:
            return "Otra"

    rnt_poly["grupo_categoria"] = rnt_poly["categoria"].apply(asignar_grupo_categoria)
    rnt_poly.loc[rnt_poly['cod_mun']==11001,'municipio'] = "BOGOTA"


    # join espacial: punto dentro de poligono (rf within rnt_poly)
    rnt_poly_proj = rnt_poly.to_crs(projected_crs)
    joined = gpd.sjoin(rf_proj, rnt_poly_proj, predicate='within', how='left')


    joined = joined.rename(columns={
        'razon_social_establecimiento': 'nombre_establecimiento',
        'categoria_right': 'categoria_establecimiento'
    })

    joined = joined[[
        'id_pnn',
        'nombre_establecimiento',
        'correo_establecimiento',
        'categoria_establecimiento',
        'grupo_categoria'
    ]]

    # Seleccionar aleatoriamente 3 establecimientos por categoría

    def sample_group(group):
        return group.drop(columns=['id_pnn']).sample(n=min(3, len(group))).to_dict(orient='records')

    categoria_dict = {}

    categorias_deseadas = [
        "alojamiento_turistico",
        "servicios_viaje_transporte",
        "actividades_turisticas_recreativas",
        "servicios_complementarios"
    ]

    for cat in categorias_deseadas:
        df_cat = joined[joined["grupo_categoria"] == cat]
        sampled = df_cat.groupby(["id_pnn"], group_keys=False).apply(sample_group).reset_index(name=cat)
        categoria_dict[cat] = sampled

    # Unir los resultados por id_pnn
    from functools import reduce

    final_df = categoria_dict[categorias_deseadas[0]]

    for cat in categorias_deseadas[1:]:
        final_df = pd.merge(final_df, categoria_dict[cat], on=["id_pnn"], how="outer")

    # Asociar municipio y departamento a cada reserva

    municipios_proj = municipios.to_crs(projected_crs)

    rf_mun = gpd.sjoin(rf_proj, municipios_proj, predicate='within', how='left').drop(columns=['index_right', 'cod_dpto', 'cod_mun', 'geom'])

    rf_mun = rf_mun.rename(columns={'nombre_dpt': 'departamento', 'nombre_mpi': 'municipio'})

    # Reservas + vias cercanas + establecimientos de turismo

    rf_vias_cercanas = rf_vias_cercanas.rename(columns={'id_reserva': 'id_pnn'})


    bigquerydf = pd.merge(rf_mun, rf_vias_cercanas, on='id_pnn', how='left')
    bigquerydf = pd.merge(bigquerydf, final_df, on='id_pnn', how='left')

    # Rendodear hectareas a 2 cifras decimales
    bigquerydf['hectareas'] = bigquerydf['hectareas'].round(2)
    bigquerydf = bigquerydf.rename(columns={'actividades_turisticas_recreativas': 'actividades_turisticas'})


    assert rf.shape[0] == bigquerydf.shape[0]
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/ruta/a/tu/proyecto/proyecto-bd-2025-01-f4fed369b39a.json"
    client = bigquery.Client()

    table_id = "proyecto-bd-2025-01.Proyecto.datos_consolidados"

    alojamiento_schema = pa.list_(
        pa.struct([
            pa.field('nombre_establecimiento', pa.string()),
            pa.field('correo_establecimiento', pa.string()),
            pa.field('categoria_establecimiento', pa.string()),
            pa.field('grupo_categoria', pa.string())
        ])
    )

    vias_cercanas_schema = pa.list_(
        pa.struct([
            pa.field('via', pa.string()),
            pa.field('tipo_via', pa.string()),
            pa.field('calzada_via', pa.string()),
            pa.field('distancia_km', pa.float64())
        ])
    )


    def convert_column_to_pyarrow_array(col, schema):
        col_fixed = col.apply(lambda x: x if isinstance(x, list) else [])

        cleaned = col_fixed.apply(lambda x: json.loads(json.dumps(x)))

        return pa.array(cleaned.tolist(), type=schema)

    pa_alojamiento = convert_column_to_pyarrow_array(bigquerydf['alojamiento_turistico'], alojamiento_schema)
    pa_servicios_viaje = convert_column_to_pyarrow_array(bigquerydf['servicios_viaje_transporte'], alojamiento_schema)
    pa_actividades = convert_column_to_pyarrow_array(bigquerydf['actividades_turisticas'], alojamiento_schema)
    pa_servicios_complementarios = convert_column_to_pyarrow_array(bigquerydf['servicios_complementarios'], alojamiento_schema)
    pa_vias_cercanas = convert_column_to_pyarrow_array(bigquerydf['vias_cercanas_datos'], vias_cercanas_schema)

    data = {
        'id_pnn': bigquerydf['id_pnn'],
        'nombre': bigquerydf['nombre'],
        'hectareas': bigquerydf['hectareas'],
        'fecha_regi': bigquerydf['fecha_regi'].dt.date,
        'departamento': bigquerydf['departamento'],
        'municipio': bigquerydf['municipio'],

        'vias_cercanas_datos': pa_vias_cercanas,
        'alojamiento_turistico': pa_alojamiento,
        'servicios_viaje_transporte': pa_servicios_viaje,
        'actividades_turisticas': pa_actividades,
        'servicios_complementarios': pa_servicios_complementarios,

        'categoria': bigquerydf['categoria']
    }

    # Create PyArrow table
    pa_table = pa.Table.from_pydict(data)

    bq_schema = [
        bigquery.SchemaField("id_pnn", "INTEGER"),
        bigquery.SchemaField("nombre", "STRING"),
        bigquery.SchemaField("hectareas", "FLOAT"),
        bigquery.SchemaField("fecha_regi", "DATE"),
        bigquery.SchemaField("departamento", "STRING"),
        bigquery.SchemaField("municipio", "STRING"),
        bigquery.SchemaField("vias_cercanas_datos", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("via", "STRING"),
            bigquery.SchemaField("tipo_via", "STRING"),
            bigquery.SchemaField("calzada_via", "STRING"),
            bigquery.SchemaField("distancia_km", "FLOAT"),
        ]),
        bigquery.SchemaField("alojamiento_turistico", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("nombre_establecimiento", "STRING"),
            bigquery.SchemaField("correo_establecimiento", "STRING"),
            bigquery.SchemaField("categoria_establecimiento", "STRING"),
            bigquery.SchemaField("grupo_categoria", "STRING"),
        ]),
        bigquery.SchemaField("servicios_viaje_transporte", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("nombre_establecimiento", "STRING"),
            bigquery.SchemaField("correo_establecimiento", "STRING"),
            bigquery.SchemaField("categoria_establecimiento", "STRING"),
            bigquery.SchemaField("grupo_categoria", "STRING"),
        ]),
        bigquery.SchemaField("actividades_turisticas", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("nombre_establecimiento", "STRING"),
            bigquery.SchemaField("correo_establecimiento", "STRING"),
            bigquery.SchemaField("categoria_establecimiento", "STRING"),
            bigquery.SchemaField("grupo_categoria", "STRING"),
        ]),
        bigquery.SchemaField("servicios_complementarios", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("nombre_establecimiento", "STRING"),
            bigquery.SchemaField("correo_establecimiento", "STRING"),
            bigquery.SchemaField("categoria_establecimiento", "STRING"),
            bigquery.SchemaField("grupo_categoria", "STRING"),
        ]),
        bigquery.SchemaField("categoria", "STRING")
    ]

    df_arrow = pa_table.to_pandas(types_mapper=pd.ArrowDtype)


    job_config = bigquery.LoadJobConfig(
        schema=bq_schema,
        write_disposition="WRITE_TRUNCATE"
    )

    job = client.load_table_from_dataframe(df_arrow, table_id, job_config=job_config)
    job.result()

    print("✅ Upload successful!")

if __name__ == "__main__":
    main()