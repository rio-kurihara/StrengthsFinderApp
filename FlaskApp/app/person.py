from decimal import ROUND_HALF_UP, Decimal

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
from sklearn.decomposition import NMF, PCA

from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header


def _run_pca(rank_matrix, n_components):
    pca = PCA(n_components)
    pca.fit(rank_matrix.T)
    return pca


def _crete_contribution_rate_table(rank_matrix, n_components):
    pca = _run_pca(rank_matrix, n_components)

    # 累積寄与率のテーブル作成
    ruiseki = pd.DataFrame(
        pca.components_.T, index=rank_matrix.index, columns=['x', 'y']).round(2)
    df_x_1 = ruiseki.sort_values(
        'x')[['x']][:5].reset_index().sort_values('x')[::-1]
    df_x_2 = ruiseki.sort_values(
        'x')[['x']][-5:].reset_index().sort_values('x')[::-1]
    df_y_1 = ruiseki.sort_values(
        'y')[['y']][:5].reset_index().sort_values('y')[::-1]
    df_y_2 = ruiseki.sort_values(
        'y')[['y']][-5:].reset_index().sort_values('y')[::-1]

    return df_x_1, df_x_2, df_y_1, df_y_2


def _pca_transform(rank_matrix, pca):
    pca_point = pca.transform(rank_matrix.T)
    pca_df = pd.DataFrame(pca_point, columns=[
                          '1', '2'], index=rank_matrix.T.index)
    return pca_df


def get_plot_pca_2d_data(rank_matrix):
    pca = _run_pca(rank_matrix, n_components=2)
    pca_df = _pca_transform(rank_matrix, pca)
    df_x_1, df_x_2, df_y_1, df_y_2 = _crete_contribution_rate_table(
        rank_matrix, n_components=2)

    x = pca_df['1']
    y = pca_df['2']

    table_trace1 = go.Table(
        header=dict(values=['資質', 'x軸への寄与率'],
                    fill=dict(color='#a1c3d1')
                    ),
        cells=dict(values=np.array(df_x_1.T),
                   fill=dict(color='#EDFAFF')
                   )
    )

    table_trace2 = go.Table(
        header=dict(values=['資質', 'x軸への寄与率'],
                    fill=dict(color='#a1c3d1')
                    ),
        cells=dict(values=np.array(df_x_2.T),
                   fill=dict(color='#EDFAFF')
                   )
    )

    table_trace3 = go.Table(
        header=dict(values=['資質', 'x軸への寄与率'],
                    fill=dict(color='#a1c3d1')
                    ),
        cells=dict(values=np.array(df_y_1.T),
                   fill=dict(color='#EDFAFF')
                   )
    )

    table_trace4 = go.Table(
        header=dict(values=['資質', 'x軸への寄与率'],
                    fill=dict(color='#a1c3d1')
                    ),
        cells=dict(values=np.array(df_y_2.T),
                   fill=dict(color='#EDFAFF')
                   )
    )

    trace = go.Scatter(
        x=x,
        y=y,
        mode='markers+text',
        text=list(pca_df.index),
        textposition='top center'
    )
#     data = [table_trace1, table_trace2, table_trace3, table_trace4, trace]
    data = [trace]

    return data


def get_plot_nmf_3d_scatter(rank_matrix):
    X = rank_matrix.T
    model = NMF(n_components=3, init='random', random_state=0)

    W = model.fit_transform(X)
    H = model.components_

    df_nmf = pd.DataFrame(W)
    df_nmf.index = X.index

    x = df_nmf[0]
    y = df_nmf[1]
    z = df_nmf[2]

    # 各成分の構成資質
    trace0 = go.Scatter3d(x=x,
                          y=y,
                          z=z,
                          mode='markers+text',
                          marker=dict(
                              size=5
                          ),
                          text=list(df_nmf.index),
                          textposition='top center')

    data = [trace0]
    return data


def get_plot_nmf_2d_scatter(rank_matrix):
    X = rank_matrix.T
    model = NMF(n_components=2, init='random', random_state=0)

    W = model.fit_transform(X)
    H = model.components_

    df_nmf = pd.DataFrame(W)
    df_nmf.index = X.index

    x = df_nmf[0]
    y = df_nmf[1]

    # 各成分の構成資質
    trace0 = go.Scatter(x=x,
                        y=y,
                        mode='markers+text',
                        marker=dict(
                             size=5
                        ),
                        text=list(df_nmf.index),
                        textposition='top center')

    data = [trace0]
    return data


