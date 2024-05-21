#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 12:21:03 2024

@author: manuelrocamoravalenti
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# ::::::::::::::::::::::::::::: FUNCIONES ::::::::::::::::::::::::::::::::

# Función para obtener próximas llegadas o salidas
def obtener_proximos_movimientos(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer la información específica de llegadas o salidas
        movimientos = []
        for div in soup.find_all('div', style=lambda value: value and 'padding-left: 5px' in value):
            # Extraer el número de la línea desde la URL de la imagen
            numero_linea = div.find('img')['src'].split('_')[-1].split('.')[0]
            destino = div.find('b').text.strip()  # Extrae el destino
            tiempo = div.find_all('span')[-1].text.strip()  # Extrae el tiempo
            movimientos.append({
                "Número de Línea": numero_linea,
                "Destino": destino,
                "Tiempo": tiempo
            })
        
        return movimientos
    except requests.RequestException as e:
        st.error(f"Error al obtener los datos de {url}: {e}")
        return []

# Función para calcular el tiempo restante
def calcular_tiempo_restante(hora_llegada):
    formato = '%M:%S'
    ahora = datetime.now().strftime(formato)
    hora_actual = datetime.strptime(ahora, formato)
    hora_llegada_dt = datetime.strptime(hora_llegada, formato)
    tiempo_restante = hora_llegada_dt - hora_actual
    return str(tiempo_restante)

# :::::::::::::::::::::::::::: INTERFAZ DE USUARIO :::::::::::::::::::::::::::::


# Cargar los datos
data = pd.read_csv('fgv-bocas.csv', delimiter=';')

# Menú de navegación en la barra lateral
pagina = st.sidebar.selectbox('Selecciona una página', ['Inicio','Próximas Llegadas y Salidas', 'Mapa Interactivo'])


if pagina == 'Inicio':
    
    st.title(" Bienvenidos a Nuestra Aplicación de Gestión de Viajes en Metro")
    
    st.image('foto_metro_1.jpg')
    # Sección para próximas llegadas y salidas
    st.markdown("""
                
                
    

Nuestra aplicación surge de la necesidad de proporcionar una herramienta que se actualice en tiempo real y ofrezca información precisa y confiable sobre la llegada de los metros. En un mundo donde el tiempo es invaluable, entendemos la importancia de minimizar la espera y optimizar los viajes de los pasajeros. 

## Actualizaciones en Tiempo Real

La característica principal de nuestra aplicación es su capacidad para actualizarse en tiempo real. Esto significa que los usuarios pueden obtener información instantánea sobre la llegada de los metros, con tiempos medidos y precisos que les permiten planificar sus desplazamientos de manera eficiente. Nunca más tendrás que adivinar cuándo llegará el próximo metro; nuestra app te lo dirá al instante.

## Organización Mejorada para los Viajes de los Pasajeros

Además de proporcionar horarios exactos, nuestra aplicación está diseñada para mejorar la organización de los viajes de los pasajeros. Con funcionalidades avanzadas, los usuarios pueden planificar sus rutas, recibir notificaciones sobre cambios y retrasos, y acceder a recomendaciones para los trayectos más rápidos y convenientes. Nuestro objetivo es hacer que cada viaje sea lo más fluido y libre de estrés posible.

## Una Solución a tus Necesidades de Transporte

En resumen, nuestra aplicación nace de la necesidad de una solución que ofrezca actualizaciones en tiempo real y una organización superior para los viajes en metro. Estamos comprometidos con la innovación y la mejora continua para que tu experiencia de viaje sea óptima, eficiente y agradable. Únete a nosotros y descubre una nueva manera de viajar en metro.
    
    
    
    
    """)
    

elif pagina == 'Próximas Llegadas y Salidas':
    data = pd.read_csv('fgv-bocas.csv', delimiter=';')
    # Sección para próximas llegadas y salidas
    st.markdown("""
    # Próximas Llegadas y Salidas
    Nueva forma de consultar de manera rápida las próximas llegadas y salidas en tu parada.
    Selecciona una estación del metro y obtén la información actualizada de los próximos trenes que llegarán o partirán desde allí.
    """)
    st.image('foto_metro.jpeg')

    # Filtrar datos para la selección de estaciones y ordenar alfabéticamente
    estaciones = sorted(data['Denominació / Denominación'].unique())

    # Entrada de texto para la estación
    estacion_input = st.text_input('Introduce el nombre de la estación:')
    estaciones_filtradas = [estacion for estacion in estaciones if estacion_input.lower() in estacion.lower()]

    estacion_seleccionada = st.selectbox('Selecciona una estación:', estaciones_filtradas)

    if estacion_seleccionada:
        # Verificar si la estación ingresada existe en el DataFrame
        if estacion_seleccionada in data['Denominació / Denominación'].values:
            url_llegadas = data[data['Denominació / Denominación'] == estacion_seleccionada]['Pròximes Arribades / Próximas llegadas'].values[0]

            llegadas = obtener_proximos_movimientos(url_llegadas)

            # Calcular el tiempo restante para llegadas
            for llegada in llegadas:
                llegada["Tiempo Restante"] = calcular_tiempo_restante(llegada["Tiempo"])

            st.markdown(f"#### Próximas llegadas para la estación: {estacion_seleccionada}")
            df_llegadas = pd.DataFrame(llegadas).sort_values(by="Destino")
            st.table(df_llegadas)

            # Añadir una pausa de 60 segundos para la actualización
            time.sleep(1)
            st.experimental_rerun()

        else:
            st.write("La estación introducida no se encuentra en el conjunto de datos.")

elif pagina == 'Mapa Interactivo':
    # Descripción de la aplicación
    st.markdown("""
    # Mapa Interactivo de las Líneas de Metro
    Bienvenido a la visualización interactiva del metro de Valencia. 
    Este mapa muestra las ubicaciones de las estaciones de metro seleccionadas. 
    Puedes elegir las líneas de metro que te interesen y ver su distribución geográfica.
    """)

    # Agregar una foto
    st.image('Plano_general.jpg')

    st.markdown("""
    **Selecciona** las líneas que necesites coger, aparecerán en el mapa las diferentes estaciones disponibles.
    """)

    # Asegurar que los tipos de datos sean correctos
    data[['latitude', 'longitude']] = data['geo_point_2d'].str.split(',', expand=True).astype(float)

    # Obtener líneas únicas del conjunto de datos
    lines = data['Línies / Líneas'].unique()  # Ajustar el nombre de la columna según tu conjunto de datos

    # Checkbox para seleccionar todas las líneas
    if st.checkbox('Select All Lines'):
        selected_lines = lines
    else:
        selected_lines = st.multiselect('Select Metro Lines:', options=lines)

    # Filtrar datos en función de las líneas seleccionadas
    filtered_data_lines = data[data['Línies / Líneas'].isin(selected_lines)]

    # Verificar si hay datos para mostrar
    if not filtered_data_lines.empty:
        # Agregar datos de ícono a los datos filtrados
        filtered_data_lines['icon_data'] = filtered_data_lines.apply(lambda row: {
            'url': 'https://cdn-icons-png.flaticon.com/128/684/684908.png',
            'width': 128,
            'height': 128,
            'anchorY': 128,
        }, axis=1)

        # Definir el estado inicial del mapa
        view_state = pdk.ViewState(
            latitude=filtered_data_lines['latitude'].mean(),
            longitude=filtered_data_lines['longitude'].mean(),
            zoom=11,
            pitch=50
        )

        # Definir la capa de íconos
        icon_layer = pdk.Layer(
            type='IconLayer',
            data=filtered_data_lines,
            get_icon='icon_data',
            get_size=2.5,
            size_scale=15,
            get_position='[longitude, latitude]',
            pickable=True,
        )

        # Crear el mapa con vista satelital
        map = pdk.Deck(
            layers=[icon_layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/satellite-v9'  # Usando la vista satelital de Mapbox
        )

        st.pydeck_chart(map)
    else:
        st.write("No data available for the selected lines.")




