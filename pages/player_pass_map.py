import pandas as pd
import PIL.Image
from mplsoccer import (Pitch, FontManager)
import matplotlib.pyplot as plt

from highlight_text import ax_text
import streamlit as st
from utils.functions_file import load_data

# from functions_file import load_data, load_data_from_url

pd.set_option('display.max_columns', None)


def player_pass_maps(data, player_name, type):
    if type == 'All Games':
        player_pass_data = data[(data['player'] == player_name) &
                                (data['type'] == 'Pass')]
        title = 'All Games'

    else:
        player_pass_data = data[(data['player'] == player_name) &
                                (data['type'] == 'Pass') &
                                (data['game'] == games)]
        title = games

    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')

    team_n = player_pass_data['team'].unique()[0]
    league_n = player_pass_data['league'].unique()[0]
    season_n = player_pass_data['season'].unique()[0]
    player_n = player_pass_data['player'].unique()[0]


    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='#6d6a69',
                  pitch_color='#eee9e5')  # control the goal transparency
    fig, ax = pitch.draw(figsize=(12, 10))
    fig.set_facecolor("#eee9e5")

    successful_passes = player_pass_data[player_pass_data['outcome_type'] == 'Successful']
    unsuccessful_passes = player_pass_data[player_pass_data['outcome_type'] == 'Unsuccessful']

    # --- Pass metrics
    succ_pass = successful_passes.shape[0]
    un_succ_pass = unsuccessful_passes.shape[0]
    total_passes = succ_pass + un_succ_pass
    pass_com = (succ_pass / total_passes) * 100

    # Detalle del texto de metricas de pases
    annotation_string = (f'Total:<{int(total_passes)}> \n'
                         f'Successful:<{int(succ_pass)}> \n'
                         f'Incompleted:<{int(un_succ_pass)}> \n'
                         f'Pass Completion:<{int((pass_com))}%>')

    # Configuracion para el highlight de los textos de metricas
    highlight_textprops = [{"fontsize": 15, "color": '#0D2C54', "fontweight": 'bold'},
                           {"fontsize": 15, "color": 'green', "fontweight": 'bold'},
                           {"fontsize": 15, "color": '#FB4D3D', "fontweight": 'bold'},
                           {"fontsize": 15, "color": '#0D2C54', "fontweight": 'bold'}]

    # Ubicacion del texto con detalle de metricas
    ax_text(80.2, 108.5, annotation_string, ha='left', va='center', fontsize=15,
            highlight_textprops=highlight_textprops,
            fontproperties=fm_rubik.prop,
            color=pitch.line_color,
            # fontproperties=fm_scada.prop,  # using the fontmanager for the google font
            ax=ax)

    # --- Successful passes
    pass_line = pitch.lines(successful_passes.x,
                            successful_passes.y,
                            successful_passes.end_x,
                            successful_passes.end_y,
                            #linestyle='dashed',
                            lw=1,
                            color='green',
                            ax=ax)

    pass_start = pitch.scatter(successful_passes.x,
                               successful_passes.y,
                               color='green', s=32, alpha=0.5, ax=ax)

    # --- Unsuccessful passes
    pass_line = pitch.lines(unsuccessful_passes.x,
                            unsuccessful_passes.y,
                            unsuccessful_passes.end_x,
                            unsuccessful_passes.end_y,
                            #linestyle='dashed',
                            lw=1,
                            color='red',
                            ax=ax)

    pass_start = pitch.scatter(unsuccessful_passes.x,
                               unsuccessful_passes.y,
                               color='red', s=32, alpha=0.5, ax=ax)

    txt_title_team = ax.text(x=0, y=109, s=player_n + ' passes',
                             size=40,
                             # here i am using a downloaded font from google fonts instead of passing a fontdict
                             fontproperties=fm_rubik.prop, color=pitch.line_color)

    ax.text(x=0.1, y=104.5,
            s=str(team_n) + " | " + str(league_n) + " | " + str(title),
            size=15,
            fontproperties=fm_rubik.prop,
            color=pitch.line_color)

    fn = 'player_pass_map.png'
    plt.savefig(fn)
    st.pyplot(plt)
    with open(fn, "rb") as img:
        btn = st.download_button(
            label="Download image",
            data=img,
            file_name=fn,
            mime="image/png"
        )



# st.dataframe(data)

with st.sidebar:
    st.title('Player Pass Map Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga', 'Serie A',
                            'Ligue 1','La Liga','Premiership','Eredivisie','Primeira Liga','EURO','AMERICA', 'WC Club',
                            'MLS','Jupiter ProLeague','UCL','EUL','Championship (ENG)','Premier League (RUS)'))
    data = load_data(app=1,league=leagues)
    data = data[data['league'] == leagues]
    data_teams = data['team'].unique()

    selected_team = st.selectbox(
        'Select a Team',
        data_teams
    )
    data = data[(data['league'] == leagues) &
                (data['team'] == selected_team)]

    data_players = data['player'].unique()

    selected_player = st.selectbox(
        'Select a Player',
        data_players
    )
    data = data[(data['league'] == leagues) &
                (data['player'] == selected_player)]
    data_games = data['game'].unique()

    games = st.selectbox(
        'Select a Game',
        data_games)

    viz_type = st.radio(label="Type of viz",
                        options=["All Games", "By Game"])

    viz = st.button("Apply", type="primary")
    st.page_link("main.py", label="Main Menu", icon="↩️")

if viz:
    player_pass_maps(data=data, player_name=selected_player, type=viz_type)
