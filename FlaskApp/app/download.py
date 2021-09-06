import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions import Download
from markdown_txt import txt as markdown_txt
from app.utils import nav_menu, create_content_header
import pandas as pd


def get_layout():
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

    sample_mst = [
        dbc.CardHeader("Sample：所属部署マスタ"),
        dbc.CardBody(
            [
                dbc.Table.from_dataframe(
                    df_sample_mst, bordered=True, hover=True),
                dbc.Button(
                    "Download", color="success", className="mt-auto", id="mst_download_btn")
            ],
        )
    ]

    sample_strengths = [
        dbc.CardHeader("Sample：診断結果"),
        dbc.CardBody(
            [
                dbc.Table.from_dataframe(
                    df_sample_strengths, bordered=True, hover=True),
                dbc.Button(
                    "Download", color="success", className="mt-auto", id="strengths_download_btn")
            ]
        )
    ]
    row_1 = dbc.Row(
        [
            dbc.Col(dbc.Card(sample_mst, color="dark", outline=True)),
            dbc.Col(dbc.Card(sample_strengths, color="dark", outline=True)),
        ],
        className="mb-4",
    )
    layout = html.Div([nav_menu,
                       create_content_header('ストレングスファインダーの結果一覧をダウンロード', ''),
                       dbc.Alert([
                           html.H4("注意事項", className="alert-heading"),
                           html.P(
                               "・本サイトからダウンロードしたデータには個人情報が含まれます。取り扱いには十分注意し、社外への情報共有は絶対に行わないでください"),
                           html.P("・本サイトで収集したデータは、社内取り扱いのみに限定します"),
                           html.P("・本サイトへのアクセスはBrainPadネットワークのみから許されています")
                       ], color='warning'),
                       row_1,
                       Download(id="mst_download"),
                       Download(id="strengths_download")
                       ],
                      style=dict(margin="50px")
                      )
    return layout
