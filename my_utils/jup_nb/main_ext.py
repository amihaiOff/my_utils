
"""
This runs some common code for notebooks.

Usage: When in IPython notebook, run

    %load_ext main_ext
"""


def load_ipython_extension(ipython):
    """
    :type ipython: ipykernel.zmqshell.ZMQInteractiveShell
    """
    ipython.run_cell(
        _main()
    )
    return


def _main():
    return """
    %reload_ext autoreload
    %autoreload 2

    import numpy as np, 
    import pandas as pd, 
    import matplotlib.pyplot as plt
    import plotly.express as px
    import plotly.graph_objects as go

    import json, os, sys, tempfile, requests
    from collections import *
    from operator import *
    from itertools import *
    from ipywidgets import *

    from my_utils.numbers import *
    from my_utils.readers import *

    pd_float_format(3)
    pd_df_num_rows(100)
    pd.options.display.max_colwidth = 1000
    pd.options.plotting.backend = "plotly"
    
    print('===============')
    print('Loaded: numpy, pandas, matplotlib, plotly(px, go), ipywidgets, json, os, sys, tempfile, requests')
    print('Loaded all from: collections, itertools, operator')
    print('===============')
    print(f'interpreter path: {sys.executable}')
    print('===============')
    print('using plotly as pd plotting backend')
    print('===============')
    """
