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
import parquet

# from functions_file import load_data, load_data_from_url

pd.set_option('display.max_columns', None)


# Función para eliminar tildes
def eliminar_tildes(texto):
    texto_nfd = unicodedata.normalize('NFD', texto)
    texto_limpio = ''.join(c for c in texto_nfd if not unicodedata.combining(c))
    return texto_limpio


@st.cache_data
def load_data():
    '''
    premierleague = pd.read_parquet(
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ENG_match_events.parquet')

    bundesliga = pd.read_parquet(
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/GER_match_events.parquet')

    serieA = pd.read_parquet(
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ITA_match_events.parquet')

    ligue1 = pd.read_parquet(
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/FRA_match_events.parquet')
    #print(bundesliga.dtypes)
    premierleague['league'] = 'Premier League'
    bundesliga['league'] = 'Bundesliga'
    serieA['league'] = 'Serie A'
    ligue1['league'] = 'Ligue 1'
    pass_data = pd.concat([premierleague, bundesliga,serieA,ligue1], ignore_index=True)
    '''
    pass_data = pd.concat(map(pd.read_parquet, [
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ENG_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/GER_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ITA_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/FRA_match_events.parquet']))

    pass_data[['date', 'game']] = pass_data['game'].str.split(" ", n=1, expand=True)
    pass_data['season'] = '23-24'


    return pass_data



def game_flow_pass_map(soccer_data, game, game_date):
    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')

    # Getting successful pass data
    pass_df = soccer_data[(soccer_data['type'] == 'Pass')
                          & (soccer_data['outcome_type'] == 'Successful')
                          & (soccer_data['game'] == game)
                          & (soccer_data['date'] == game_date)]

    # Get team names
    team1 = pass_df['team'].unique()[0]
    team2 = pass_df['team'].unique()[1]
    print(team1)
    print(team2)

    # Get other game details
    game = pass_df['game'].unique()[0]
    league = pass_df['league'].unique()[0]
    season = pass_df['season'].unique()[0]

    # Get successful pass data for each team
    team1_pass_df = pass_df[pass_df['team'] == team1]
    team2_pass_df = pass_df[pass_df['team'] == team2]
    bins = (6, 4)

    # Setup pass flow for Team 1
    fig, axs = plt.subplots(nrows=2, figsize=(15, 18))
    fig.set_facecolor('#eee9e5')
    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='#01161E',
                  pitch_color='#eee9e5')  # you can also adjust the transparency (alpha)
    # Team 1 heatmap
    bs_heatmap = pitch.bin_statistic(team1_pass_df.x, team1_pass_df.y, statistic='count', bins=bins)
    pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                           ['#eee9e5', '#2f3e46'], N=100)
    hm = pitch.heatmap(bs_heatmap, ax=axs[0], cmap=pearl_earring_cmap)

    # Team 1 pass flow
    fm = pitch.flow(team1_pass_df.x, team1_pass_df.y, team1_pass_df.end_x, team1_pass_df.end_y,
                    color='black', arrow_type='same',
                    arrow_length=5, bins=bins, ax=axs[0])

    # Team 1 title details
    txt_title_main = axs[0].text(x=0.1, y=109, s=team1 + ' Pass Flow Map',
                                 size=40,
                                 # here i am using a downloaded font from google fonts instead of passing a fontdict
                                 fontproperties=fm_rubik.prop, color=pitch.line_color)

    txt_title_details = axs[0].text(x=0.1, y=104.5,
                                    s="vs " + str(team2) + " | " + str(game_date) + " | " + str(league) + " | " + str(
                                        season),
                                    size=15,
                                    fontproperties=fm_rubik.prop, color=pitch.line_color)

    pitch.draw(axs[0])

    # Setup pass flow for Team 2
    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='#01161E',
                  pitch_color='#eee9e5')  # you can also adjust the transparency (alpha)
    # Team 2 heatmap
    bs_heatmap = pitch.bin_statistic(team2_pass_df.x, team2_pass_df.y, statistic='count', bins=bins)
    pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                           ['#eee9e5', '#2f3e46'], N=100)
    hm = pitch.heatmap(bs_heatmap, ax=axs[1], cmap=pearl_earring_cmap)

    # Team 2 pass flow
    fm = pitch.flow(team2_pass_df.x, team2_pass_df.y, team2_pass_df.end_x, team2_pass_df.end_y,
                    color='black', arrow_type='same',
                    arrow_length=5, bins=bins, ax=axs[1])

    # Team 2 title details
    txt_title_main = axs[1].text(x=0.1, y=109, s=team2 + ' Pass Flow Map',
                                 size=40,
                                 # here i am using a downloaded font from google fonts instead of passing a fontdict
                                 fontproperties=fm_rubik.prop, color=pitch.line_color)

    txt_title_details = axs[1].text(x=0.1, y=104.5,
                                    s="vs " + str(team1) + " | " + str(game_date) + " | " + str(league) + " | " + str(
                                        season),
                                    size=15,
                                    fontproperties=fm_rubik.prop, color=pitch.line_color)

    pitch.draw(axs[1])
    st.pyplot(plt)


data = load_data()
# st.dataframe(data)

with st.sidebar:
    st.title('Pass Flow Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga', 'Serie A','Ligue 1'))

    data = data[data['league'] == leagues]

    data_dates = data['date'].unique()

    Gdates = st.selectbox(
        'Select a date',
        data_dates
    )
    data = data[(data['league'] == leagues) & (data['date'] == Gdates)]
    data_games = data['game'].unique()

    games = st.selectbox(
        'Select a Game',
        data_games)

game_flow_pass_map(soccer_data=data, game_date=Gdates, game=games)
