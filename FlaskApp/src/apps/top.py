import pickle

from dash import dcc, html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import yaml
from dash.dependencies import Input, Output

from app import app

# load setting file
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# load data
df_all = pd.read_csv(config['data_path']['all34_exsits_null'], index_col='index')
df_all = df_all.fillna('nan')

with open(config['data_path']['dict_colors_strengths'], mode='rb') as f:
    dict_colors_strengths = pickle.load(f)
with open(config['data_path']['dict_strengths_desc'], mode='rb') as f:
    dict_strengths_desc = pickle.load(f)


header_contents = html.Div(
    [
        html.H5('受診済みの方の資質ランキング表示',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('参照したい方の氏名を入力してください（複数可）')
    ]
)

unique_users = np.unique(df_all.index)

top_drop_down_menu = dcc.Dropdown(
    id='input_id',
    options=[{'label': i, 'value': i} for i in unique_users],
    multi=True,
)

layout = html.Div(
    [
        header_contents,
        top_drop_down_menu,
        dcc.Graph(id='strengths-list'),
    ]
)


def create_strengths_rank_list(df, dict_colors_strengths, dict_strengths_desc, list_person):
    """ユーザーの資質一覧を表示するためのグラフオブジェクトを作成

    Args:
        df (pd.DataFrame): 全ユーザーの資質ランキング
        dict_colors_strengths (dict): 各資質のカラーコード
                                    ex: {'責任感': '#ffbcdd', '達成欲': '#ffbcdd', ...}
        dict_strengths_desc (dict): 各資質の説明
                                    ex: {'収集心': '収集や蓄積を必要とします',
                                        '分析思考': '物事の理由と原因を追究します',
                                        ...}
        list_person (list): 任意のユーザー名のリスト

    Returns:
        list: グラフオブジェクトのリスト
    """

    data = []
    num_strengths = 35

    for i_th in range(1, num_strengths):

        i_th_strenghts = list(df[df['rank'] == i_th].loc[list_person]['strengths'])
        colors_for_strenghts = [dict_colors_strengths[_x] for _x in i_th_strenghts]

        marker = dict(
            color=colors_for_strenghts,
            line=dict(color='rgb(8,48,107)', width=1.5)
        )

        description_for_strengths = [dict_strengths_desc[_x] for _x in i_th_strenghts]
        i_th_strenghts_for_display = [_x.replace(_x, 'コミュニ<br>ケ―ション')
                                      if _x == 'コミュニケーション' else _x for _x in i_th_strenghts]

        trace = go.Bar(
            x=list_person,
            y=[1] * len(list_person),
            marker=marker,
            hoverinfo='text',
            hovertext=description_for_strengths,
            text=i_th_strenghts_for_display,
            textposition='inside'
        )

        data.append(trace)

    return data


@app.callback(Output('strengths-list', 'figure'), [Input('input_id', 'value')])
def update_graph(list_person):
    data = create_strengths_rank_list(
        df_all, dict_colors_strengths, dict_strengths_desc, list_person)

    layout = go.Layout(
        font=dict(size=16),
        hovermode='closest',
        height=1800,
        width=1000,
        barmode='stack',
        showlegend=False,
        xaxis=dict(side='top', tickangle=90),
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
