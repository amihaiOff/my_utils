import numpy as np
from typing import Any

import pandas as pd
import plotly.graph_objects
from IPython.core.display import display
from ipywidgets import Dropdown, HBox, Label, Layout, Output, VBox
from pandas.core.groupby import DataFrameGroupBy
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from ..utils import grouped


class DictViewer(VBox):
    """
    Display dict values according to dropdown of keys.
    Useful for dicts of dataframes
    """
    # lists above this size will be displayed as-is
    MAX_LIST_LEN = 20

    def __init__(self, datadict: dict):
        self.d = datadict

        self.w_cus = Dropdown(options=self.d.keys())
        self.w_cus.observe(self.on_key_change, 'value')
        self.w_out = Output()
        self.selected_val = None

        super().__init__([
            self.w_cus, self.w_out
        ])
        self.on_key_change()

    def on_key_change(self, *_):
        self.w_out.clear_output()
        v = self.d[self.w_cus.value]
        self.selected_val = v

        with self.w_out:
            display(DictViewer(v) if isinstance(v, dict) else v)

    def display_all(self):
        kids = []
        for name, v in self.d.items():
            o = Output()
            with o:
                display(v)
            kids += [Label(name), o]
        return VBox(kids)


class GBViewer(DictViewer):
    """
    Group-by viewer - nice display for pandas GroupBy objects in jupyter notebook.

    Usage example (in jupyter notebook):
        GBViewer(df.groupby('some-col'))
    """
    def __init__(self, groupby: DataFrameGroupBy, dropna=False):
        super().__init__({str(k): self._dropna(v, dropna) for k, v in groupby})

    @staticmethod
    def _dropna(df, shoulddrop=False):
        return df.dropna(how='all', axis=1) if shoulddrop else df


class OutputWrapper(Output):
    """
    Useful for converting dataframes to ipywidgets that can be displayed inside a VBox, etc.

    Usage example (in jupyter notebook):
        HBox([ Label('my dataframe:'), OutputWrapper(df) ])
    """
    def __init__(self, obj_to_display: Any = '', iterate=False):
        super().__init__()
        self.obj = None
        self.reset(obj_to_display, iterate=iterate)

    def reset(self, obj_to_display: Any = '', iterate=False):
        self.clear_output()
        self.obj = obj_to_display
        with self:
            if iterate:
                for o in self.obj:
                    display(o)
            else:
                display(self.obj)


def subplots(*figs) -> plotly.graph_objects.Figure:
    """
    Create a subplot figure from a list of figures with two columns.
    Accepts plotly express and graph_objects figures.
    :return:
    """
    ncols = 2
    nrows = len(figs) // 2 + 1
    fig = make_subplots(rows=nrows, cols=ncols)
    for i, curr_fig in enumerate(figs):
        # plots are indexed starting with 1
        row = i // 2 + 1
        col = i % 2 + 1
        fig.add_trace(curr_fig.data[0], row=row, col=col)

    return fig



def sub_dfs(*dfs):
    """
    Stack pandas dataframes side by side with as many rows as needed based on
    len(dfs)
    :param dfs:
    :return:
    """
    includes_labels = False
    if len(dfs) % 2 == 0:
        for elem in dfs[::2]:
            if not isinstance(elem, str):
                break
        else:  # didn't break
            includes_labels = True

    container = VBox()
    if includes_labels:
        dfs, labels = dfs[1::2], dfs[::2]
        if len(dfs) % 2 == 1:
            dfs += (None,)
            labels += ('',)

        for (df_l, df_r), (label_l, label_r) in zip(grouped(dfs, 2),
                                                    grouped(labels, 2)):
            container.children += (HBox([Label(label_l), OutputWrapper(df_l),
                                         Label(label_r), OutputWrapper(df_r)]),)
    else:
        if len(dfs) % 2 == 1:
            dfs = dfs + (None,)
        for df_l, df_r in grouped(dfs, 2):
            container.children += (HBox([OutputWrapper(df_l), OutputWrapper(df_r)]),)

    return container


def add_diagonal(fig: plotly.graph_objects.Figure, color='black', width=2):
    """
    add diaglonal line (x = y) to a plotly figure
    :param fig:
    :param color: line color
    :param width: line width
    :return:
    """
    max_point = max(fig.data[0]['x'].max(), fig.data[0]['y'].max())
    fig.add_trace(go.Scatter(x=np.arange(max_point), y=np.arange(max_point), mode='lines',
               line=dict(color=color, width=width, dash='dash')))
    return fig


def square_fig(fig: plotly.graph_objects.Figure):
    """
    Make a plotly figure square to have the same scale on both axes
    :param fig:
    :return:
    """
    max_point = max(fig.data[0]['x'].max(), fig.data[0]['y'].max())
    fig.update_xaxes(range=[0, max_point])
    fig.update_yaxes(range=[0, max_point])
    return fig


def col_intersection(colA: pd.Series, colB: pd.Series) -> set:
    """
    Return a series with the intersection of two series.
    :param colA:
    :param colB:
    :return:
    """
    return set(colA).intersection(set(colB))


def df_sneak_peak(df: pd.DataFrame, n_rows: int = 10) -> None:
    """
    Display a sneak peak of a dataframe -
    1. first n (def=10) rows
    2. Shape
    3. Describe
    4. Column dtypes
    :param df:
    :param n_rows: Number of rows from the top to display
    :return:
    """
    h = HBox([VBox([Label('Head:'),
                    OutputWrapper(df.head(n_rows)),
                    Label('Describe:'),
                    OutputWrapper(df.describe())],
                   layout=Layout(overflow='scroll hidden', max_width='65%')),
              VBox([Label('Dtypes:'),
                    OutputWrapper(df.dtypes),
                    Label('Shape:'),
                    OutputWrapper(df.shape)],
                   layout=Layout(overflow='scroll hidden'))])
    h.layout.flex = '1 1 auto'
    display(h)
