import os

import dash_bootstrap_components as dbc
import pandas as pd
import yaml
from app import app
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv

# .envから環境変数を読み込む
load_dotenv()

# settings
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# パスの設定
bucket_name = os.getenv('BUCKET_NAME')
bucket_path = 'gs://{}/'.format(bucket_name)
strengths_path = bucket_path + config['strengths_path']
department_path = bucket_path + config['demogra_path']
mst_category_path = bucket_path + config['mst_category_path']

# load data
df_strengths = pd.read_csv(strengths_path, index_col='rank')
df_department = pd.read_csv(department_path)
df_strengths_category = pd.read_csv(mst_category_path)
list_users = list(df_strengths.columns)
list_departments = config['departments']
list_unique_strengths = list(df_strengths_category['strengths'])

# layout の定義
header_contents = html.Div(
    [
        html.H5('アップロード済みのデータを編集したい方はこちらから',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)

considerations_contents = dbc.Alert(
    [
        html.P("・誤って他の人のデータを編集しないようにお気を付けください。"),
    ],
    color='warning',
    style={'width': '50%'}
)

user_and_department_form = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Label("データを編集したい方の氏名"),
                dcc.Dropdown(id='user-name',
                             options=[{'label': i, 'value': i}
                                      for i in list_users],
                             multi=False),
            ],
            width=3,
        ),
        dbc.Col(
            [
                dbc.Label("変更後の部署名"),
                dcc.Dropdown(id='department-name',
                             placeholder="変更しない場合は入力不要です。",
                             options=[{'label': i, 'value': i}
                                      for i in list_departments],
                             multi=False),
            ],
            width=3,
        ),
    ],
    className="g-3",
)


# 資質情報の変更用フォーム
strengths_input_form = html.Div(
    [
        html.P('変更したいセルをクリックして変更してください。'),
        dash_table.DataTable(
            id='datatable-for-edit',
            editable=True,
            fill_width=False
        )
    ])

# 編集完了ボタン
edit_button = dbc.Button("変更",
                         id='edit-button',
                         color="danger",
                         n_clicks=0
                         )


layout = html.Div(
    [
        header_contents,
        considerations_contents,
        user_and_department_form,
        strengths_input_form,
        html.P(),
        edit_button,
        html.P(),
        html.Div(id='output-test-test')
    ]
)


# ユーザー名が入力されたら、そのユーザー名の既存データを表示する
# そのデータをもとに既存データを編集してもらう
@app.callback(Output('datatable-for-edit', 'data'),
              Output('datatable-for-edit', 'columns'),
              [Input('user-name', 'value')]
              )
def update_display_data(user_name):
    if user_name == None:
        return None, None
    else:
        # 入力されたユーザーのデータを抽出
        df = df_strengths[user_name]
        data = [{'rank': i, 'strengths': strengths_name}
                for i, strengths_name in enumerate(list(df), 1)]
        # 列名の定義
        columns = [{'name': 'rank', 'id': 'rank'},
                   {"name": 'strengths', "id": 'strengths'}]

        return data, columns


def check_strengths(list_strengths):
    # 存在する資質名かチェックして、T/Fを返す
    def _check_exists_strength(list_strengths):
        list_flgs = [strengths_name in list_unique_strengths for strengths_name in list_strengths]
        return all(list_flgs)
    # 資質名が重複していないかチェックして、T/Fを返す

    def _check_duplicate_strengths(list_strengths):
        return len(set(list_strengths)) == len(list_strengths)
    # 上記のチェック関数がすべてTrueの場合のみTrueを返す
    return all([_check_exists_strength(list_strengths),
               _check_duplicate_strengths(list_strengths)
                ])

# 編集ボタンが押されたら、データをチェックしてOKならCSVを更新する


@app.callback(Output('output-test-test', 'children'),
              State('user-name', 'value'),
              State('department-name', 'value'),
              State('datatable-for-edit', 'data'),
              Input('edit-button', 'n_clicks'))
def edit_data(user_name, department, input_strengths, n_clicks):
    if n_clicks >= 1:
        # 入力された資質名をリストとして抽出
        list_input_strengths = [i['strengths'] for i in input_strengths]
        # 入力された資質が正しいかチェックする
        check_result = check_strengths(list_input_strengths)
        # 所属部署名が入力された場合は、データを変更してGCSにアップロードする
        if check_result:
            print('b', df_strengths[user_name])
            df_strengths[user_name] = list_input_strengths
            print('a', df_strengths[user_name])
            # 更新したs資質データを GCS にアップロードする
            # df_strengths.to_csv(strengths_path, index=True)
            display_message = "{} さんの資質データを修正しました。".format(user_name)

            if department != None:
                # 編集対象のユーザーの所属名を変更する
                df_department.loc[df_department['name'] == user_name, ['department']] = department
                # 更新した所属データを GCS にアップロードする
                # df_department.to_csv(department_path, index=False)
                display_message = "{} さんの資質データと所属データを修正しました。".format(user_name)

        else:
            display_message = "資質データの入力に誤りがあります。資質名は正しく入力してください。"

        display_contents = dbc.Alert(
            [
                html.H5(display_message, className="alert-heading"),
            ], color='danger'
        )

        return display_contents
