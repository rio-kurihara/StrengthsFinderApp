import datetime
import json
import os

import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from app import app
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv
from google.cloud import storage

from apps.pdf_loader import (check_parsed_txt, convert_parsed_txt,
                             create_fname_for_save_pdf,
                             is_correct_input_strengths, is_not_input_empty,
                             is_pdf, pdf_to_txt, save_pdf_to_gcs,
                             save_pdf_to_local)

# .envから環境変数を読み込む
load_dotenv()

# settings.yaml の読み込み
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# パスを設定
bucket_name = os.getenv('BUCKET_NAME')
bucket_path = 'gs://{}/'.format(bucket_name)
tmp_pdf_save_dir = config['tmp_pdf_save_dir']
strengths_path = bucket_path + config['strengths_path']
demogra_path = bucket_path + config['demogra_path']
# バックアップ用の csv は "ファイル名_bkup_日付.csv"
today = str(datetime.date.today())
strengths_bkup_path = strengths_path.replace('strengths.csv',
                                             'strengths_bkup_{}.csv'.format(today))
demogra_bkup_path = demogra_path.replace('demogra.csv',
                                         'demogra_bkup_{}.csv'.format(today))
# 所属部署のリスト
list_departments = config['departments']

# GCS の設定
client = storage.Client()
bucket = client.get_bucket(bucket_name)


def append_row_to_csv_strengths(user_name: str, df: pd.DataFrame) -> None:
    # 既存の csv ファイルを GCS から読み込み、新しいデータを追加する
    df_org = pd.read_csv(strengths_path)
    df_org[user_name] = df['strengths']
    # 新しいデータを追加した csv ファイルを GCS にアップロードする
    df_org.to_csv(strengths_path, index=False)
    df_org.to_csv(strengths_bkup_path, index=False)

    print('original csv file update done')


def append_row_to_csv_demogra(user_name: str, department: str) -> None:
    # 既存の csv ファイルを GCS から読み込み、新しいデータを追加する
    df_org = pd.read_csv(demogra_path)
    sr_input = pd.Series([user_name, department], index=["name", "department"])
    df_org = df_org.append(sr_input, ignore_index=True)
    # GCS にアップロードする
    df_org.to_csv(demogra_path, index=False)
    df_org.to_csv(demogra_bkup_path, index=False)


# layout に追加するコンポーネントの作成
header_contents = html.Div(
    [
        html.H5('ストレングスファインダーの結果をアップロード',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.Br()
    ]
)

user_and_department_form = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Label("氏名"),
                dbc.Input(
                    type="text",
                    id="user-name"
                ),
            ],
            width=3,
        ),
        dbc.Col(
            [
                dbc.Label("所属"),
                dcc.Dropdown(
                    id="department",
                    options=[
                        {'label': i, 'value': i} for i in list_departments
                    ],
                ),
            ],
            width=3,
        ),
    ],
    className="g-3",
)

