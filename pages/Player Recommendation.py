import pandas as pd
import duckdb
# import os
import numpy as np
from PIL import Image
# import matplotlib.image as mpimg

from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, add_image)
import matplotlib.pyplot as plt
# import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
# from matplotlib.colors import to_rgba, LinearSegmentedColormap
import unicodedata
import streamlit as st

pd.set_option('display.max_columns', None)


# Función para eliminar tildes
def eliminar_tildes(texto):
    texto_nfd = unicodedata.normalize('NFD', texto)
    texto_limpio = ''.join(c for c in texto_nfd if not unicodedata.combining(c))
    return texto_limpio


@st.cache_data
def load_data():
    player_data = pd.read_csv('data/player_unique_recommendations.csv')

    # Aplicar la función a la columna 'texto'
    player_data['Player'] = player_data['Player'].apply(eliminar_tildes)

    return player_data


data = load_data()
recommend_data = data.copy()
unique_players = recommend_data['Player'].unique()
unique_tournament = recommend_data['Comp'].unique()
unique_team = recommend_data['Squad'].unique()
unique_position = recommend_data['PlayerPos'].unique()
unique_age = recommend_data['Age'].unique()
unique_age = np.sort(unique_age, axis=0)
unique_nationality = recommend_data['Nation'].unique()

with st.sidebar:
    st.title('Select Player :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox(
        'Select a League',
        ('Premier League', 'La Liga', 'Ligue 1', 'Bundesliga', 'Serie A',
         'Eredivisie', 'Primeira Liga', 'Belgian Pro League',
         'Brasileiro Série A', 'Primera División'))
    data = data[data['Comp'] == leagues]
    data_teams = data['Squad'].unique()

    teams = st.selectbox(
        'Select a team',
        data_teams
    )
    data = data[(data['Comp'] == leagues) & (data['Squad'] == teams)]
    data_teams_players = data['Player'].unique()
    players = st.selectbox(
        'Select a Player',
        data_teams_players)

### Selectboxes to filter the base of players to analyze and recommend

select_comp = st.multiselect(
    'Select a League',
    unique_tournament, key='s_comp'
)

select_positions = st.multiselect(
    'Select a Position(s)',
    unique_position, key='s_position'
)

start_age, end_age = st.select_slider(
    'Select a range of age',
    options=unique_age,
    value=(15, 40))

# player_shot_map(player=players)
st.dataframe(unique_age)
