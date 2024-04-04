import pandas as pd
# import os
import numpy as np
# import matplotlib.image as mpimg
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# import matplotlib.patches as patches
# from matplotlib.colors import to_rgba, LinearSegmentedColormap
import streamlit as st
from utils.functions_file import load_data

pd.set_option('display.max_columns', None)

# Define the dictionary
# Dictionario para homologar posiciones ya que hay jugadores que no tienen jugadores especificas
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
# Funcion que toma la posicion del jugador a evaluar y retorna las posiciones homologas del dictionario
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

# Carga de datos y seleccion de valores unicos de campos claves
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

# Sidebar con selectboxes para seleccion de liga, equipo y jugador
with st.sidebar:
    st.title('Select Player :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox(
        'Select a League',
        ('Premier League', 'La Liga', 'Ligue 1', 'Bundesliga', 'Serie A',
         'Eredivisie', 'Primeira Liga', 'Belgian Pro League',
         'Brasileiro Série A', 'Primera División',
         'Championship','Segunda División','Ligue 2','2. Bundesliga','Serie B'))
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
    st.page_link("main.py", label="Main Menu", icon="↩️")

### Selectboxes to filter the base of players to analyze and recommend
with st.popover("View Filters"):

    # Multiselect para filtrar ligas de los jugadores similares encontrados
    select_comp = st.multiselect(
        'Select a League',
        unique_tournament, key='s_comp',
        default='Premier League'
    )
    # Multiselect para filtrar edades de los jugadores similares encontrados
    start_age, end_age = st.select_slider(
        'Select a range of age',
        options=unique_age,
        value=(15, 40))

    # Multiselect para filtrar minutos de los jugadores similares encontrados
    start_min, end_min = st.select_slider(
        'Select a range of Minutes',
        options=unique_minutes,
        value=(1, max_minutes))

### ------------------------ ###
### Pasos para generar el dataset que se va a usar en la generacion de jugadores similares

# Metricas del jugadores seleccionado
select_player = data[data['Player'] == players]
attributes = load_data(app=2)

selected_player_position = select_player['PlayerPos'].unique()[0]

options = get_player_positions(selected_player_position)

# Se filtran la base de jugadores a usar para buscar similares con base em los filtros
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

# Funcion para obtener los jugadores similares
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
data_text = rec_result.to_string(index=False, header=True)

import google.generativeai as genai
from markdown_pdf import MarkdownPdf,Section




gem_api = 'AIzaSyAKKRcbonvFpJL5q6Il_50cHEWtoe60cxk'
genai.configure(api_key=gem_api)
model = genai.GenerativeModel('gemini-pro')
#order_txt = "Based on the next data, write a soccer scouting report for each player on it, do not use bullet list, write a paragraph, is an obligation use and mention their metrics available in the data:  " + data_text

