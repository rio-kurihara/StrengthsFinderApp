import base64
import datetime
import os

import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from dash import dcc, html
from dash.dependencies import Input, Output, State
from google.cloud import storage

from app import app
from apps.pdf_loader import pdf_to_txt, convert_parsed_txt, check_parsed_txt


# setting
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
tmp_pdf_save_dir = config['tmp_pdf_save_dir']
bucket_name = config['bucket_name']
strengths_path = config['base_dir'] + config['strengths_path']
strengths_bkup_path = config['base_dir'] + config['strengths_bkup_path']
demogra_path = config['base_dir'] + config['demogra_path']
demogra_bkup_path = config['base_dir'] + config['demogra_bkup_path']

client = storage.Client()
bucket = client.get_bucket(bucket_name)


def save_pdf_file(contents, save_path):
    bytes_base64 = contents.encode("utf8").split(b";base64,")[1]  # str->bytes
    decoded_data = base64.decodebytes(bytes_base64)

    with open(save_path, "wb") as fp:
        fp.write(decoded_data)


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
    # save file (temporary)
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    datetime_now = dt_now_jst_aware.strftime('%Y%m%d_%H%M%S_')
    pdf_save_path = os.path.join(tmp_pdf_save_dir, datetime_now+filename)
    save_pdf_file(contents, pdf_save_path)

    # Upload the pdf file to GCS bucket
    upload_pdf_path = 'upload_data/pdf/'+datetime_now+filename
    blob = bucket.blob(upload_pdf_path)
    blob.upload_from_filename(pdf_save_path)

    # pdf2txt
    txt = pdf_to_txt(pdf_save_path)
    list_strengths = convert_parsed_txt(txt)
    parse_status = check_parsed_txt(list_strengths)

    if parse_status:
        # format DataFrame
        df_strengths_input = pd.DataFrame(list_strengths)
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
        df_strengths_org = pd.read_csv(strengths_path)
        df_strengths_org[user_name] = df_strengths_input['strengths']
        df_strengths_org.to_csv(strengths_path, index=False)
        df_strengths_org.to_csv(strengths_bkup_path, index=False)

        # streangth
        df_demogra = pd.read_csv(demogra_path)
        sr_demogra_input = pd.Series([user_name, department], index=["name", "department"])
        df_demogra = df_demogra.append(sr_demogra_input, ignore_index=True)
        df_demogra.to_csv(demogra_path, index=False)
        df_demogra.to_csv(demogra_bkup_path, index=False)

        # アップロードされたPDFファイルの削除
        os.remove(pdf_save_path)

    else:
        output = 'PDFの読み込みに失敗しました。お手数ですが手動入力の程お願い致します。'

    return output
