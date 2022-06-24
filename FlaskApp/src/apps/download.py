import os
from typing import Union

import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from app import app
from dash import html
from dash.dependencies import Input, Output
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from dotenv import load_dotenv

# .envから環境変数を読み込む
load_dotenv()

# settings.yaml の読み込み
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

bucket_name = os.getenv('BUCKET_NAME')
bucket_path = 'gs://{}/'.format(bucket_name)
strengths_path = bucket_path + config['strengths_path']
department_path = bucket_path + config['demogra_path']

# 表示用にサンプルデータを作成（データフレーム）
df_sample_department = pd.DataFrame(
    {
        "name": ["氏名1", "氏名2", "氏名3", "..."],
        "department": ["AN", "DE", "DS", "..."],
    }
)

df_sample_strengths = pd.DataFrame(
    {
        "rank": ["1", "2", "3", "..."],
        "氏名1": ["学習欲", "内省", "コミュニケーション", "..."],
        "氏名2": ["適応性", "アレンジ", "ポジティブ", "..."],
        "氏名3": ["着想", "学習欲", "収集心", "..."],
    }
)

# layout に追加するコンポーネントの作成
sample_department_card = dbc.CardBody(
    [
        dbc.Table.from_dataframe(df_sample_department, bordered=True, hover=True),
        dbc.Button("Download", color="success", className="mt-auto", id="mst_download_btn")
    ],
)

sample_department_layout = [
    dbc.CardHeader("Sample：所属部署マスタ"),
    sample_department_card
]

sample_strengths_card = dbc.CardBody(
    [
        dbc.Table.from_dataframe(df_sample_strengths, bordered=True, hover=True),
        dbc.Button("Download", color="success", className="mt-auto", id="strengths_download_btn")
    ]
)

sample_strengths_layout = [
    dbc.CardHeader("Sample：診断結果"),
    sample_strengths_card
]

layout_samples = dbc.Row(
    [
        dbc.Col(dbc.Card(sample_department_layout, color="dark", outline=True)),
        dbc.Col(dbc.Card(sample_strengths_layout, color="dark", outline=True)),
    ],
    className="mb-4",
)

header_contents = html.Div(
    [
        html.H5('ストレングスファインダーの結果一覧をダウンロード',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)

considerations_contents = dbc.Alert(
    [
        html.H4("注意事項", className="alert-heading"),
        html.P(
            "・本サイトからダウンロードしたデータには個人情報が含まれます。取り扱いには十分注意し、社外への情報共有は絶対に行わないでください"),
        html.P("・本サイトで収集したデータは、社内取り扱いのみに限定します"),
        html.P("・本サイトへのアクセスは社内ネットワークのみから許されています")
    ], color='warning'
)

layout = html.Div(
    [
        header_contents,
        considerations_contents,
        layout_samples,
        Download(id="mst_download"),
        Download(id="strengths_download")
    ]
)


@app.callback(Output("mst_download", "data"),
              [Input('mst_download_btn', 'n_clicks')])
def download_demogra_csv(n_clicks: Union[int, None]) -> Union[dict, None]:
    """ダウンロードボタンがクリックされたら所属リストのファイルをダウンロード"""
    if type(n_clicks) == int:
        df = pd.read_csv(department_path)
        dataframe_content = send_data_frame(df.to_csv, filename="member_demogra.csv", index=False)
        return dataframe_content
    else:
        return None


@app.callback(Output("strengths_download", "data"),
              [Input('strengths_download_btn', 'n_clicks')])
def download_strengths_csv(n_clicks: Union[int, None]) -> Union[dict, None]:
    """ダウンロードボタンがクリックされたら資質順位のファイルをダウンロード"""
    if type(n_clicks) == int:
        df = pd.read_csv(strengths_path)
        dataframe_content = send_data_frame(df.to_csv, filename="member_strengths.csv", index=False)
        return dataframe_content
    else:
        return None
