import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import yaml
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

from app import app


# settings
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
strengths_path = config['base_dir'] + config['strengths_path']
demogra_path = config['base_dir'] + config['demogra_path']

# サンプルデータの作成（データフレーム）
df_sample_mst = pd.DataFrame(
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
sample_mst_card = dbc.CardBody(
    [
        dbc.Table.from_dataframe(df_sample_mst, bordered=True, hover=True),
        dbc.Button("Download", color="success", className="mt-auto", id="mst_download_btn")
    ],
)

sample_mst_layout = [
    dbc.CardHeader("Sample：所属部署マスタ"),
    sample_mst_card
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
        dbc.Col(dbc.Card(sample_mst_layout, color="dark", outline=True)),
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
        html.P("・本サイトへのアクセスはBrainPadネットワークのみから許されています")
    ], color='warning'
)

layout = html.Div(
    [header_contents,
     considerations_contents,
     layout_samples,
     Download(id="mst_download"),
     Download(id="strengths_download")
     ]
)


@app.callback(Output("mst_download", "data"),
              [Input('mst_download_btn', 'n_clicks')])
def get_master(n_clicks):
    if not n_clicks == None:
        df = pd.read_csv(demogra_path)
        return send_data_frame(df.to_csv, filename="member_demogra.csv")
    else:
        return None


@app.callback(Output("strengths_download", "data"),
              [Input('strengths_download_btn', 'n_clicks')])
def get_strengths(n_clicks):
    if not n_clicks == None:
        df = pd.read_csv(strengths_path)
        return send_data_frame(df.to_csv, filename="member_strengths.csv")
    else:
        return None
