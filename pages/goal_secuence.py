import pandas as pd
# import google.generativeai as genai
import google.generativeai as genai
from mplsoccer import (Pitch, FontManager)
import matplotlib.pyplot as plt
import PIL.Image
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st
import os
from utils.functions_file import load_data
from dotenv import load_dotenv

def goals_previous_actions(actions_data, team):
    pass_df = actions_data[(actions_data['league'] == leagues) &
                           (actions_data['team'] == team) &
                           (actions_data['type'] == 'Goal')]

    # pass_df = pd.DataFrame()
    pass_df_tmp = pd.DataFrame()
    actions_df = pd.DataFrame()

    filas = [fila for fila in pass_df.itertuples()]

    for fila in filas:
        # st.text(fila.Index)
        indx = fila.Index

        # st.dataframe(actions_data.query("index >= (@indx-5) and index <= @indx "))
        pass_df_tmp = actions_data.query("index >= (@indx-5) and index <= @indx ")
        pass_df_tmp['x_siguiente'] = pass_df_tmp['x'].shift(-1)
        pass_df_tmp['y_siguiente'] = pass_df_tmp['y'].shift(-1)
        pass_df_tmp['goal_index'] = fila.minute
        actions_df = pd.concat([actions_df, pass_df_tmp])

    # st.dataframe(actions_df)
    return actions_df


