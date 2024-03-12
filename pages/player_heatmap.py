import pandas as pd
import duckdb
# import os
# import numpy as np
# from PIL import Image
# import matplotlib.image as mpimg

from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, add_image)
import matplotlib.pyplot as plt
# import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import to_rgba, LinearSegmentedColormap
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
    '''
    premierleague = pd.read_csv('https://github.com/adlihs/streamlit_shot_map/releases/download/soccer/ENG_match_events.csv')
    bundesliga = pd.read_csv('https://github.com/adlihs/streamlit_shot_map/releases/download/soccer/GER_match_events.csv')
    premierleague['league'] = 'Premier League'
    premierleague['season'] = '23-24'
    bundesliga['league'] = 'Bundesliga'
    bundesliga['season'] = '23-24'

    pass_data = pd.concat([premierleague, bundesliga], ignore_index=True)
    '''
    pass_data = pd.concat(map(pd.read_parquet, [
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ENG_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/GER_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ITA_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/FRA_match_events.parquet']))
    pass_data[['date', 'game']] = pass_data['game'].str.split(" ", n=1, expand=True)
    pass_data['season'] = '23-24'

    return pass_data


def player_heatmap(soccer_data, player_name, custom_color):
    player_data = soccer_data[(soccer_data['player'] == player_name) &
                              (soccer_data['x'] < 99) &
                              (soccer_data['y'] < 99) &
                              (soccer_data['x'] > 0) &
                              (soccer_data['y'] > 0)]

    # Viz Font
    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')

    # Details vars
    team_n = player_data['team'].unique()[0]
    league_n = player_data['league'].unique()[0]
    season_n = player_data['season'].unique()[0]

    # Pitch config
    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='#01161E',
                  pitch_color='#eee9e5')  # control the goal transparency
    fig, ax = pitch.draw(figsize=(12, 10))
    fig.set_facecolor("#eee9e5")

    # Heatmap color config
    pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                           ['#eee9e5', custom_color], N=100)

    # Heatmap config
    heatmap = pitch.kdeplot(player_data.x, player_data.y, ax=ax, cmap=pearl_earring_cmap, fill=True, levels=100)

    # Player Title
    txt_title_player = ax.text(x=0, y=109, s=player_name + ' heatmap',
                               size=40,
                               # here i am using a downloaded font from google fonts instead of passing a fontdict
                               fontproperties=fm_rubik.prop, color=custom_color)

    txt_subtitle_details = ax.text(x=0.1, y=104.5,
                                   s=str(team_n) + " | " + str(league_n) + " | " + str(season_n),
                                   size=15,
                                   fontproperties=fm_rubik.prop,
                                   color=custom_color)
    st.pyplot(plt)


data = load_data()
data = data[data['player'].notna()]
mapeo = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u','ü':'u', 'ø':'o',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U','Ü':'U', 'Ø':'O'
}
# Reemplazar las letras con tilde por las mismas letras sin tilde
data['player'] = data['player'].apply(lambda x: ''.join([mapeo.get(char, char) for char in x]))



# st.dataframe(data)

with st.sidebar:
    st.title('Player Heatmap Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga'))

    data = data[data['league'] == leagues]

    data_teams = data['team'].unique()

    team_name = st.selectbox(
        'Select a Team',
        data_teams
    )
    data = data[(data['league'] == leagues) & (data['team'] == team_name)]
    data_players = data['player'].unique()


    players = st.selectbox(
        'Select a Game',
        data_players)


    color = st.color_picker('Pick A Color', '#0D2C54')

player_heatmap(soccer_data=data, player_name=players, custom_color=color)
