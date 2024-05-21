#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 12:41:08 2024

@author: manuelrocamoravalenti
"""

import streamlit as st
import pandas as pd
import numpy as np

# Load your data
data = pd.read_csv('fgv-bocas.csv', delimiter=';')

# Split 'geo_point_2d' into two separate columns
lat_lng = data['geo_point_2d'].str.split(',', expand=True)
data['latitude'] = lat_lng[0].astype(float)
data['longitude'] = lat_lng[1].astype(float)

# Now you can use st.map()
st.map(data[['latitude', 'longitude']])

