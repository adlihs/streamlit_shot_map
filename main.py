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

