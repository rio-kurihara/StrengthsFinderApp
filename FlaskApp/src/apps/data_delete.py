from audioop import mul
import yaml
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from app import app

# settings
with open('src/settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
strengths_path = config['base_dir'] + config['strengths_path']
department_path = config['base_dir'] + config['demogra_path']

# load data
df_strengths = pd.read_csv(strengths_path, index_col='rank')
df_department = pd.read_csv(department_path)
list_users = list(df_strengths.columns)

# layout の定義
header_contents = html.Div(
    [
        html.H5('アップロード済みのデータを削除したい方はこちらから',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('')
    ]
)

considerations_contents = dbc.Alert(
    [
        html.P("・誤って他の人のデータを削除しないように気を付けてください。"),
        html.P("・削除を取り消したい場合は、再度データをアップロードしていただくか、管理者までご連絡ください。"),
    ], color='warning'
)

# 削除ボタンが押されたときの確認用ポップアップ
confirm_dialog = dcc.ConfirmDialog(
    id='confirm-danger',
    message='本当に削除してよろしいですか？'
)

user_name_input_form = dbc.FormGroup(
    [
        dbc.Label("削除したい方の氏名", className="mr-2"),
        dcc.Dropdown(id='user-name',
                     options=[{'label': i, 'value': i}
                              for i in list_users],
                     multi=False),
    ],
    className="mr-3",
)

delete_button = dbc.Button("削除",
                           id='delete-button',
                           color="danger",
                           outline=True,
                           n_clicks=0,
                           #    external_link=True,
                           #    href="/data/delete_done"
                           )

layout = html.Div(
    [
        header_contents,
        considerations_contents,
        confirm_dialog,
        user_name_input_form,
        delete_button,
        html.P(),
        html.Div(id='output')
    ]
)
# 削除ボタンが押されたら、確認用ポップアップを表示する
# 氏名が入力されていなかった場合もポップアップで入力を促す


@ app.callback(Output('confirm-danger', 'displayed'),
               Input('delete-button', 'n_clicks'),
               State('user-name', 'value'))
def display_confirm(n_clicks, user_name):
    if n_clicks > 0 and user_name != None:
        return True
    return False

# 確認用ポップアップで OK が押されたら、データを削除して、削除完了画面へ推移する


@ app.callback(Output('output', 'children'),
               Input('confirm-danger', 'submit_n_clicks'),
               State('user-name', 'value'))
def update_output(submit_n_clicks, user_name):
    if submit_n_clicks:
        # list_users から削除したい人の名前を削除
        list_users.remove(user_name)
        # 削除したい人以外のデータを抽出
        df_strengths_deleted = df_strengths[list_users]
        df_department_deleted = df_department[df_department['name'].isin(list_users)]

        # 削除したデータを GCS にアップロード
        df_strengths_deleted.to_csv(strengths_path, index=True)
        df_department_deleted.to_csv(department_path, index=False)

        # 削除完了のメッセージを表示するためのコンポーネントを返す
        deleted_message = "{} さんのデータを削除しました。".format(user_name)
        deleted_contents = dbc.Alert(
            [
                html.H5(deleted_message, className="alert-heading"),
            ], color='danger'
        )
        return deleted_contents
