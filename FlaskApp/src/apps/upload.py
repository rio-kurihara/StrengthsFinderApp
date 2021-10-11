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
from apps.pdf_loader import check_parsed_txt, convert_parsed_txt, pdf_to_txt


# settings.yaml の読み込み
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)


# パスを設定
tmp_pdf_save_dir = config['tmp_pdf_save_dir']
base_dir = config['base_dir']
strengths_path = base_dir + config['strengths_path']
strengths_bkup_path = base_dir + config['strengths_bkup_path']
demogra_path = base_dir + config['demogra_path']
demogra_bkup_path = base_dir + config['demogra_bkup_path']

# GCS の設定
bucket_name = config['bucket_name']
client = storage.Client()
bucket = client.get_bucket(bucket_name)


def save_pdf_file(contents: str, save_path: str) -> None:
    """ PDF ファイルをローカルに保存する

    Args:
        contents (str): ユーザーから送られてきたファイル
        save_path (str): 保存先のパス
    """
    # str -> bytes
    bytes_base64 = contents.encode("utf8").split(b";base64,")[1]
    # Base64をデコード
    decoded_data = base64.decodebytes(bytes_base64)

    with open(save_path, "wb") as fp:
        fp.write(decoded_data)


# layout に追加するコンポーネントの作成
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
    # 現在日時を取得
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    datetime_now = dt_now_jst_aware.strftime('%Y%m%d_%H%M%S_')
    # 一時保存先のディレクトリを作成
    os.makedirs(tmp_pdf_save_dir, exist_ok=True)
    # PDF ファイルを保存
    pdf_save_path = os.path.join(tmp_pdf_save_dir, datetime_now+filename)
    save_pdf_file(contents, pdf_save_path)

    # 一時保存したファイルを GCS にアップロードする
    upload_pdf_fname = datetime_now + filename
    upload_pdf_path = base_dir + 'pdf/' + upload_pdf_fname
    blob = bucket.blob(upload_pdf_path)
    blob.upload_from_filename(pdf_save_path)

    # PDF をパースしてテキストにする
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

        # streangth
        # 既存の csv ファイルを GCS から読み込み、新しいデータを追加する
        df_strengths_org = pd.read_csv(strengths_path)
        df_strengths_org[user_name] = df_strengths_input['strengths']
        # GCS にアップロードする
        df_strengths_org.to_csv(strengths_path, index=False)
        df_strengths_org.to_csv(strengths_bkup_path, index=False)

        # demogra
        # 既存の csv ファイルを GCS から読み込み、新しいデータを追加する
        df_demogra = pd.read_csv(demogra_path)
        sr_demogra_input = pd.Series([user_name, department], index=["name", "department"])
        df_demogra = df_demogra.append(sr_demogra_input, ignore_index=True)
        # GCS にアップロードする
        df_demogra.to_csv(demogra_path, index=False)
        df_demogra.to_csv(demogra_bkup_path, index=False)

        # 一時保存していた PDF ファイルの削除
        os.remove(pdf_save_path)

    else:
        output = 'PDFの読み込みに失敗しました。お手数ですが手動入力の程お願い致します。'

    return output