upload_pdf_form = html.Div(
    [
        html.P('ストレングスファインダーのHPからダウンロードしたPDFをアップロードしてください'),
        html.P('※日本語データのみ対応'),
        dcc.Upload(
            id='pdf-upload',
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
        user_and_department_form,
        html.P(),
        upload_pdf_form
    ]
    # ,inline=False,
)

data_table = dash_table.DataTable(
    id='datatable-upload-container',
    editable=True,
    fill_width=False
)

upload_button = dbc.Button("送信",
                           id='upload-button',
                           color="success",
                           n_clicks=0,
                           href="/data/upload_result",
                           external_link=True,
                           loading_state={'component_name': '',
                                          'is_loading': '',
                                          'prop_name': ''}
                           )
layout = html.Div(
    [
        header_contents,
        upload_form,
        html.Br(),
        html.Div(id='pdf-upload-state'),
        data_table,
        html.Br(),
        upload_button,
        html.Div(id='output-state')
    ]
)


@app.callback(Output('datatable-upload-container', 'data'),
              Output('datatable-upload-container', 'columns'),
              Output('pdf-upload-state', 'children'),
              Input('pdf-upload', 'contents'),
              State('pdf-upload', 'filename'))
# ユーザーからファイルがアップロードされると以下の処理が走る（この時点で中身はbinary）
def update_output(contents, filename):
    if contents is None:
        return [{}], [], ''
    # PDF ファイル以外がアップロードされた場合はエラーメッセージを表示する
    if not is_pdf(filename):
        m = dbc.Alert("PDF ファイルをアップロードしてください。",
                      color="danger",
                      style={'width': '50%'})
        return [{}], [], m
    else:
        """ 処理の流れ
        1. アップロードされた PDF ファイルを一時的にローカルに保存する
        2. ローカルに保存した PDF ファイルを GCS にアップロードする
        3. ローカルに保存した PDF ファイルを読み込み、定義済みの形にパースする
        4. ローカルに保存した PDF ファイルを削除する
        5. 3.でパースしたデータを dash_table.DataTable に渡せる形に整形し、return する
        """
        # 1.アップロードされた PDF ファイルを一時的にローカルに保存する
        #  保存するファイル名を生成（"現在日時＋アップロード時のファイル名.pdf"）
        save_fname = create_fname_for_save_pdf(filename)
        local_save_path = os.path.join(tmp_pdf_save_dir, save_fname)
        #  保存先のディレクトリを作成
        os.makedirs(tmp_pdf_save_dir, exist_ok=True)
        #  ローカルに保存
        save_pdf_to_local(contents, local_save_path)

        # 2.ローカルに保存した PDF ファイルを GCS にアップロードする
        upload_gcs_path = 'pdf/' + save_fname
        save_pdf_to_gcs(bucket, local_save_path, upload_gcs_path)

        # 3.ローカルに保存した PDF ファイルを読み込み、定義済みの形にパースする
        txt = pdf_to_txt(local_save_path)
        list_strengths = convert_parsed_txt(txt)
        parse_status = check_parsed_txt(list_strengths)
        print('PDF file parse done')

        # 4.ローカルに保存した PDF ファイルを削除
        os.remove(local_save_path)
        print('deleted PDF file at local')

        # 5.3.でパースしたデータを dash_table.DataTable に渡せる形に整形し、return する
        #  データテーブル用に列名を定義する
        columns = [{'name': 'rank', 'id': 'rank'},
                   {"name": 'strengths', "id": 'strengths'}]

        if parse_status:
            m = dbc.Alert("以下の内容が正しければページ下部の「送信」ボタンを押してください。", color="success"),
            # パースした結果をデータテーブルに渡すために dict にする
            data = [{'rank': i, 'strengths': strengths_name}
                    for i, strengths_name in enumerate(list_strengths, 1)]
            return data, columns, m
        else:
            # 読み込みに失敗した場合は、ユーザーに手入力してもらう
            m = dbc.Alert('PDFの読み込みに失敗しました。お手数ですが以下のフォームから手動入力をお願い致します。',
                          color="danger",
                          style={'width': '50%'})
            # 手入力用に空のデータテーブルを作成
            empty_data = [{'rank': i, 'strengths': ''} for i in range(1, 35)]
            return empty_data, columns, m


@app.callback(Output('output-state', 'children'),
              State('datatable-upload-container', 'data'),
              State('user-name', 'value'),
              State('department', 'value'),
              Input('upload-button', 'n_clicks'))
def update_gcs_csv(rows, user_name, department, n_clicks):
    """ 処理の流れ
    1. 入力データのチェック結果を json として保存する (input_check_state)
    2. 入力データのチェックが全て True だった場合のみ、
       入力された資質データをデータフレーム化して GCS にアップロードする
    ※ 入力データのチェック結果が False だった場合については、upload_result.py にて出力画面を制御している
       （ユーザーがアップロードボタンを押した後、"/data/upload_result" に飛ぶ仕様）
    """

    if n_clicks >= 1:
        # 1. 入力データのチェック結果を json として保存する
        #  ∵入力データのチェック結果によって、「アップロード結果」ページの表示内容を条件分岐させたい（True なら「成功」、False なら「失敗」と表示したい）
        #  TODO: dash は stateless らしいのでこの書き方にしているが、より良い方法あるか検討する
        input_check_state = {'user_name': is_not_input_empty(user_name),
                             'department': is_not_input_empty(department),
                             'strengths': is_correct_input_strengths(rows)
                             }
        json_save_path = os.path.join(tmp_pdf_save_dir, 'input_check_state.json')
        with open(json_save_path, 'w') as f:
            json.dump(input_check_state, f, indent=4)

        # 2. 入力データのチェックが全て True だった場合のみ、
        #    入力された資質データをデータフレーム化して GCS にアップロードする
        if all(input_check_state.values()):
            # 資質のテーブルデータを読み込む
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
