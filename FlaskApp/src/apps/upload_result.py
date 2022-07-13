import json
import os

import yaml
from app import app
from dash import dcc, html
from dash.dependencies import Input, Output


# settings.yaml の読み込み
with open('settings.yaml') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# パスを設定
tmp_pdf_save_dir = '/tmp/'
# 入力データが正しかったかどうかのステータスをもつ json
input_state_path = os.path.join(tmp_pdf_save_dir, 'input_check_state.json')

contents = html.Div(
    [
        html.Div(id='uplode-result'),
        dcc.Store(id='intermediate-value')
    ]
)


layout = html.Div([contents])

# アップロードに成功した場合のメッセージ
contents_ok = html.Div(
    [
        html.H5('アップロードが完了しました',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('マッチング機能のみ、反映に5分程かかります。'),
        dcc.Store(id='intermediate-value')
    ]
)
# アップロードに失敗した場合のメッセージ
contents_user_name_is_empty = html.Div(
    [
        html.H5('アップロードに失敗しました',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('ユーザー名が入力されていることを確認してください。'),
        dcc.Store(id='intermediate-value')
    ]
)

contents_department_is_empty = html.Div(
    [
        html.H5('アップロードに失敗しました',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('所属部署が入力されていることを確認してください。'),
        dcc.Store(id='intermediate-value')
    ]
)


contents_strengths_is_incorrect = html.Div(
    [
        html.H5('アップロードに失敗しました',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('資質が34個入力されていることを確認してください。'),
        dcc.Store(id='intermediate-value')
    ]
)


contents_user_name_is_exists = html.Div(
    [
        html.H5('アップロードに失敗しました',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('すでに存在するユーザー名です'),
        dcc.Store(id='intermediate-value')
    ]
)

contents_ng = html.Div(
    [
        html.H5('アップロードに失敗しました',
                style=dict(padding="10px", borderLeft="5px #b31b1b solid")),
        html.P('お手数ですがアップロードページに戻り、もう一度やり直してください。'),
        dcc.Store(id='intermediate-value')
    ]
)


@app.callback(Output('uplode-result', 'children'),
              Input('intermediate-value', 'data'))
def update_result_message(_):
    try:
        with open(input_state_path) as f:
            input_state = json.load(f)
        # state ファイルを削除
        os.remove(input_state_path)

        # state によって表示する内容を分岐させる
        if input_state['user_name'] == False:
            return contents_user_name_is_empty
        elif input_state['department'] == False:
            return contents_department_is_empty
        elif input_state['strengths'] == False:
            return contents_strengths_is_incorrect
        elif input_state['exists_user'] == False:
            return contents_user_name_is_exists
        else:  # 全ての state が True だった場合
            return contents_ok
    except:
        # TODO：この分岐に入るのはどういうケースか洗い出す
        # ファイルが存在しない場合は state を False に設定する
        print('not found input state json file')
        return contents_ng
