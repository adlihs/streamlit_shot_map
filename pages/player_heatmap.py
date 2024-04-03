import pandas as pd
# import os
# import numpy as np
import PIL.Image
# import matplotlib.image as mpimg

from mplsoccer import (Pitch, FontManager)
import matplotlib.pyplot as plt
# import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st

from utils.functions_file import load_data

pd.set_option('display.max_columns', None)


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
                  line_color='#6d6a69',
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
    fn = 'player_heatmap.png'
    plt.savefig(fn)
    with open(fn, "rb") as img:
        btn = st.download_button(
            label="Download image",
            data=img,
            file_name=fn,
            mime="image/png"
        )





# st.dataframe(data)

with st.sidebar:
    st.title('Player Heatmap Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga', 'Serie A',
                            'Ligue 1', 'La Liga','Premiership','Eredivisie','Primeira Liga','MLS','Jupiter ProLeague'))
    data = load_data(app=1,league=leagues)
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
    viz = st.button("Apply", type="primary")

if viz:
    player_heatmap(soccer_data=data, player_name=players, custom_color=color)
