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

button = """
<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="edmundneil" data-color="#5F7FFF" data-emoji=""  data-font="Lato" data-text="Buy me a chocolate" data-outline-color="#000000" data-font-color="#ffffff" data-coffee-color="#FFDD00" style="background-color: black;" ></script>
"""

html(button, height=70, width=380)

st.markdown(
    """
    <style>
        iframe[width="380"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
            background-color: black;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
