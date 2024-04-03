import pandas as pd
# import os
import numpy as np
import PIL.Image
# import matplotlib.image as mpimg

from mplsoccer import (Pitch, FontManager)
import matplotlib.pyplot as plt
# import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st
from utils.functions_file import load_data

# from functions_file import load_data, load_data_from_url

pd.set_option('display.max_columns', None)

import google.generativeai as genai
gem_api = 'AIzaSyAKKRcbonvFpJL5q6Il_50cHEWtoe60cxk'
genai.configure(api_key=gem_api)
model = genai.GenerativeModel('gemini-pro-vision')

def process_data(data, date, game, team_index):
    event_data = data.copy()
    event_data = event_data[(event_data['type'] != 'FormationSet') & (event_data['type'] != 'Start')]
    event_data = event_data[(event_data['game'] == game) &
                            (event_data['date'] == date)]
    event_data['pass_recipient_name'] = event_data['player'].shift(-1)
    event_data['pass_recipient_team'] = event_data['team'].shift(-1)

    if team_index == 1:
        team = event_data['team'].unique()[0]
    else:
        team = event_data['team'].unique()[1]

    sub = event_data.loc[event_data["type"] == "SubstitutionOff"].loc[event_data["team"] == team].iloc[0]["minute"]
    sub_players = event_data[(event_data['type'] == "SubstitutionOn") &
                             (event_data['team'] == team)]

    # make df with successfull passes by England until the first substitution
    mask_team1 = event_data[(event_data['type'] == 'Pass') &
                            (event_data['team'] == team) &
                            (event_data['minute'] <= sub) &
                            (event_data['outcome_type'] == 'Successful')]

    pass_team1 = mask_team1[
        ['x', 'y', 'end_x', 'end_y', "player", "team", "pass_recipient_name", "pass_recipient_team"]]
    pass_team1 = pass_team1[pass_team1['pass_recipient_team'] == team]
    pass_team1 = pass_team1[pass_team1['pass_recipient_name'].notna()]
    pass_team1 = pass_team1[
        ['x', 'y', 'end_x', 'end_y', "player", "pass_recipient_name"]]

    # Calculate Centralization
    # calculate number of successful passes by player
    no_passes = pass_team1.groupby(['player']).x.count().reset_index()
    no_passes.rename({'x': 'pass_count'}, axis='columns', inplace=True)
    # find one who made most passes
    max_no = no_passes["pass_count"].max()
    # calculate the denominator - 10*the total sum of passes
    denominator = 10 * no_passes["pass_count"].sum()
    # calculate the nominator
    nominator = (max_no - no_passes["pass_count"]).sum()
    # calculate the centralisation index
    centralisation_index = nominator / denominator

    mapeo = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ø': 'o', 'ñ': 'n', 'Ñ':'N', 'ë':'e','ã':'a','ï':'i',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ø': 'O', 'ü':'u','ğ':'g'
    }

    # Reemplazar las letras con tilde por las mismas letras sin tilde
    pass_team1['player'] = pass_team1['player'].apply(lambda x: ''.join([mapeo.get(char, char) for char in x]))
    pass_team1['pass_recipient_name'] = pass_team1['pass_recipient_name'].apply(
        lambda x: ''.join([mapeo.get(char, char) for char in x]))

    #### Calculate scatter features
    scatter_df = pd.DataFrame()
    for i, name in enumerate(pass_team1["player"].unique()):
        passx = pass_team1.loc[pass_team1["player"] == name]["x"].to_numpy()
        recx = pass_team1.loc[pass_team1["pass_recipient_name"] == name]["end_x"].to_numpy()
        passy = pass_team1.loc[pass_team1["player"] == name]["y"].to_numpy()
        recy = pass_team1.loc[pass_team1["pass_recipient_name"] == name]["end_y"].to_numpy()
        scatter_df.at[i, "player"] = name
        # make sure that x and y location for each circle representing the player is the average of passes and receptions
        scatter_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
        scatter_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))
        # calculate number of passes
        scatter_df.at[i, "no"] = pass_team1.loc[pass_team1["player"] == name].count().iloc[0]

    # adjust the size of a circle so that the player who made more passes
    scatter_df['marker_size'] = (scatter_df['no'] / scatter_df['no'].max() * 1500)
    # scatter_df = scatter_df[scatter_df['no'] >= 2]
    scatter_df['sub'] = np.where(scatter_df['player'].isin(sub_players['player']), 1, 0)

    ### Calculate line features
    # counting passes between players
    pass_team1["pair_key"] = pass_team1.apply(lambda x: "_".join(sorted([x["player"], x["pass_recipient_name"]])),
                                              axis=1)
    lines_df = pass_team1.groupby(["pair_key"]).x.count().reset_index()
    lines_df.rename({'x': 'pass_count'}, axis='columns', inplace=True)
    # setting a treshold. You can try to investigate how it changes when you change it.
    lines_df = lines_df[lines_df['pass_count'] >= 2]

    return scatter_df, lines_df, team, centralisation_index


