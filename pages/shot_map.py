import pandas as pd
import duckdb
# import os
# import numpy as np
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
from functions_file import load_data

pd.set_option('display.max_columns', None)


def player_shot_map(player=None):
    shot_data = load_data(app=3)
    data = shot_data[shot_data['player'] == player]  # get_player_shoot_data(player=player)
    data = data.drop_duplicates()
    # team_id = data.iloc[0]['team_id']
    team_name = data.iloc[0]['home_away']  # get_team_name(team_id=team_id)

    data_gol = data[data.result == 'Goal'].copy()
    data_non_goal = data[data.result != 'Goal'].copy()

    # Calculate total goals
    total_goals = duckdb.sql("SELECT COUNT(*) as 'goals' FROM data where result='Goal'").df()
    total_goals = total_goals['goals'].iloc[0]

    # Calculate total xG
    total_xG = duckdb.sql("SELECT sum(xG) as 'xG' FROM data ").df()
    total_xG = total_xG['xG'].iloc[0]
    total_xG = round(float(total_xG), 1)

    # Calculate total xGOT
    # total_xGOT = duckdb.sql("SELECT sum(expected_goals_on_target) as 'xGOT' FROM data ").df()
    # total_xGOT = total_xGOT['xGOT'].iloc[0]
    # total_xGOT = round(float(total_xGOT), 1)

    # Calculate total shots
    total_shots = duckdb.sql("SELECT COUNT(*) as 'shots' FROM data ").df()
    total_shots = total_shots['shots'].iloc[0]
    total_shots = round(int(total_shots), 0)

    # total_xG
    # total_shots

    season = data['season'].iloc[0]
    league = data['league_name'].iloc[0]

    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')

    pitch = VerticalPitch(pitch_type='custom',
                          pitch_length=105,
                          pitch_width=68,
                          pitch_color='#eee9e5',
                          line_color='#6d6a69',
                          half=True)  # control the goal transparency
    fig, ax = pitch.draw(figsize=(12, 10))
    fig.set_facecolor("#eee9e5")
    goal = pitch.scatter((data_gol.X / 100) * 105 * 100, (data_gol.Y / 100) * 68 * 100,
                         # size varies between 100 and 1000 (points squared)
                         s=(data_gol.xG * 900) + 100,
                         c='#001D4A',  # color for scatter in hex format
                         edgecolors='#001D4A',  # give the markers a charcoal border
                         # for other markers types see: https://matplotlib.org/api/markers_api.html
                         marker='o',
                         alpha=0.5,
                         ax=ax)

    non_goal = pitch.scatter((data_non_goal.X / 100) * 105 * 100, (data_non_goal.Y / 100) * 68 * 100,
                             # size varies between 100 and 1000 (points squared)
                             s=(data_non_goal.xG * 900) + 100,
                             c='#6d6a69',  # color for scatter in hex format
                             edgecolors='#6d6a69',  # give the markers a charcoal border
                             # for other markers types see: https://matplotlib.org/api/markers_api.html
                             marker='o',
                             alpha=0.5,
                             ax=ax)

    txt_title_team = ax.text(x=68, y=109, s=player + ' shots',
                             size=40,
                             # here i am using a downloaded font from google fonts instead of passing a fontdict
                             fontproperties=fm_rubik.prop, color=pitch.line_color)

    txt_title_tournament = ax.text(x=68, y=107, s=team_name + " | " + str(league) + " " + str(season),
                                   size=15,
                                   fontproperties=fm_rubik.prop, color=pitch.line_color)
    # icons = team_icons_dictionary()

    # imagen = icons.get(str(team_name))
    # imagen = Image.open(imagen)
    # ax_image = add_image(imagen, fig, left=0.84, bottom=0.9, width=0.08,
    # alpha=0.9, interpolation='hanning')

    # Text with metrics values

    ### xG ###
    ax.text(54.7, 72.5, total_xG, fontsize=12, ha='center', va='center', color='white', fontproperties=fm_rubik.prop)
    xG_rect = FancyBboxPatch((53.5, 71.5), 2.4, 2.2, boxstyle="round,pad=0.3", facecolor='#001D4A',
                             edgecolor='#001D4A', lw=1.5)
    txt_xG = ax.text(x=63, y=72, s='xG:',
                     size=18,
                     fontproperties=fm_rubik.prop, color=pitch.line_color)
    ax.add_patch(xG_rect)

    ### Goals ###
    ax.text(54.7, 67.5, total_goals, fontsize=12, ha='center', va='center', color='white', fontproperties=fm_rubik.prop)
    goals_rect = FancyBboxPatch((53.5, 66.5), 2.4, 2.2, boxstyle="round,pad=0.3", facecolor='#001D4A',
                                edgecolor='#001D4A', lw=1.5)

    txt_goals = ax.text(x=63, y=67, s='Goals:',
                        size=18,
                        fontproperties=fm_rubik.prop, color=pitch.line_color)

    ax.add_patch(goals_rect)

    ### xGOT ###
    # ax.text(54.7, 62.5, total_xGOT, fontsize=12, ha='center', va='center', color='white', fontproperties=fm_rubik.prop)
    # xGOT_rect = FancyBboxPatch((53.5, 61.5), 2.4, 2.2, boxstyle="round,pad=0.3", facecolor='#001D4A',
    # edgecolor='#001D4A', lw=1.5)

    # txt_xGOT = ax.text(x=63, y=62, s='xGOT:',
    # size=18,
    # fontproperties=fm_rubik.prop, color=pitch.line_color)

    # ax.add_patch(xGOT_rect)

    # image = Image.open('bck.png')
    # add an image
    # ax_image = add_image(image, fig, left=0.0725, bottom=0.125, width=0.855,
    # alpha=0.3, interpolation='hanning')

    ### Shots ###
    ax.text(54.7, 62.5, total_shots, fontsize=12, ha='center', va='center', color='white', fontproperties=fm_rubik.prop)
    shots_rect = FancyBboxPatch((53.5, 61.5), 2.4, 2.2, boxstyle="round,pad=0.3", facecolor='#001D4A',
                                edgecolor='#001D4A', lw=1.5)

    txt_shots = ax.text(x=63, y=62, s='Shots:',
                        size=18,
                        fontproperties=fm_rubik.prop, color=pitch.line_color)

    ax.add_patch(shots_rect)

    ### Graph labels ###
    goal_icon = pitch.scatter(x=50.7, y=60.5,
                              # size varies between 100 and 1000 (points squared)
                              s=400,
                              c='#001D4A',  # color for scatter in hex format
                              edgecolors='#001D4A',  # give the markers a charcoal border
                              # for other markers types see: https://matplotlib.org/api/markers_api.html
                              marker='o',
                              alpha=0.5,
                              ax=ax)
    goal_label = ax.text(57.7, 50.7, 'Goals', fontsize=12, ha='center', va='center', color=pitch.line_color,
                         fontproperties=fm_rubik.prop)

    shot_icon = pitch.scatter(x=50.7, y=51.5,
                              # size varies between 100 and 1000 (points squared)
                              s=400,
                              c='#6d6a69',  # color for scatter in hex format
                              edgecolors='#6d6a69',  # give the markers a charcoal border
                              # for other markers types see: https://matplotlib.org/api/markers_api.html
                              marker='o',
                              alpha=0.5,
                              ax=ax)

    shot_label = ax.text(48.7, 50.7, 'Shots', fontsize=12, ha='center', va='center', color=pitch.line_color,
                         fontproperties=fm_rubik.prop)

    xG_icon = pitch.scatter(x=50.7, y=10,
                            # size varies between 100 and 1000 (points squared)
                            s=200,
                            c='#eee9e5',  # color for scatter in hex format
                            edgecolors='#6d6a69',  # give the markers a charcoal border
                            # for other markers types see: https://matplotlib.org/api/markers_api.html
                            marker='.',
                            alpha=0.5,
                            ax=ax)
    xG_icon = pitch.scatter(x=50.7, y=8.5,
                            # size varies between 100 and 1000 (points squared)
                            s=600,
                            c='#eee9e5',  # color for scatter in hex format
                            edgecolors='#6d6a69',  # give the markers a charcoal border
                            # for other markers types see: https://matplotlib.org/api/markers_api.html
                            marker='.',
                            alpha=0.5,
                            ax=ax)
    xG_icon = pitch.scatter(x=50.7, y=6.5,
                            # size varies between 100 and 1000 (points squared)
                            s=1250,
                            c='#eee9e5',  # color for scatter in hex format
                            edgecolors='#6d6a69',  # give the markers a charcoal border
                            # for other markers types see: https://matplotlib.org/api/markers_api.html
                            marker='.',
                            alpha=0.5,
                            ax=ax)

    xG_label = ax.text(4.7, 50.7, 'xG', fontsize=12, ha='center', va='center', color=pitch.line_color,
                       fontproperties=fm_rubik.prop)

    st.pyplot(plt)


data = load_data(app=3)

with st.sidebar:
    st.title('Shot Map Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox(
        'Select a League',
        ('Premier League', 'Bundesliga', 'Serie A', 'Ligue 1', 'La Liga'))
    data = data[data['league_name'] == leagues]
    data_teams = data['home_away'].unique()

    teams = st.selectbox(
        'Select a team',
        data_teams
    )
    data = data[(data['league_name'] == leagues) & (data['home_away'] == teams)]
    data_teams_players = data['player'].unique()
    players = st.selectbox(
        'Select a Player',
        data_teams_players)

player_shot_map(player=players)
