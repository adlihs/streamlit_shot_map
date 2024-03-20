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
from functions_file import load_data

pd.set_option('display.max_columns', None)

# Define the dictionary
player_positions = {
    'Centre-Back': ['Centre-Back', 'DF'],
    'Defensive Midfield': ['Defensive Midfield', 'midfield', 'MF'],
    'Left-Back': ['Left-Back', 'DF'],
    'Left Winger': ['Left Winger', 'FW', 'attack'],
    'Central Midfield': ['Central Midfield', 'midfield', 'MF'],
    'Centre-Forward': ['Centre-Forward', 'attack', 'FW'],
    'Right-Back': ['Right-Back', 'DF'],
    'FW': ['FW', 'attack', 'Centre-Forward', 'Second Striker'],
    'DF': ['DF', 'Centre-Back', 'Left-Back', 'Right-Back'],
    'MF': ['MF', 'Defensive Midfield', 'Central Midfield', 'Attacking Midfield', 'Left Midfield', 'Right Midfield',
           'midfield'],
    'Attacking Midfield': ['Attacking Midfield', 'midfield', 'MF'],
    'Right Winger': ['Right Winger', 'FW', 'attack'],
    'Left Midfield': ['Left Midfield', 'midfield', 'MF'],
    'midfield': ['midfield', 'Defensive Midfield', 'Central Midfield', 'Attacking Midfield', 'Left Midfield',
                 'Right Midfield',
                 'midfield'],
    'attack': ['attack', 'Centre-Forward', 'FW', 'Second Striker'],
    'Right Midfield': ['Right Midfield', 'midfield', 'MF'],
    'Second Striker': ['Second Striker', 'FW', 'attack']
}


# Define a function to get positions based on a key
def get_player_positions(position):
    """
  This function takes a player position as input and returns a list of associated options from the player_positions dictionary.

  Args:
      position: The player position to look up (e.g., "Centre-Back").

  Returns:
      A list of options associated with the given position, or an empty list if the position is not found.
  """
    if position in player_positions:
        return player_positions[position]
    else:
        return []


data = load_data(app=2)
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
    select_player_data = select_player_data[
        (select_player_data['Comp'] == leagues) & (select_player_data['Squad'] == teams)]
    data_teams_players = select_player_data['Player'].unique()
    players = st.selectbox(
        'Select a Player',
        data_teams_players)

### Selectboxes to filter the base of players to analyze and recommend


select_comp = st.multiselect(
    'Select a League',
    unique_tournament, key='s_comp',
    default='Premier League'
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
attributes = load_data(app=2)
selected_player_position = select_player['PlayerPos'].unique()[0]

options = get_player_positions(selected_player_position)
print(options)
attributes = attributes[
    (attributes['PlayerPos'].isin(options))
    & (attributes['Age'] <= end_age)
    & (attributes['Comp'].isin(select_comp))
    & (attributes['Min_Playing_Time'] >= start_min)
    & (attributes['Min_Playing_Time'] <= end_min)]

# attributes = attributes.append(select_player)
attributes = pd.concat([attributes, select_player], ignore_index=True)

att_players_names = attributes.copy()
attributes = attributes.iloc[:, 7:]

attributes = attributes.fillna(0)

bck_attributes = attributes.copy()
bck_attributes['Player'] = att_players_names['Player']

bck_attributes = bck_attributes.reset_index(drop=True)
attributes = attributes.reset_index(drop=True)

scaled = StandardScaler()
x = scaled.fit_transform(attributes)

recommendations = NearestNeighbors(n_neighbors=11, algorithm='auto', p=2).fit(x)
player_index = recommendations.kneighbors(x)[1]


def get_player_index(x):
    # bck_atributos = bck_atributos.reset_index(drop=True)
    return bck_attributes[bck_attributes['Player'] == x].index.tolist()[0]


def recommend_players(player, data_to_filter):
    # print('Here are 5 players similar to', player, ':' '\n')
    index = get_player_index(player)
    player_list = []
    for i in player_index[index][1:]:
        p_tmp = bck_attributes.iloc[i]['Player']
        if player != p_tmp:
            player_list.append(bck_attributes.iloc[i]['Player'])

    filtered_df = data_to_filter[data_to_filter['Player'].isin(player_list) &
                                 (data_to_filter['Comp'].isin(select_comp)) &
                                 (data_to_filter['PlayerPos'].isin(options)) &
                                 (data_to_filter['Min_Playing_Time'] >= start_min)]
    filtered_df = filtered_df.iloc[:, 1:]
    filtered_df = filtered_df.drop_duplicates()
    return filtered_df


rec_result = recommend_players(players, data_to_filter=load_data(app=2))
### ------------------------ ###

# player_shot_map(player=players)
# st.dataframe(unique_age)
st.dataframe(rec_result)

# st.text(rec_result['Player'].unique())
