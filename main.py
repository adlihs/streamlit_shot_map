import pandas as pd
import duckdb
import os
import numpy as np
from PIL import Image
import matplotlib.image as mpimg

from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, add_image)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import to_rgba, LinearSegmentedColormap
import unicodedata

pd.set_option('display.max_columns', None)

