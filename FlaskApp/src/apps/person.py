import pickle
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
import yaml
from dash import dcc, html
from dash.dependencies import Input, Output

from app import app


def _get_colorpalette(colorpalette, n_colors):
    palette = sns.color_palette(
        colorpalette, n_colors)
    rgb = ['rgb({},{},{})'.format(*[x*256 for x in rgb])
           for rgb in palette]
    return rgb


def create_correlation_table(df_corr_all34, target_user):
    """１人のユーザーに対する全ユーザーの相関係数を表示するためのグラフオブジェクトを作成

    Args:
        df_corr_all34 (pd.DataFrame): 全ユーザーの相関行列
        target_user (str): ユーザー名

    Returns:
        list: グラフオブジェクトのリスト
    """

    data = []

    df_sorted = df_corr_all34[[target_user]].sort_values(
        by=target_user, ascending=False)
    list_users = df_sorted.index

    n_legends = len(list_users)
    colors = _get_colorpalette('RdYlBu', n_legends)
    heder_color = ['white', 'black']
    cells_color = ['whitesmoke', colors]

    values_tmp = df_sorted[[target_user]].values.flatten()
    # 四捨五入
    values = [Decimal(str(x)).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP) for x in values_tmp]

    trace = go.Table(header=dict(values=[[''], target_user], fill=dict(color=heder_color), font=dict(color='white')),
                     cells=dict(values=[list_users, values], fill=dict(color=cells_color)))

    data.append(trace)

    return data


# load setting file
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# load data
df_corr_all34 = pd.read_csv(
    config['data_path']['all34_corr'], index_col='index')

unique_users = np.unique(df_corr_all34.index)


header_contents = html.Div(
    [
        html.H5('相関',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('任意の名前を1名入力すると、登録済みのメンバー全員との相関がみられます')
    ]
)

users_drop_down_list = dcc.Dropdown(
    id='user-name',
    options=[{'label': i, 'value': i} for i in unique_users],
    multi=False
)

layout = html.Div(
    [
        header_contents,
        users_drop_down_list,
        dcc.Graph(id='correlation-table'),
    ]
)


@app.callback(Output('correlation-table', 'figure'), [Input('user-name', 'value')])
def update_graph(target_user):

    data = create_correlation_table(df_corr_all34, target_user)

    layout = go.Layout(
        font=dict(size=16),
        hovermode='closest',
        height=2000,
        width=1000,
        barmode='stack',
        showlegend=False,
        xaxis=dict(title="Strengths",
                   side='top',
                   tickangle=90),
        yaxis=dict(
            autorange='reversed',
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            dtick=1,
        )
    )

    return {'data': data, 'layout': layout}
