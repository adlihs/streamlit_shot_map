import pandas as pd
import streamlit as st
import unicodedata


def eliminar_tildes(texto):
    texto_nfd = unicodedata.normalize('NFD', texto)
    texto_limpio = ''.join(c for c in texto_nfd if not unicodedata.combining(c))
    return texto_limpio


"""
def load_data(app, league):
    if app == 1:  # goal_secuence, pass_flow, player_heatmap, player_pass_map
        event_data = pd.concat(map(pd.read_parquet, [
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ENG_match_events.parquet',
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/GER_match_events.parquet',
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ITA_match_events.parquet',
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ESP_match_events.parquet',
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/SCO_match_events.parquet',
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/NED_match_events.parquet',
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/POR_match_events.parquet',
            # 'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/FRA_match_events.parquet']))
            'https://github.com/adlihs/streamlit_shot_map/releases/download/soccer/match_events.parquet']))

        event_data[['date', 'game']] = event_data['game'].str.split(" ", n=1, expand=True)
        event_data['season'] = '23-24'
        event_data = event_data[event_data['league'] == league]

        event_data = event_data[event_data['player'].notna()]

        mapeo = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ø': 'o',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ø': 'O'
        }

        # Reemplazar las letras con tilde por las mismas letras sin tilde
        event_data['player'] = event_data['player'].apply(lambda x: ''.join([mapeo.get(char, char) for char in x]))

        return event_data

    elif app == 2:  # player_recommendation
        player_data = pd.read_csv(
            'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/player_unique_recommendations.csv')
        #
        # Aplicar la función a la columna 'texto'
        player_data['Player'] = player_data['Player'].apply(eliminar_tildes)

        return player_data

    elif app == 3:  # shot_map

        shot_data = pd.concat(map(pd.read_excel, [
            'data/GER_team_season_shots.xlsx',
            'data/ITA_team_season_shots.xlsx',
            'data/FRA_team_season_shots.xlsx',
            'data/ESP_team_season_shots.xlsx',
            'data/epl_team_season_shots.xlsx']), ignore_index=True)

        # Cambiar 'h' por el valor de la columna 'home_team'
        shot_data.loc[shot_data['home_away'] == 'h', 'home_away'] = shot_data['home_team']

        # Cambiar 'a' por el valor de la columna 'away_team'
        shot_data.loc[shot_data['home_away'] == 'a', 'home_away'] = shot_data['away_team']

        # Aplicar la función a la columna 'texto'
        shot_data['player'] = shot_data['player'].apply(eliminar_tildes)

        return shot_data
"""


@st.cache_data
def load_data(app, league=None):
    if app == 1:  # goal_secuence, pass_flow, player_heatmap, player_pass_map
        if league == 'Premier League':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ENG_match_events.parquet')
        elif league == 'Bundesliga':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/GER_match_events.parquet')

        elif league == 'Serie A':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ITA_match_events.parquet')

        elif league == 'Ligue 1':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/FRA_match_events.parquet')

        elif league == 'La Liga':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ESP_match_events.parquet')

        elif league == 'Premiership':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/SCO_match_events.parquet')

        elif league == 'Eredivisie':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/NED_match_events.parquet')

        elif league == 'MLS':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/MLS_match_events.parquet')

        elif league == 'Jupiter ProLeague':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/BEL_match_events.parquet')

        elif league == 'Primeira Liga':
            event_data = pd.read_parquet(
                'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/POR_match_events.parquet')

        event_data[['date', 'game']] = event_data['game'].str.split(" ", n=1, expand=True)
        event_data['season'] = '23-24'
        event_data = event_data[event_data['league'] == league]

        event_data = event_data[event_data['player'].notna()]

        mapeo = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ø': 'o',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ø': 'O'
        }

        # Reemplazar las letras con tilde por las mismas letras sin tilde
        event_data['player'] = event_data['player'].apply(lambda x: ''.join([mapeo.get(char, char) for char in x]))

        return event_data

    elif app == 2:  # player_recommendation
        player_data = pd.read_csv(
            'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/player_unique_recommendations.csv')
        #
        # Aplicar la función a la columna 'texto'
        player_data['Player'] = player_data['Player'].apply(eliminar_tildes)

        return player_data

    elif app == 3:  # shot_map

        shot_data = pd.concat(map(pd.read_excel, [
            'data/GER_team_season_shots.xlsx',
            'data/ITA_team_season_shots.xlsx',
            'data/FRA_team_season_shots.xlsx',
            'data/ESP_team_season_shots.xlsx',
            'data/epl_team_season_shots.xlsx']), ignore_index=True)

        # Cambiar 'h' por el valor de la columna 'home_team'
        shot_data.loc[shot_data['home_away'] == 'h', 'home_away'] = shot_data['home_team']

        # Cambiar 'a' por el valor de la columna 'away_team'
        shot_data.loc[shot_data['home_away'] == 'a', 'home_away'] = shot_data['away_team']

        # Aplicar la función a la columna 'texto'
        shot_data['player'] = shot_data['player'].apply(eliminar_tildes)

        return shot_data