def get_plot_nmf_3d_table(rank_matrix):
    X = rank_matrix.T
    model = NMF(n_components=3, init='random', random_state=0)

    W = model.fit_transform(X)
    H = model.components_

    df_nmf = pd.DataFrame(W)
    df_nmf.index = X.index

    x = df_nmf[0]
    y = df_nmf[1]
    z = df_nmf[2]

    df_H = pd.DataFrame(H).T
    df_H.index = rank_matrix.index
    df_H.columns = ['x軸', 'y軸', 'z軸']
    df_H = df_H.sort_values(['x軸', 'y軸', 'z軸'])[::-1]

    # 各成分の構成資質
    trace0 = go.Heatmap(x=df_H.columns,
                        y=df_H.index,
                        z=df_H,
                        colorscale='Viridis')

    data = [trace0]
    return data


def get_plot_nmf_2d_table(rank_matrix):
    X = rank_matrix.T
    model = NMF(n_components=2, init='random', random_state=0)

    W = model.fit_transform(X)
    H = model.components_

    df_nmf = pd.DataFrame(W)
    df_nmf.index = X.index

    x = df_nmf[0]
    y = df_nmf[1]

    df_H = pd.DataFrame(H).T
    df_H.index = rank_matrix.index
    df_H.columns = ['x軸', 'y軸']
    df_H = df_H.sort_values(['x軸', 'y軸'])[::-1]

    # 各成分の構成資質
    trace0 = go.Heatmap(x=df_H.columns,
                        y=df_H.index,
                        z=df_H,
                        colorscale='Viridis')

    data = [trace0]
    return data


# def get_layout(toc_text, df_corr_all34, list_method):
#     person_text = markdown_txt.get_person_content()
#     md_text = dcc.Markdown(toc_text + person_text)

#     person_text2 = markdown_txt.get_person_content2()
#     md_text2 = dcc.Markdown(person_text2)

#     label = df_corr_all34.columns
#     layout = html.Div([
#         md_text,
#         html.Div([
#             html.Div([
#                 dcc.Graph(
#                     id='heatmap',
#                     figure={
#                         'data': [
#                             go.Heatmap(x=label,
#                                        y=label,
#                                        z=df_corr_all34,
#                                        zmin=-1,
#                                        zmid=0,
#                                        zmax=1,
#                                        colorscale='RdBu')
#                         ],
#                         'layout': {
#                             'title': '相関',
#                             'width': 700,
#                             'height': 700
#                         },
#                     })
#             ]),
#             md_text2,
#             html.Div([
#                 dcc.RadioItems(
#                     id='input_id',
#                     options=[{'label': i, 'value': i} for i in list_method],
#                     value='NMF(3d)',
#                     labelStyle={'display': 'inline-block'}
#                 ),
#                 dcc.Graph(id='dim-reduction'),
#                 dcc.Graph(id='dim-reduction-table')
#             ])
#         ])
#     ])
#     return layout

def get_layout(target_person):
    layout = html.Div([
        nav_menu,
        create_content_header('相関',
                              '任意の名前を1名入力すると、登録済みのメンバー全員との相関がみられます'),
        dcc.Dropdown(
            id='input_id',
            options=[{'label': i, 'value': i} for i in target_person],
            # value=list_person,
            multi=False,
        ),
        dcc.Graph(id='my-graph'),
    ],
        style=dict(margin='50px')
    )
    return layout


def _get_colorpalette(colorpalette, n_colors):
    palette = sns.color_palette(
        colorpalette, n_colors)
    rgb = ['rgb({},{},{})'.format(*[x*256 for x in rgb])
           for rgb in palette]
    return rgb


def get_plot_table_data(df_corr_all34, target_person):
    data = []

    df_sorted = df_corr_all34[[target_person]].sort_values(
        by=target_person, ascending=False)
    list_person = df_sorted.index

    n_legends = len(list_person)
    colors = _get_colorpalette('RdYlBu', n_legends)
    heder_color = ['white', 'black']
    cells_color = ['whitesmoke', colors]

    values_tmp = df_sorted[[target_person]].values.flatten()
    # 四捨五入
    values = [Decimal(str(x)).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP) for x in values_tmp]

    trace = go.Table(header=dict(values=[[''], target_person], fill=dict(color=heder_color), font=dict(color='white')),
                     cells=dict(values=[list_person, values], fill=dict(color=cells_color)))
    data.append(trace)

    return data
