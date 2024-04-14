import pandas as pd
# import os
import numpy as np
import PIL.Image
# import matplotlib.image as mpimg

from mplsoccer import (Pitch, FontManager)
import matplotlib.pyplot as plt
# import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors
import streamlit as st
from utils.functions_file import load_data
from highlight_text import HighlightText, ax_text, fig_text

# from functions_file import load_data, load_data_from_url


def area_control_viz(soccer_data,game,game_date):
    event_data = soccer_data[soccer_data['game'] == game]
    event_data = event_data[(event_data['type'] != 'FormationSet') & (event_data['type'] != 'Start')]

    # Only passes
    event_data = event_data[(event_data['type'] == 'Pass') &
                            (event_data['outcome_type'] == 'Successful') &
                            (event_data['x'] < 99) &
                            (event_data['y'] < 99) &
                            (event_data['x'] > 0) &
                            (event_data['y'] > 0)]


    team1 = event_data['team'].unique()[0]
    team2 = event_data['team'].unique()[1]
    game = event_data['game'].unique()[0]
    league = event_data['league'].unique()[0]
    season = event_data['season'].unique()[0]

    home_team_passes = event_data.query("team == @team1 ")
    away_team_passes = event_data.query("team == @team2 ")
    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')

    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='black',  # 6d6a69
                  pitch_color='#eee9e5')  # control the goal transparency
    fig, ax = pitch.draw(figsize=(14, 12))
    fig.set_facecolor("#eee9e5")

    bins = (6, 5)
    x = pd.to_numeric(event_data['x'])
    y = pd.to_numeric(event_data['y'])

    # -- Home
    home_x = pd.to_numeric(home_team_passes['x'])
    home_y = pd.to_numeric(home_team_passes['y'])
    home_stats = pitch.bin_statistic(home_x, home_y, bins=bins)

    # -- away
    away_x_inv_temp = []
    away_y_inv_temp = []
    away_x_inv = []
    away_y_inv = []
    for i, row in away_team_passes.iterrows():
        away_x = pd.to_numeric(row.x)
        away_y = pd.to_numeric(row.y)
        away_x_inv_temp, away_y_inv_temp = pitch.flip_side(away_x, away_y, True)
        away_x_inv.append(away_x_inv_temp)
        away_y_inv.append(away_y_inv_temp)

    away_stats = pitch.bin_statistic(away_x_inv, away_y_inv, bins=bins)

    for j in range(len(home_stats['statistic'])):

        for k in range(len(home_stats['statistic'][j])):

            total_touches = home_stats['statistic'][j][k] + away_stats['statistic'][j][k]

            if home_stats['statistic'][j][k] > (total_touches * 0.55):
                home_stats['statistic'][j][k] = 100
            elif away_stats['statistic'][j][k] > (total_touches * 0.55):
                home_stats['statistic'][j][k] = 50
            else:
                home_stats['statistic'][j][k] = 0

    # plot the heatmap

    cmap = colors.ListedColormap(
        ['#e4dfda', '#c1666b', '#48a9a6'])  # (contest,away,home) (0,50,100) (gray,naranja, verde) ffba08
    # Home: Azul, Away: Naranja, Contest: Gray
    hm = pitch.heatmap(home_stats, ax=ax, cmap=cmap, edgecolors='white')  # ,alpha=0.5)

    txt_title_team = ax.text(x=0, y=109, s='Area Control',
                             size=40,
                             # here i am using a downloaded font from google fonts instead of passing a fontdict
                             fontproperties=fm_rubik.prop, color="#6d6a69")

    ax.text(x=0.1, y=104.5,
            s=str(game_date) + " | " + str(game) + " | " + str(league) + " " + str(season),
            size=15,
            fontproperties=fm_rubik.prop,
            color="#6d6a69")

    # Detalle del texto de metricas de pases
    annotation_string = (f"<{team1}>'s controlled area \n"
                         f"<{team2}>'s controlled area \n")

    # Configuracion para el highlight de los textos de metricas
    highlight_textprops = [{"fontsize": 12, "color": '#48a9a6', "fontweight": 'bold'},
                           {"fontsize": 12, "color": '#c1666b', "fontweight": 'bold'}]

    # Ubicacion del texto con detalle de metricas
    ax_text(80.2, 108.5, annotation_string, ha='left', va='center', fontsize=12,
            highlight_textprops=highlight_textprops,
            fontproperties=fm_rubik.prop,
            color="#6d6a69",
            # fontproperties=fm_scada.prop,  # using the fontmanager for the google font
            ax=ax)

    pitch.arrows(0, -2, 10, -2, ax=ax, color="#48a9a6")
    pitch.arrows(100, -2, 90, -2, ax=ax, color="#c1666b")
    pitch.annotate(text=team1, xytext=(3, -3.8), xy=(0, -2), ha='center', va='center', color="#48a9a6",
                   ax=ax)
    pitch.annotate(text=team2, xytext=(97, -3.8), xy=(100, -2), ha='center', va='center', color="#c1666b",
                   ax=ax)

    st.pyplot(plt)
    st.markdown("A team controls an area when it has **more than 55% of total passes** in the area")
    fn = f'are control {games}.png'
    plt.savefig(fn)
    with open(fn, "rb") as img:
        btn = st.download_button(
            label="Download image",
            data=img,
            file_name=fn,
            mime="image/png"
        )


with st.sidebar:
    st.title('Area Control Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga', 'Serie A',
                            'Ligue 1', 'La Liga','Premiership','Eredivisie','Primeira Liga','MLS',
                            'Jupiter ProLeague','UCL','EUL','Championship (ENG)','Premier League (RUS)'))
    data = load_data(app=1,league=leagues)
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
    viz = st.button("Apply", type="primary")
    st.page_link("main.py", label="Main Menu", icon="↩️")


if viz:
    area_control_viz(soccer_data=data, game_date=Gdates, game=games)