text_string = f"This data with the next columns meaning: "
text_string += f"""
'Squad' as 'Team',
'Comp' as 'League',
'Player' as 'Player',
'Nation' as 'Player Nationality',
'Age' as 'Player Age',
'PlayerPos' as 'Player Position',
'TklW_Tackles' as 'Tackles Won',
'Int' as 'Interceptions',
'Clr' as 'Clearences',
'Sh_Blocks' as 'Shot Blocks',
'Pass_Blocks' as 'Pass Blocks',
'Tkl+Int' as 'Tackles plus Interceptions',
'SCA90_SCA' as 'SCA per 90',
'GCA90_GCA' as 'GCA per 90',
'Recov' as 'Recoveries',
'Won_Aerial_Duels' as 'Won Aerial Duels',
'Won_percent_Aerial_Duels' as 'Won Aerial Duels percentage',
'Cmp_Total' as 'Total Pass Completed',
'Cmp_percent_Total' as 'Total Pass Completed percentage',
'Cmp_Short' as 'Total Short Pass Completed',
'Cmp_percent_Short' as 'Total Short Pass Completed percentage',
'Cmp_Medium' as 'Total Medium Pass Completed',
'Cmp_percent_Medium' as 'Total Medium Pass Completed',
'Cmp_Long' as 'Total Long Pass Completed',
'Cmp_percent_Long' as 'Total Long Pass Completed percentage',
'Ast' as Assist,
'xAG' as 'Expected Assisted Goal',
'xA_Expected' as 'Expected Assists',
'PPA' as 'Passes Into Penalty Area',
'CrsPA' as 'Crosses Into Penalty Area',
'PrgP' as 'Progressive Passes',
'KP' as 'Key Passes',
'Final_Third' as 'Passes Into Final Third',
'Min_Playing_Time' as 'Playing Time Minutes',
'Starts_Starts' as 'Starts',
'Mn_per_Start_Starts' as 'Minutes Per Starts',
'Compl_Starts' as 'Completed Matches Played',
'Subs_Subs' as 'Substitute Appearances',
'Mn_per_Sub_Subs' as 'Minutes Per Substitution',
'Touches_Touches' as Touches,
'Def Pen_Touches' as Touches in Defensive Penalty Area,
'Def 3rd_Touches' as Touches in Defensive Third,
'Mid 3rd_Touches' as Touches in Middle Third,
'Att 3rd_Touches' as Touches in Attacking Third,
'Att Pen_Touches' as Touches in Attacking Penalty Area,
'Live_Touches' as Live Touches,
'Att_Take_Ons' as Attacking Take Ons,
'Succ_Take_Ons' as Successful Take Ons,
'Succ_percent_Take_Ons' as Successful Take Ons percentage,
'Tkld_Take_Ons' as Takled Take Ons,
'Tkld_percent_Take_Ons' as Tackled Take Ons percentage,
'Carries_Carries' as Carries,
'TotDist_Carries' as Carries Total Distance,
'PrgDist_Carries' as Progressive Carries Distance,
'PrgC_Carries' as Progressive Carries,
'Final_Third_Carries' as Final Third Carries,
'CPA_Carries' as Carries Into Penalty Areas,
'Mis_Carries' as Miscontrol Carries,
'Dis_Carries' as Dispossessesd Carries,
'Rec_Receiving' as Passes Received,
'PrgR_Receiving' as Progressive Passes Received,
'Gls_Standard' as Goals,
'Sh_Standard' as Shots,
'SoT_Standard' as Shots On Target,
'SoT_percent_Standard' as Shot on Target percentage,
'Sh_per_90_Standard' as 'Shots per 90',
'SoT_per_90_Standard' as 'Shots On Target Per 90',
'G_per_Sh_Standard' as Goals Per Shot,
'G_per_SoT_Standard' as Goals Per Shot On Target,
'Dist_Standard' as Shot Distance,
'FK_Standard' as Free Kicks,
'PK_Standard' as Penalty Kicks,
'PKatt_Standard' as Penalty Kicks attempted,
'xG_Expected' as Expected Goals,
'npxG_Expected' as Non Penalty Expected Goals,
'npxG_per_Sh_Expected' as Non Penalty Expected Goals per Shot,
'G_minus_xG_Expected' as Goals minus Expected Goals,
'np:G_minus_xG_Expected' as Non Penalty Goals minus Expected Goals,
'Gls' as Goals,
'G+A' as Goals plus Assists,
'G_minus_PK' as Goals minus Penalty Kicks,
'xAG_Expected' as Expected Assisted Goals,
'npxG+xAG_Expected' as Non Penalty Goals plus Expected Assisted Goals,
'Gls_Per_Minutes' as Goals Per Minutes,
'Ast_Per_Minutes' as Assists Per Minutes,
'G+A_Per_Minutes' as Goals plus Assists Per Minutes,
I'm scouting those players in the data, please understand the columns names and column meaning mentioned before and based on player position select the key column metrics and write a scout report for every player in the column 'Player', with the next format:
Player Name, 
Age, 
Nationality, 
Team, 
League, 
Key Metrics 
and paragraph with the report based on key metrics, is mandatory include all the players in the data: {rec_result} 
"""
#write a simple soccer player scout report for each player on it based on their key metrics in the dataframe, please use the player position in the column PlayerPos to determine which metrics are need it in the report, metrics must be included always in a paragraph style: {rec_result}
# by player position what are the key metrics based on columns and with that metrics write a player scout report for every player in the data: {rec_result}
order_txt = str(text_string) #+ data_text

viz = st.button("View AI Scout Report", type="primary")

if viz:
    response = model.generate_content(order_txt)
    st.markdown(response.text)

    ### Generacion de PDF
    pdf = MarkdownPdf(toc_level=1)
    leagues_txt  = ', '.join(select_comp)
    pdf.add_section(Section("# Technical Scout: " + str(players) + "\n"
                            + "Leagues: " + str(leagues_txt) + " | " + "Between " + str(int(start_age)) + " and " + str(int(end_age)) + " | " + "At least " + str(int(start_min)) + " minutes" + "\n"
                            + "\n" + response.text ,toc=False))
    pdf.save("AI Technical Scout Report.pdf")

    with open("AI Technical Scout Report.pdf", "rb") as file:
        btn = st.download_button(
                label="Download Report",
                data=file,
                file_name="AI_Technical_Report.pdf"
                #mime="image/png"
              )
