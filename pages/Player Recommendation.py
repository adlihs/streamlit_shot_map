import pandas as pd
import duckdb
# import os
import numpy as np
from PIL import Image
# import matplotlib.image as mpimg
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

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
select_player_data = data.copy()  # data to player selection sliders
recommend_data = data.copy()
unique_players = recommend_data['Player'].unique()
unique_tournament = recommend_data['Comp'].unique()
unique_team = recommend_data['Squad'].unique()
unique_position = recommend_data['PlayerPos'].unique()
unique_age = recommend_data['Age'].unique()
unique_age = np.sort(unique_age, axis=0)
unique_nationality = recommend_data['Nation'].unique()
unique_minutes = recommend_data['Min_Playing_Time'].unique()
unique_minutes = np.sort(unique_minutes, axis=0)
max_minutes = recommend_data['Min_Playing_Time'].max()

with st.sidebar:
    st.title('Select Player :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox(
        'Select a League',
        ('Premier League', 'La Liga', 'Ligue 1', 'Bundesliga', 'Serie A',
         'Eredivisie', 'Primeira Liga', 'Belgian Pro League',
         'Brasileiro Série A', 'Primera División'))
    select_player_data = select_player_data[select_player_data['Comp'] == leagues]
    data_teams = select_player_data['Squad'].unique()

    teams = st.selectbox(
        'Select a team',
        data_teams
    )
    select_player_data = select_player_data[(select_player_data['Comp'] == leagues) & (select_player_data['Squad'] == teams)]
    data_teams_players = select_player_data['Player'].unique()
    players = st.selectbox(
        'Select a Player',
        data_teams_players)

### Selectboxes to filter the base of players to analyze and recommend


select_comp = st.multiselect(
    'Select a League',
    unique_tournament, key='s_comp'
)


start_age, end_age = st.select_slider(
    'Select a range of age',
    options=unique_age,
    value=(15, 40))

start_min, end_min = st.select_slider(
    'Select a range of Minutes',
    options=unique_minutes,
    value=(1, max_minutes))

### ------------------------ ###
select_player = data[data['Player'] == players]
attributes = load_data()
selected_player_position = select_player['PlayerPos'].unique()[0]
print(selected_player_position)


attributes = attributes[(attributes['PlayerPos'] == selected_player_position)
                        & (attributes['Age'] <= end_age)
                        & (attributes['Comp'].isin(select_comp))
                        & (attributes['Min_Playing_Time'] >= start_min)
                        & (attributes['Min_Playing_Time'] <= end_min)]

attributes = attributes.append(select_player)

att_players_names = attributes.copy()
attributes = attributes.iloc[:, 7:]

attributes = attributes.fillna(0)

bck_attributes = attributes.copy()
bck_attributes['Player'] = att_players_names['Player']

bck_attributes = bck_attributes.reset_index(drop=True)
attributes = attributes.reset_index(drop=True)

scaled = StandardScaler()
x = scaled.fit_transform(attributes)

recommendations = NearestNeighbors(n_neighbors=4, algorithm='auto', p=2).fit(x)
player_index = recommendations.kneighbors(x)[1]


def get_player_index(x):
    # bck_atributos = bck_atributos.reset_index(drop=True)
    return bck_attributes[bck_attributes['Player'] == x].index.tolist()[0]


def recommend_players(player,data_to_filter):
    #print('Here are 5 players similar to', player, ':' '\n')
    index = get_player_index(player)
    player_list = []
    for i in player_index[index][1:]:
        p_tmp = bck_attributes.iloc[i]['Player']
        if player != p_tmp:

            player_list.append(bck_attributes.iloc[i]['Player'])

    filtered_df = data_to_filter[data_to_filter['Player'].isin(player_list)]

    return filtered_df


rec_result = recommend_players(players, data_to_filter=load_data())
### ------------------------ ###

# player_shot_map(player=players)
# st.dataframe(unique_age)
st.dataframe(rec_result['Player'].unique())
#st.text(rec_result['Player'].unique())
