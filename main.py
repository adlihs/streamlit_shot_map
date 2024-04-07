import pandas as pd
import duckdb
#import os
#import numpy as np
#from PIL import Image
#import matplotlib.image as mpimg

from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, add_image)
import matplotlib.pyplot as plt
#import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
#from matplotlib.colors import to_rgba, LinearSegmentedColormap
import unicodedata
import streamlit as st
from streamlit.components.v1 import html


st.header("Welcome!")
intro_text = '''On this site, you will discover a range of solutions 
that exemplify data analysis in soccer.

Please visit my LinkedIn and Tableau Public Profile
'''
st.text(intro_text)

st.markdown(f"[LinkedIn](https://www.linkedin.com/in/edmundneil)")
st.markdown(f"[Tableau Public Profile](https://public.tableau.com/app/profile/edmondneil/vizzes)")

#st.image('dataflow.png', caption='')

with st.sidebar:
    st.page_link("main.py", label="Home", icon="🏠")
    st.page_link("pages/goal_secuence.py", label="Goal Secuence", icon="⚽️")
    st.page_link("pages/pass_flow.py", label="Pass Flow", icon="🔄")
    st.page_link("pages/Pass_Network.py", label="Pass Network", icon="🕸️")
    st.page_link("pages/Player Recommendation.py", label="Player Recommendation", icon="🚀")
    st.page_link("pages/player_heatmap.py", label="Player Heatmap", icon="⚡")
    st.page_link("pages/player_pass_map.py", label="Player Pass Map", icon="➡️")
    st.page_link("pages/shot_map.py", label="Player Shot Map", icon="🎯")

