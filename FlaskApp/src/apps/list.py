import os

import numpy as np
import pandas as pd
import yaml
from app import app
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from dotenv import load_dotenv

# from src.app import app  # pytest のときのみこっち

# .envから環境変数を読み込む
load_dotenv()

# settings.yaml の読み込み
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# パスを設定
bucket_name = os.getenv('BUCKET_NAME')
bucket_path = 'gs://{}/'.format(bucket_name)
strengths_path = bucket_path + config['strengths_path']
colors_strengths_path = bucket_path + config['colors_strengths_path']
strengths_desc_path = bucket_path + config['strengths_desc_path']

# GCS のバケットからファイルを読み込む
df_all = pd.read_csv(strengths_path, index_col='rank')
df_all = df_all.fillna('nan')
unique_users = np.unique(df_all.columns)

# 資質別の説明文と色情報の json を読み込む
tmp_df_colors_strengths = pd.read_json(colors_strengths_path, orient='index')
dict_colors_strengths = tmp_df_colors_strengths[0].to_dict()
tmp_df_strengths_desc = pd.read_json(strengths_desc_path, orient='index')
dict_strengths_desc = tmp_df_strengths_desc[0].to_dict()

# レイアウトに追加するコンポーネントの作成
header_contents = html.Div(
    [
        html.H5('受診済みの方の資質ランキング表示',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('参照したい方の氏名を入力してください（複数可）')
    ]
)

# 入力用ドロップダウンの定義
users_drop_down_list = dcc.Dropdown(
    id='input_id',
    options=[{'label': i, 'value': i} for i in unique_users],
    multi=True,
)

# データテーブルの定義
data_table = dash_table.DataTable(
    id='strengths-list',
    fill_width=False,
    tooltip_delay=0,
    tooltip_duration=None,
    style_data={
        'if': {'column_id': 'rank'},
        'backgroundColor': 'white',
        'color': 'black',
        'textAlign': 'right'
    },
    style_header={
        'height': 'auto',
        'backgroundColor': 'white',
        'color': 'black',
        'fontWeight': 'bold',
        'textAlign': 'left'
    },
    style_cell_conditional=[{
        'height': 'auto',
        'color': 'white',
        'fontWeight': 'bold',
        'textAlign': 'left'
    }]
)

# layout の定義
layout = html.Div(
    [
        header_contents,
        users_drop_down_list,
        html.P(),
        data_table
    ]
)


@app.callback(
    Output('strengths-list', 'data'),
    Output('strengths-list', 'columns'),
    Output('strengths-list', 'tooltip_data'),
    Output('strengths-list', 'style_data_conditional'),
    Input('input_id', 'value')
)
def update_graph(list_person):
    if list_person == None:
        return [], [], [], []
    else:
        df = df_all[list_person]

        tooltip_data = []

        for dict_row in df.to_dict('records'):
            tmp_dict = {}
            for user_name in list_person:
                strength = dict_row[user_name]
                text = dict_strengths_desc[strength]
                text = text.replace('<br>', '')  # TODO <BR>
                tmp_dict[user_name] = {'value': text}
            tooltip_data.append(tmp_dict)

        style_data_conditional = []
        for index, dict_row in enumerate(df.to_dict('records')):
            for user_name in list_person:
                tmp_dict = {}
                strengths = dict_row[user_name]
                bkg_color = dict_colors_strengths[strengths]

                tmp_dict['if'] = {'row_index': index, 'column_id': user_name}
                tmp_dict['background-color'] = bkg_color
                tmp_dict['whiteSpace'] = 'normal'
                style_data_conditional.append(tmp_dict)

        df = df.reset_index()
        data = df.to_dict('records')
        columns = [{'id': c, 'name': c} for c in ['rank']+list_person]

        return data, columns, tooltip_data, style_data_conditional