def viz_previous_events(soccer_data=None, game=None, team=None, minute=None):
    # Load environment variables from .env file

    load_dotenv(dotenv_path='.env')

    # Access variables
    os.environ["gem_api"] = st.secrets["gem_api"]
    gem_api = os.environ.get('gem_api')  # env




    genai.configure(api_key=gem_api)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # soccer_data = soccer_data.sort_values(by=["date", "game", "minute", "second"])

    soccer_data = soccer_data[(soccer_data['goal_index'] == minute)]
    soccer_data = soccer_data.reset_index()

    # st.dataframe(soccer_data)
    goal_data = soccer_data[soccer_data['type'] == 'Goal']

    goal_player = goal_data['player'].unique()[0]
    goal_team = goal_data['team'].unique()[0]
    league = goal_data['league'].unique()[0]
    date_game = goal_data['date'].unique()[0]

    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')

    # Setup pass flow for Team 1
    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='#01161E',
                  pitch_color='#eee9e5')  # control the goal transparency
    fig, ax = pitch.draw(figsize=(12, 10))
    fig.set_facecolor("#eee9e5")  # you can also adjust the transparency (alpha)

    pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                           ['#eee9e5', '#2f3e46'], N=100)

    def modificar_fila_anterior(df, indice, columna1, columna2, valor1, valor2):
        """
        Modifica los valores de dos columnas en la fila previa a un índice en un DataFrame.

        Args:
            df: El DataFrame.
            indice: El índice de la fila a partir de la cual se busca la fila anterior.
            columna1: La primera columna a modificar.
            columna2: La segunda columna a modificar.
            valor1: El nuevo valor para la primera columna.
            valor2: El nuevo valor para la segunda columna.

        Returns:
            El DataFrame modificado.
        """
        # Pendiente evaluar si la accion anterior es un pase!!!!
        # Actualziacion de las columnas x_siguiente y y_siguiente de la fila anterior a la de la accion
        # del rival
        df['temp_index'] = df.index
        fila_anterior = df.query("temp_index == (@indice-1)")
        df = df.drop('temp_index', axis=1)
        fila_anterior[columna1] = valor1
        fila_anterior[columna2] = valor2
        df.loc[fila_anterior.index] = fila_anterior

        # Actualziacion de las columnas x y y de la fila  de la accion del rival
        df['temp_index'] = df.index
        fila_actual = df.query("temp_index == (@indice)")
        df = df.drop('temp_index', axis=1)
        fila_actual['x'] = valor1
        fila_actual['y'] = valor2
        df.loc[fila_actual.index] = fila_actual

        return df

    #### Cambiar los valores de las posiciones de las acciones rivales
    for row in soccer_data.itertuples():
        indx_rival = soccer_data[soccer_data.index == row.Index]
        rival_team = str(indx_rival['team'].unique()[0])
        # st.text(rival_team)
        # st.text(goal_team)

        if str(goal_team) != str(rival_team):
            soccer_data = modificar_fila_anterior(soccer_data, row.Index, 'x_siguiente', 'y_siguiente', (100 - row.x),
                                                  (100 - row.y))
            # st.dataframe(soccer_data)

    # Se recorre el DF para ir ploteando lineas y circulos de las acciones del gol
    for row in soccer_data.itertuples():
        if row.team == goal_team:
            action_type = row.type
            if action_type == "Pass":
                if row.Index == 0:
                    scatters = pitch.scatter(row.x, row.y, color='blue', s=157,
                                             zorder=10, ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="white",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       transparent=True,
                                       n_segments=100,
                                       color='black',
                                       ax=ax)
                    arrow_line = pitch.arrows(row.x, row.y,
                                              ((row.x + row.x_siguiente) / 2), ((row.y + row.y_siguiente) / 2),
                                              width=1,
                                              zorder=9,
                                              headwidth=8,
                                              color='black',
                                              ax=ax)
                    # Other actions related to passing...
                else:
                    scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                             edgecolors='black', zorder=10, ax=ax)
                    scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                             edgecolors='black',
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="black",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       transparent=True,
                                       n_segments=100,
                                       color='black',
                                       ax=ax)
                    arrow_line = pitch.arrows(row.x, row.y,
                                              ((row.x + row.x_siguiente) / 2), ((row.y + row.y_siguiente) / 2),
                                              width=1,
                                              zorder=9,
                                              headwidth=8,
                                              color='black',
                                              ax=ax)
                    # Other actions related to passing...
            else:
                if row.Index == 5:
                    scatters = pitch.scatter(row.x, row.y, color='red', s=157,
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="white",
                                   ax=ax)
                    # Other actions related to non-passing...
                elif row.Index == 0:
                    scatters = pitch.scatter(row.x, row.y, color='blue', s=157,
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="white",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       color='black',
                                       linestyle='dashed',
                                       ax=ax)
                else:
                    scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                             edgecolors='black',
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="black",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       color='black',
                                       linestyle='dashed',
                                       ax=ax)

        else:  # ELSE PRINCIPAL

            action_type = row.type
            if action_type == "Pass":
                if row.Index == 0:
                    scatters = pitch.scatter(row.x, row.y, color='blue', s=157,
                                             zorder=10, ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="white",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       transparent=True,
                                       n_segments=100,
                                       color='black',
                                       ax=ax)
                    arrow_line = pitch.arrows(row.x, row.y,
                                              ((row.x + row.x_siguiente) / 2), ((row.y + row.y_siguiente) / 2),
                                              width=1,
                                              zorder=9,
                                              headwidth=8,
                                              color='black',
                                              ax=ax)
                    # Other actions related to passing...
                else:
                    scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                             edgecolors='black', zorder=10, ax=ax)
                    scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                             edgecolors='black',
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="black",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       transparent=True,
                                       n_segments=100,
                                       color='black',
                                       ax=ax)
                    arrow_line = pitch.arrows(row.x, row.y,
                                              ((row.x + row.x_siguiente) / 2), ((row.y + row.y_siguiente) / 2),
                                              width=1,
                                              zorder=9,
                                              headwidth=8,
                                              color='black',
                                              ax=ax)
                    # Other actions related to passing...
            else:
                if row.Index == 5:
                    scatters = pitch.scatter(row.x, row.y, color='red', s=157,
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="white",
                                   ax=ax)
                    # Other actions related to non-passing...
                elif row.Index == 0:
                    scatters = pitch.scatter(row.x, row.y, color='blue', s=157,
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="white",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       color='black',
                                       linestyle='dashed',
                                       ax=ax)
                else:
                    scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                             edgecolors='black',
                                             # alpha=0.5,
                                             zorder=10,
                                             ax=ax)
                    pitch.annotate(row.Index, xy=(row.x, row.y),
                                   va='center',
                                   ha='center',
                                   zorder=11,
                                   color="black",
                                   ax=ax)
                    line = pitch.lines(row.x, row.y,
                                       row.x_siguiente, row.y_siguiente,
                                       lw=1,
                                       color='black',
                                       linestyle='dashed',
                                       ax=ax)

    txt_title_team = ax.text(x=0, y=109, s=goal_player + ' goal',
                             size=40,
                             # here i am using a downloaded font from google fonts instead of passing a fontdict
                             fontproperties=fm_rubik.prop, color='#0D2C54')

    ax.text(x=0.1, y=104.5,
            s=str(goal_team) + " | " + str(league) + " | " + str(game) + " | " + str(date_game) +
              " | " + "Minute: " + str(minute),
            size=15,
            fontproperties=fm_rubik.prop,
            color=pitch.line_color)

    ### Goal AI narrative

    narrative_df = soccer_data[['team', 'player', 'minute', 'second', 'type', 'x', 'y']].rename(
        columns={'type': 'action'})
    narra_df =narrative_df.copy()
    narrative_df = narrative_df.reset_index()

    text = narrative_df.to_string(index=False, header=True)
    #print(text)

    order_txt = "I'm going to give you a Index, team, player name, minute, second and action for a soccer game goal, to help you understand the position of the action the pitch widht is 100 and the height is 100, so analize the position of the action, do not include coordinates, and please re-create briefly the play using the data, use only the information provided, put between () the Index, include all the actions for the teams in order based on the Index, and i want a bulleted list:" + text


    #order_txt2 = "The next data is for a secuence of action before a goal is scored, please analyze it and write a brief and simple description of the play as a soccer commentator, use only the information provided in the order provided:  " + text
    #response2 = model.generate_content(order_txt2)

    #order_txt2 = f"The next dataframe {narra_df} with the next columns {narra_df.columns}, this data is for actions previous a goal in a soccer game, please use it to write a description of all the play previous a goal is scored as football commentator using only the data in the dataframe provided."
    #response2 = model.generate_content(order_txt2)
    # print(response.text)

    # ax.text(x=0.1, y=0.5,
    #        s=response.text,
    #        size=10,
    #        fontproperties=fm_rubik.prop,
    #        color=pitch.line_color)
    fn = 'goal_secuence.png'
    plt.savefig(fn)
    st.pyplot(plt)
    with open(fn, "rb") as img:
        btn = st.download_button(
            label="Download image",
            data=img,
            file_name=fn,
            mime="image/png"
        )

    response = model.generate_content(order_txt)

    st.markdown('***AI GOAL DESCRIPTION***')
    st.markdown(response.text)
    #st.markdown('***AI GOAL COMMENTATOR***')
    #st.markdown(response2.text)





