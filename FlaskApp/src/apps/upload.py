import base64
import datetime
import os

import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from dash import dcc, html
from dash.dependencies import Input, Output, State

from app import app
from apps import pdf_loader


def save_file(contents, save_path):
    bytes_base64 = contents.encode("utf8").split(b";base64,")[1]  # str->bytes
    decoded_data = base64.decodebytes(bytes_base64)

    with open(save_path, "wb") as fp:
        fp.write(decoded_data)


# load setting file
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# layout の設定
header_contents = html.Div(
    [
        html.H5('ストレングスファインダーの結果をアップロード',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.Br()
    ]
)

user_name_input_form = dbc.FormGroup(
    [
        dbc.Label("氏名", className="mr-2"),
        dcc.Input(id='user-name', type='text', value=' '),
    ],
    className="mr-3",
)

department_input_form = dbc.FormGroup(
    [
        dbc.Label("所属", className="mr-2"),
        dcc.Input(id='department', type='text', value=' '),
    ],
    className="mr-3",
)

upload_pdf_form = dbc.FormGroup(
    [
        html.P('ストレングスファインダーのHPからダウンロードしたPDFをアップロードしてください'),
        dcc.Upload(
            id='upload-pdf',
            children=html.Div(
                [
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]
            ),
            style={
                'width': '50%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center'
            },
            multiple=False
        ),
    ],
    className="mr-3",
)

check_button = dbc.Button("確認へ", id='check-button', color="primary", n_clicks=0)

upload_form = dbc.Form(
    [
        user_name_input_form,
        department_input_form,
        upload_pdf_form,
        check_button
    ],
    inline=False,
)

layout = html.Div(
    [
        header_contents,
        upload_form,
        html.Br(),
        html.Div(id='output-state')
    ]
)


@app.callback(Output('output-state', 'children'),
              Input('check-button', 'n_clicks'),
              State('user-name', 'value'),
              State('department', 'value'),
              State('upload-pdf', 'contents'),
              State('upload-pdf', 'filename')
              )
def update_output(_, user_name, department, contents, filename):
    # save file
    save_dir = config['data_path']['upload_dir']
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    datetime_now = dt_now_jst_aware.strftime('%Y%m%d_%H%M%S_')

    save_path = os.path.join(save_dir, datetime_now+filename)
    save_file(contents, save_path)

    # pdf2txt
    txt = pdf_loader.pdf_to_txt(save_path)
    dict_result = pdf_loader.txt_to_dict_format(txt)

    if dict_result['status'] == True:
        # format DataFrame
        df_strengths_input = pd.DataFrame(dict_result['result'])
        df_strengths_input.index = df_strengths_input.index + 1  # 1始まりにするため
        df_strengths_input = df_strengths_input.reset_index()
        df_strengths_input.columns = ['rank', 'strengths']

        # 確認画面の設定
        upload_button = dbc.Button("アップロード",
                                   id='upload-button',
                                   color="success",
                                   n_clicks=0,
                                   href="/data/upload_done",
                                   external_link=True
                                   )

        output = html.Div(
            [
                dbc.Table.from_dataframe(df_strengths_input),
                upload_button
            ]
        )

        # csv ファイルをアップデートする
        # streangth
        df_strengths_org = pd.read_csv(config['data_path']['strengths_csv'])
        df_strengths_org[user_name] = df_strengths_input['strengths']
        df_strengths_org.to_csv(config['data_path']['strengths_csv'], index=False)

        # streangth
        df_demogra = pd.read_csv(config['data_path']['demogra_csv'])
        sr_demogra_input = pd.Series([user_name, department], index=["name", "department"])
        df_demogra = df_demogra.append(sr_demogra_input, ignore_index=True)
        df_demogra.to_csv(config['data_path']['demogra_csv'], index=False)

        # アップロードされたファイルの削除
        os.remove(save_path)

    else:
        output = dict_result['error_message']

    return output
