import geopandas as gpd
import pandas as pd
import streamlit as st 


st.write("""
         # Annual Consumption by half-postcode location
         """)

st.header('From BEIS Data ')

# Load London postcode 
london_postcodes = pd.read_csv("./data/london_postcode_list.csv")
london_postcodes = list(london_postcodes.Postcodes)
london_postcodes_half = [x.split(None, 1)[0] for x in london_postcodes]

# load boundaries
path = './data/london_districts.shp'
london_shp = gpd.read_file(path)

# Find boundaries by London postcode 
london_shp = london_shp[london_shp.name.isin(london_postcodes_half)]

# Load consumption data
consumption_data = pd.read_csv("./data/consumption_data_london_postcodes_consumption.csv")
consumption_data['london_postcodes_half'] = [x.split(None, 1)[0] for x in consumption_data.POSTCODE]
consumption_data['Consumption (kWh)'] = consumption_data['Consumption (kWh)']/12

consumption_data_half = consumption_data.groupby('london_postcodes_half').mean().reset_index()


london_shp['postcode'] = london_shp['name']
consumption_data_half['postcode'] = consumption_data_half.london_postcodes_half

consumption_data_map = london_shp.merge(consumption_data_half, left_on='postcode', right_on='postcode', how="inner")

x = st.slider("Minimum threshold", 0, 15000, 10000)
y = st.slider("Maximum threshold", 0, 5000, 1000)

consumption_data_map = consumption_data_map[(consumption_data_map['Consumption (kWh)']<x)] 
consumption_data_map = consumption_data_map[(consumption_data_map['Consumption (kWh)']>y)] 

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
import numpy as np 

plt.rcParams['axes.facecolor'] = (0.9, 0.9, 0.9)

fig, ax = plt.subplots(1, 1, figsize=(15,15))

# This dictionary defines the colormap
cdict = {'red':  ((0.0, 0.0, 0.0),   # no red at 0
                  (0.5, 1.0, 1.0),   # all channels set to 1.0 at 0.5 to create white
                  (1.0, 0.8, 0.8)),  # set to 0.8 so its not too bright at 1

        'green': ((0.0, 0.8, 0.8),   # set to 0.8 so its not too bright at 0
                  (0.5, 1.0, 1.0),   # all channels set to 1.0 at 0.5 to create white
                  (1.0, 0.0, 0.0)),  # no green at 1

        'blue':  ((0.0, 0.0, 0.0),   # no blue at 0
                  (0.5, 1.0, 1.0),   # all channels set to 1.0 at 0.5 to create white
                  (1.0, 0.0, 0.0))   # no blue at 1
       }

ax.axis('off')

# Create the colormap using the dictionary
GnRd = colors.LinearSegmentedColormap('GnRd', cdict)

divider = make_axes_locatable(ax)

consumption_data_map.plot(column='Consumption (kWh)', ax=ax, legend=True, 
                          legend_kwds={'label': "Energy Use (kWh)", 'orientation': "horizontal"}, 
                         cmap=GnRd)
st.pyplot()