with st.sidebar:
    st.title('Goal Secuence Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga', 'Serie A', 'Ligue 1','EURO',
                            'La Liga','Premiership','Eredivisie','Primeira Liga',
                            'MLS','Jupiter ProLeague','UCL','EUL','Championship (ENG)','Premier League (RUS)'))
    data = load_data(app=1,league=leagues)
    base_data = data.copy()
    data = data[data['league'] == leagues]

    data_teams = data['team'].unique()

    teams = st.selectbox(
        'Select a team',
        data_teams
    )
    data = data[(data['league'] == leagues) & (data['team'] == teams)]
    data_games = data['game'].unique()

    games = st.selectbox(
        'Select a Game',
        data_games)

    data = data[
        (data['league'] == leagues) & (data['team'] == teams) & (data['game'] == games) & (data['type'] == 'Goal')]
    data_minutes = data['minute'].unique()

    minutes = st.selectbox(
        'Select a Goal Minute',
        data_minutes)

    viz = st.button("Apply", type="primary")
    st.page_link("main.py", label="Main Menu", icon="↩️")

base_data = base_data[(base_data['league'] == leagues) &
                      (base_data['game'] == games)]

if viz and data_minutes.shape[0] > 0:
    goals_previous_actions_df = goals_previous_actions(actions_data=base_data, team=teams)
    viz_previous_events(soccer_data=goals_previous_actions_df, game=games, minute=minutes)
elif not viz and data_minutes.shape[0] == 0:
    st.text('No goals to display. Select another game...')
elif viz and data_minutes.shape[0] == 0:
    st.text('No goals to display. Select another game...')