def network_pass_viz(team_index):
    scatter_df, lines_df, team, centralization = process_data(data=data, date=Gdates, game=games, team_index=team_index)
    # st.dataframe(lines_df)
    # st.dataframe(scatter_df)
    # plot once again pitch and vertices
    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')
    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='#6d6a69',
                  pitch_color='#eee9e5')  # control the goal transparency
    fig, ax = pitch.draw(figsize=(12, 10))
    fig.set_facecolor("#eee9e5")

    for index, row in scatter_df.iterrows():
        if row['sub'] == 1:
            pitch.scatter(row.x, row.y,
                          s=row.marker_size,
                          color='#eee9e5',
                          edgecolors='#F1797F',#F1797F A5A2A1
                          linewidth=4,
                          alpha=1,
                          ax=ax, zorder=3)
        else:
            pitch.scatter(row.x, row.y,
                          s=row.marker_size,
                          color='#eee9e5',
                          edgecolors='#A5A2A1',  # F1797F A5A2A1
                          linewidth=4,
                          alpha=1,
                          ax=ax, zorder=3)


    for i, row in scatter_df.iterrows():
        pitch.annotate(row.player, xy=(row.x, row.y),
                       c='black',
                       va='center',
                       ha='center',
                       fontproperties=fm_rubik.prop,
                       # weight = "bold",
                       size=12, ax=ax, zorder=4)

    for i, row in lines_df.iterrows():
        player1 = row["pair_key"].split("_")[0]
        player2 = row['pair_key'].split("_")[1]

        # take the average location of players to plot a line between them
        player1_x = scatter_df.loc[scatter_df["player"] == player1]['x'].iloc[0]
        player1_y = scatter_df.loc[scatter_df["player"] == player1]['y'].iloc[0]
        player2_x = scatter_df.loc[scatter_df["player"] == player2]['x'].iloc[0]
        player2_y = scatter_df.loc[scatter_df["player"] == player2]['y'].iloc[0]
        num_passes = row["pass_count"]
        # adjust the line width so that the more passes, the wider the line
        line_width = (num_passes / lines_df['pass_count'].max() * 10)
        # plot lines on the pitch
        pitch.lines(player1_x, player1_y, player2_x, player2_y,
                    alpha=0.5, lw=line_width, zorder=2, color="#A5A2A1", ax=ax) #A5A2A1

    # fig.suptitle("England Passing Network against Sweden", fontsize = 30)
    txt_title_team = ax.text(x=0, y=109, s=str(team) + ' Pass Network',
                             size=40,
                             # here i am using a downloaded font from google fonts instead of passing a fontdict
                             fontproperties=fm_rubik.prop, color=pitch.line_color)
    txt_title_details = ax.text(x=0.1, y=104.5,
                                s=str(Gdates) + " | " + str(leagues) + " | " + str(
                                    games) + " | " + "Network Centralization: " + str(
                                    round((centralization * 100), 1)) + "%",
                                size=15,
                                fontproperties=fm_rubik.prop, color=pitch.line_color)
    # plt.show()
    fn = 'network_'+str(team_index)+ '_scatter.png'
    plt.savefig(fn)

    st.pyplot(plt)


# st.dataframe(data)

with st.sidebar:
    st.title('Pass Network Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga', 'Serie A',
                            'Ligue 1', 'La Liga', 'Premiership', 'Eredivisie', 'Primeira Liga', 'MLS',
                            'Jupiter ProLeague'))
    data = load_data(app=1, league=leagues)
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

# game_flow_pass_map(soccer_data=data, game_date=Gdates, game=games)


network_pass_viz(team_index=1)
fn = 'network_'+str(1)+ '_scatter.png'
with open(fn, "rb") as img:
    btn = st.download_button(
        label="Download image",
        data=img,
        file_name=fn,
        mime="image/png"
    )
network_pass_viz(team_index=2)
fn = 'network_'+str(2)+ '_scatter.png'
with open(fn, "rb") as img:
    btn = st.download_button(
        label="Download image",
        data=img,
        file_name=fn,
        mime="image/png"
    )
