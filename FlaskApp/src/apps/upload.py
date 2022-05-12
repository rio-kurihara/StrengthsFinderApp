import base64
import datetime
import os

import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from google.cloud import storage

from app import app
from apps.pdf_loader import check_parsed_txt, convert_parsed_txt, pdf_to_txt


# settings.yaml の読み込み
with open('src/settings.yaml') as f:
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


def create_fname_for_save_pdf(filename):
    # PDF を保存するファイル名を生成する: "現在日時＋アップロード時のファイル名.pdf"
    # 現在日時を取得
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    datetime_now = dt_now_jst_aware.strftime('%Y%m%d_%H%M%S_')

    # PDF を保存するパスを生成
    pdf_save_fname = datetime_now + filename

    return pdf_save_fname


def save_pdf_to_local(contents: str, save_path: str) -> None:
    """ PDF ファイルをローカルに保存する

    Args:
        contents (str): ユーザーから送られてきたファイル（バイナリ）
        save_path (str): 保存先のパス
    """
    # 保存先のディレクトリを作成
    os.makedirs(tmp_pdf_save_dir, exist_ok=True)
    # str -> bytes
    bytes_base64 = contents.encode("utf8").split(b";base64,")[1]
    # Base64をデコード
    decoded_data = base64.decodebytes(bytes_base64)

    with open(save_path, "wb") as fp:
        fp.write(decoded_data)


def save_pdf_to_gcs(pdf_local_path, upload_gcs_path):
    # ローカルに一時保存したPDFファイルを GCS にアップロードする
    # blob = bucket.blob(upload_gcs_path)
    # blob.upload_from_filename(pdf_local_path)
    print('PDF file upload done')


def format_to_dataframe(list_strengths: list) -> pd.DataFrame:
    """
    PDF をパースしたリストをデータフレーム化する

    Args:
        list_strengths (list): 資質名のリスト（5個 or 34個 の要素）
    Return:
        pd.DataFrame:
    """
    df = pd.DataFrame(list_strengths)
    df.index = df.index + 1  # 1始まりにするため
    df = df.reset_index()
    df.columns = ['rank', 'strengths']

    return df


def append_row_to_csv_strengths(user_name, df_strengths_new):
    # 既存の csv ファイルを GCS から読み込み、新しいデータを追加する
    df_strengths_org = pd.read_csv(strengths_path)
    df_strengths_org[user_name] = df_strengths_new['strengths']
    # 新しいデータを追加した csv ファイルを GCS にアップロードする
    df_strengths_org.to_csv(strengths_path, index=False)
    df_strengths_org.to_csv(strengths_bkup_path, index=False)


def append_row_to_csv_demogra(user_name, department):
    # 既存の csv ファイルを GCS から読み込み、新しいデータを追加する
    df_demogra = pd.read_csv(demogra_path)
    sr_demogra_input = pd.Series([user_name, department], index=["name", "department"])
    df_demogra = df_demogra.append(sr_demogra_input, ignore_index=True)
    # GCS にアップロードする
    df_demogra.to_csv(demogra_path, index=False)
    df_demogra.to_csv(demogra_bkup_path, index=False)


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
            id='datatable-upload',
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

upload_form = dbc.Form(
    [
        user_name_input_form,
        department_input_form,
        upload_pdf_form
    ],
    inline=False,
)

data_table = dash_table.DataTable(
    id='datatable-upload-container',
    editable=True,
    fill_width=False
)

upload_button = dbc.Button("アップロード",
                           id='upload-button',
                           color="success",
                           n_clicks=0,
                           href="/data/upload_done",
                           external_link=True
                           )
layout = html.Div(
    [
        header_contents,
        upload_form,
        html.Br(),
        data_table,
        html.Br(),
        upload_button
    ]
)

# PDFファイルがユーザーからアプリにアップロードされる（この時点で中身はbinary）


@ app.callback(Output('datatable-upload-container', 'data'),
               Output('datatable-upload-container', 'columns'),
               Input('datatable-upload', 'contents'),
               State('datatable-upload', 'filename'))
def update_output(contents, filename):
    if contents is None:
        return [{}], []

    # 保存するファイル名を生成（"現在日時＋アップロード時のファイル名.pdf"）
    save_fname = create_fname_for_save_pdf(filename)
    # post された バイナリデータを文字列に変換し、一時的にローカルに保存
    local_save_path = os.path.join(tmp_pdf_save_dir, save_fname)
    save_pdf_to_local(contents, local_save_path)
    # ローカルに一時保存したPDFファイルを GCS にアップロードする
    upload_gcs_path = 'pdf/' + save_fname
    save_pdf_to_gcs(local_save_path, upload_gcs_path)
    # PDF をパースしてテキストにする
    txt = pdf_to_txt(local_save_path)
    list_strengths = convert_parsed_txt(txt)
    parse_status = check_parsed_txt(list_strengths)

    # ローカルに一時保存していた PDF ファイルの削除
    os.remove(local_save_path)

    if parse_status:
        # パースした結果をデータフレーム化する
        df_strengths = format_to_dataframe(list_strengths)
        output = df_strengths.to_dict('records'), \
            [{"name": i, "id": i} for i in df_strengths.columns]
    else:
        output = 'PDFの読み込みに失敗しました。お手数ですが手動入力の程お願い致します。'

    return output


@app.callback(Output('output-state', 'children'),
              State('datatable-upload-container', 'data'),
              State('user-name', 'value'),
              State('department', 'value'),
              Input('upload-button', 'n_clicks'))
def display_output(rows, user_name, department, _):
    pruned_rows = []
    for row in rows:
        # require that all elements in a row are specified
        # the pruning behavior that you need may be different than this
        if all([cell != '' for cell in row.values()]):
            pruned_rows.append(row)

    df_strengths_new = pd.DataFrame.from_dict(pruned_rows)

    # GCS に新しいデータをアップロード
    append_row_to_csv_strengths(user_name, df_strengths_new)
    append_row_to_csv_demogra(user_name, department)
